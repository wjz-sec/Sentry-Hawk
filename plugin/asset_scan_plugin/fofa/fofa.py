import time
import requests
import tldextract
from plugin.read_config import read_config
from app.models import Asset_info, Domain_info, Projects, Domain_ip, Asset_scan_input
from plugin.tools.auth import remove_duplicates_from_list
from plugin.asset_scan_plugin.fofa.fofa_sign import get_url
from plugin.asset_scan_plugin.utils import clean_url, is_ipv4

def fofa_query(query, fofa_token, blacklist_keywords, size=20, pg=1):
    fofa_api_url = get_url(query, pg, size)
    try:
        response = requests.get(url=fofa_api_url, headers={
            "authorization": fofa_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
        })
        response.raise_for_status()
        print(f"FOFA API 请求状态: {response.status_code}, 查询语句: {query}")
        if response.status_code != 200:
            print(f"[fofa] 请求失败，状态码：{response.status_code}，返回内容：{response.text}")
            return []
        if response.json().get("code", -1) != 0:
            print(f"[fofa] 请求失败，状态码：{response.status_code}，返回内容：{response.text}")
            return []
        
        page = response.json().get("data", {}).get("page", {})
        num = page.get("num", -1)
        total = page.get("total", -1)
        print(f"[fofa] 采集第{pg}页，一共{total}个")
        rs = response.json().get("data", {}).get('assets', [])
        results = [res for res in rs if not any(kw in res['id'] for kw in blacklist_keywords)]
        if  total == -1:
            return results
        if num * size >= total:
            return results
        npg = pg + 1
        time.sleep(2)
        fr = fofa_query(query, fofa_token, blacklist_keywords, size, npg)
        results.extend(fr)
        return results
    except Exception as e:
        print("fofa请求失败", pg, response.text, e)
        return []


def fofa(project_id):
    print("fofa-scan:--------------------------------")
    # 获取资产列表
    print(f"项目ID: {project_id}")
    assest_list = Asset_scan_input.objects.filter(asset_project=project_id)
    
    # 配置
    config = read_config()
    fofa_token = config['api']['FOFA_USER_TOKEN']
    blacklist_keywords = config['blacklist_keywords']['blacklist_mail']
    project_instance = Projects.objects.get(id=project_id)
    
    # 结果存储
    asset_info_ip = []
    asset_info_domain = []

    # domain_info_dict_list = []
    # ip_info_dict_list = []
    
    # 先保存原始URL资产
    for assest in assest_list:
        if assest.asset_type == "URL" and not Asset_info.objects.filter(asset=assest.asset, asset_project_id=project_id).exists():
            # 保存原始URL到Asset_info
            Asset_info_instance = Asset_info.objects.create(
                asset=assest.asset,
                asset_project=project_instance,
                asset_type='URL'
            )
            if Asset_info_instance:
                print(f"插入URL到Asset_info: {assest.asset}")
                # 根据URL是否为IP地址决定创建Domain_ip还是Domain_info
                if is_ipv4(clean_url(assest.asset)):
                    if not Domain_ip.objects.filter(domain=assest.asset, target_id=Asset_info_instance.asset_id).exists():
                        Domain_ip.objects.create(
                            domain=assest.asset,
                            target_id=Asset_info_instance.asset_id,
                            add_time=Asset_info_instance.asset_add_time,
                            editor_time=Asset_info_instance.asset_editor_time
                        )
                else:
                    if not Domain_info.objects.filter(subdomain=assest.asset, target_id=Asset_info_instance.asset_id).exists():
                        Domain_info.objects.create(
                            subdomain=assest.asset,
                            target_id=Asset_info_instance.asset_id,
                            add_time=Asset_info_instance.asset_add_time,
                            editor_time=Asset_info_instance.asset_editor_time
                        )
    
    # 查询域名相关数据
    for assest in assest_list:
        if assest.asset_type == "URL":
            assest.asset_type = "Domain"
            assest.asset = clean_url(assest.asset)
            if is_ipv4(assest.asset):
                assest.asset_type = "IP"
        
        if assest.asset_type == "Domain":
            domain = assest.asset
            time.sleep(0.5)
            results = fofa_query(f'domain="{domain}"', fofa_token, blacklist_keywords)
            # print("results", results)
            print(f"查询域名: {domain}, 返回结果数量: {len(results)}")
            for result in results:  # 假设每个 result 是一个列表，域名通常是第一个字段，IP 是第二个字段
                subdomain = result['id']  # 这是返回的子域名
                ip = result['ip']  # 这是返回的 IP 地址
                subdomain = clean_url(subdomain)
                ip = clean_url(ip)

                if any(subdomain.startswith(prefix) for prefix in blacklist_keywords):
                    print(f"跳过子域名（黑名单匹配）: {subdomain}")
                    continue
                asset_info_ip.append(ip)
                asset_info_domain.append(subdomain)
                # domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})

        if assest.asset_type == "IP":
            ip = assest.asset
            results = fofa_query(f'ip="{ip}"', fofa_token, blacklist_keywords)
            print(f"查询IP: {ip}, 返回结果数量: {len(results)}")
            for result in results:  # 假设每个 result 是一个列表，域名通常是第一个字段，IP 是第二个字段
                subdomain = result['id']  # 这是返回的子域名
                ip = result['ip']  # 这是返回的 IP 地址
                subdomain = clean_url(subdomain)
                ip = clean_url(ip)
                if any(subdomain.startswith(prefix) for prefix in blacklist_keywords):
                    print(f"跳过子域名（黑名单匹配）: {subdomain}")
                    continue
                asset_info_ip.append(ip)
                asset_info_domain.append(subdomain)
                extracted = tldextract.extract(subdomain)
                domain = str(extracted.domain + '.' + extracted.suffix)
                # domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})
                # ip_info_dict_list.append({'ip': ip, 'port': result.get('port', '')})  # 假设端口是第三个字段
                # ip_info_dict_list.append({'ip': ip, 'port': result[2] if len(result) > 2 else ''})  # 假设端口是第三个字段
    
    # 去重处理
    asset_info_ip = remove_duplicates_from_list(asset_info_ip)
    asset_info_domain = remove_duplicates_from_list(asset_info_domain)
    # domain_info_dict_list = remove_duplicates_from_dict_list(domain_info_dict_list)
    # ip_info_dict_list = remove_duplicates_from_dict_list(ip_info_dict_list)
    print(f"去重后IP: {asset_info_ip}")
    print(f"去重后子域名: {asset_info_domain}")

    # 第一步：将数据插入到 Asset_info 表
    project_instance = Projects.objects.filter(id=project_id).first()
    
    # 插入 IP 数据
    for ip in asset_info_ip:
        if ip and not Asset_info.objects.filter(asset=ip, asset_project_id=project_id).exists():
            # 插入数据到 Asset_info 表
            Asset_info_instance = Asset_info.objects.create(
                asset=ip, asset_project=project_instance, asset_type='IP'
            )
            print(f"插入IP到Asset_info: {ip}")
            
            # 检查插入成功后的 Asset_info_instance
            if Asset_info_instance:
                print(f"Asset_info 数据插入成功，ID: {Asset_info_instance.asset_id}")
            
                # 插入数据到 Domain_ip 表
                if not Domain_ip.objects.filter(domain=ip, target_id=Asset_info_instance.asset_id).exists():
                    Domain_ip.objects.create(
                        domain=ip,
                        target_id=Asset_info_instance.asset_id,  # 使用 Asset_scan_input 的 asset_id
                        add_time=Asset_info_instance.asset_add_time,
                        editor_time=Asset_info_instance.asset_editor_time
                    )
                    print(f"插入IP到Domain_ip: {ip}")
                else:
                    print(f"Domain_ip 数据已存在，跳过插入: {ip}")
            else:
                print(f"未能成功插入 IP 到 Asset_scan_input: {ip}")

    # 插入 Domain 数据
    for domain in asset_info_domain:
        if domain and not Asset_info.objects.filter(asset=domain, asset_project_id=project_id).exists():
            # 插入数据到 Asset_scan_input 表
            Asset_info_instance = Asset_info.objects.create(
                asset=domain, asset_project=project_instance, asset_type='Domain'
            )
            print(f"插入域名到Asset_info: {domain}")
            
            # 检查插入成功后的 Asset_info_instance
            if Asset_info_instance:
                print(f"Asset_info 数据插入成功，ID: {Asset_info_instance.asset_id}")
                
                # 插入数据到 Domain_info 表
                if not Domain_info.objects.filter(subdomain=domain, target_id=Asset_info_instance.asset_id).exists():
                    Domain_info.objects.create(
                        subdomain=domain,
                        target_id=Asset_info_instance.asset_id,  # 使用 Asset_scan_input 的 asset_id
                        add_time=Asset_info_instance.asset_add_time,
                        editor_time=Asset_info_instance.asset_editor_time
                    )
                    print(f"插入域名到Domain_info: {domain}")
                else:
                    print(f"Domain_info 数据已存在，跳过插入: {domain}")