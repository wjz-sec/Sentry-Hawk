import time
import requests
from plugin.read_config import read_config
from app.models import Asset_info, Domain_info, Projects, Domain_ip, Asset_scan_input
from plugin.tools.auth import remove_duplicates_from_list
from plugin.asset_scan_plugin.utils import clean_url, is_ipv4


def quake(project_id):
    print("quake-scan:--------------------------------")
    # 获取资产列表
    print(f"项目ID: {project_id}")
    assest_list = Asset_scan_input.objects.filter(asset_project=project_id)
    
    # 结果存储
    asset_info_ip = []
    asset_info_domain = []
    # domain_info_dict_list = []
    # ip_info_dict_list = []
    
    # 配置
    config = read_config()
    blacklist_prefixes = config['blacklist_keywords']['blacklist_mail']
    project_instance = Projects.objects.get(id=project_id)
    
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
    
    # 获取 IP 和 Domain 资产列表
    ip_list = Asset_scan_input.objects.filter(asset_project=project_id, asset_type='IP').values_list('asset', flat=True)
    domain_list = Asset_scan_input.objects.filter(asset_project=project_id, asset_type='Domain').values_list('asset', flat=True)
    
    print(f"IP列表: {list(ip_list)}")
    print(f"域名列表: {list(domain_list)}")

    
    # 读取配置
    config = read_config()
    blacklist_prefixes = config['blacklist_keywords']['blacklist_mail']
    quake_api_key = config['api']['QUAKE_API_KEY']
    quake_api_url = 'https://quake.360.net/api/v3/search/quake_service' 
    headers = {"X-QuakeToken": quake_api_key, "Content-Type": "application/json"}
    data = {"query": '', "start": 0, "size": 10000}

    
    # 查询域名相关数据
    for domain in domain_list:
        time.sleep(0.5)
        data['query'] = f'domain:"{domain}"'
        response = requests.post(url=quake_api_url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get('data', [])
            print(f"查询域名: {domain}, 返回结果数量: {len(results)}")
            for result in results:
                subdomain = result.get('domain', '')
                ip = result.get('ip', '')
                ip = clean_url(ip)
                subdomain = clean_url(subdomain)
                if any(subdomain.startswith(prefix) for prefix in blacklist_prefixes):
                    print(f"跳过子域名（黑名单匹配）: {subdomain}")
                    continue
                asset_info_ip.append(ip)
                asset_info_domain.append(subdomain)
                # domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})
    
    # 查询 IP 相关数据
    for ip in ip_list:
        data['query'] = f'ip:"{ip}"'
        response = requests.post(url=quake_api_url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get('data', [])
            print(f"查询IP: {ip}, 返回结果数量: {len(results)}")
            for result in results:
                subdomain = result.get('domain', '')
                ip = result.get('ip', '')
                if any(subdomain.startswith(prefix) for prefix in blacklist_prefixes):
                    print(f"跳过子域名（黑名单匹配）: {subdomain}")
                    continue
                ip = clean_url(ip)
                subdomain = clean_url(subdomain)
                asset_info_ip.append(ip)
                asset_info_domain.append(subdomain)
                # extracted = tldextract.extract(subdomain)
                # domain = str(extracted.domain + '.' + extracted.suffix)
                # domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})
                # ip_info_dict_list.append({'ip': ip, 'port': result.get('port', '')})
    
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

