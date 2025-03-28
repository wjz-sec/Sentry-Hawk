import time
import requests
import tldextract
from plugin.read_config import read_config
from app.models import Asset_info, Domain_info, Ip_info, Projects, Domain_ip, Asset_scan_input
from plugin.tools.auth import remove_duplicates_from_dict_list, remove_duplicates_from_list
import base64
import re


def fofa_query(query, fofa_email, fofa_key, blacklist_keywords):
    fofa_api_url = 'https://fofa.info/api/v1/search/all'
    b64_query = base64.b64encode(query.encode('utf-8'))
    params = {'email': fofa_email, 'key': fofa_key, 'qbase64': b64_query, 'size': 10000}
    response = requests.get(url=fofa_api_url, params=params)
    print(f"FOFA API 请求状态: {response.text}, 查询语句: {query}")
    if response.status_code == 200:
        results = response.json().get('results', [])
        return [res for res in results if not any(kw in res[0] for kw in blacklist_keywords)]
    return []  # 如果请求失败，返回空列表

# 用来去掉 http:// 和 https:// 的正则表达式
url_pattern = re.compile(r'https?://')

def clean_url(url):
    # 使用正则去掉 http:// 或 https://
    return re.sub(url_pattern, '', url)

def fofa(project_id):
    print("fofa-scan:--------------------------------")
    # 获取 IP 和 Domain 资产列表
    ip_list = Asset_scan_input.objects.filter(asset_project=project_id, asset_type='IP').values_list('asset', flat=True)
    domain_list = Asset_scan_input.objects.filter(asset_project=project_id, asset_type='Domain').values_list('asset', flat=True)
    
    print(f"项目ID: {project_id}")
    print(f"IP列表: {list(ip_list)}")
    print(f"域名列表: {list(domain_list)}")

    # 配置
    config = read_config()
    fofa_email = config['email']['FOFA_EMAIL']
    fofa_key = config['api']['FOFA_API_KEY']
    blacklist_keywords = config['blacklist_keywords']['blacklist_mail']
    project_instance = Projects.objects.get(id=project_id)
    
    # 首先将初始资产添加到Asset_info表
    for ip in ip_list:
        if ip and not Asset_info.objects.filter(asset=ip, asset_project_id=project_id).exists():
            Asset_info_instance = Asset_info.objects.create(
                asset=ip, asset_project=project_instance, asset_type='IP'
            )
            print(f"插入初始IP到Asset_info: {ip}")
            
            if Asset_info_instance:
                if not Domain_ip.objects.filter(domain=ip, target_id=Asset_info_instance.asset_id).exists():
                    Domain_ip.objects.create(
                        domain=ip,
                        target_id=Asset_info_instance.asset_id,
                        add_time=Asset_info_instance.asset_add_time,
                        editor_time=Asset_info_instance.asset_editor_time
                    )
                    print(f"插入初始IP到Domain_ip: {ip}")
    
    for domain in domain_list:
        if domain and not Asset_info.objects.filter(asset=domain, asset_project_id=project_id).exists():
            Asset_info_instance = Asset_info.objects.create(
                asset=domain, asset_project=project_instance, asset_type='Domain'
            )
            print(f"插入初始域名到Asset_info: {domain}")
            
            if Asset_info_instance:
                if not Domain_info.objects.filter(subdomain=domain, target_id=Asset_info_instance.asset_id).exists():
                    Domain_info.objects.create(
                        subdomain=domain,
                        target_id=Asset_info_instance.asset_id,
                        add_time=Asset_info_instance.asset_add_time,
                        editor_time=Asset_info_instance.asset_editor_time
                    )
                    print(f"插入初始域名到Domain_info: {domain}")
    
    # 结果存储
    asset_info_ip = []
    asset_info_domain = []
    domain_info_dict_list = []
    ip_info_dict_list = []
    
    # 查询域名相关数据
    for domain in domain_list:
        time.sleep(0.5)
        results = fofa_query(f'domain="{domain}"', fofa_email, fofa_key, blacklist_keywords)
        print(f"查询域名: {domain}, 返回结果数量: {len(results)}")
        for result in results:  # 假设每个 result 是一个列表，域名通常是第一个字段，IP 是第二个字段
            subdomain = result[0]  # 这是返回的子域名
            ip = result[1]  # 这是返回的 IP 地址
            subdomain = clean_url(subdomain)
            ip = clean_url(ip)
            if any(subdomain.startswith(prefix) for prefix in blacklist_keywords):
                print(f"跳过子域名（黑名单匹配）: {subdomain}")
                continue
            asset_info_ip.append(ip)
            asset_info_domain.append(subdomain)
            domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})
    
    # 查询 IP 相关数据
    for ip in ip_list:
        results = fofa_query(f'ip="{ip}"', fofa_email, fofa_key, blacklist_keywords)
        print(f"查询IP: {ip}, 返回结果数量: {len(results)}")
        for result in results:  # 假设每个 result 是一个列表，域名通常是第一个字段，IP 是第二个字段
            subdomain = result[0]  # 这是返回的子域名
            ip = result[1]  # 这是返回的 IP 地址
            subdomain = clean_url(subdomain)
            ip = clean_url(ip)
            if any(subdomain.startswith(prefix) for prefix in blacklist_keywords):
                print(f"跳过子域名（黑名单匹配）: {subdomain}")
                continue
            asset_info_ip.append(ip)
            asset_info_domain.append(subdomain)
            extracted = tldextract.extract(subdomain)
            domain = str(extracted.domain + '.' + extracted.suffix)
            domain_info_dict_list.append({'domain': domain, 'subdomain': subdomain, 'domain_to_ip': ip})
            ip_info_dict_list.append({'ip': ip, 'port': result[2] if len(result) > 2 else ''})  # 假设端口是第三个字段
    
    # 去重处理
    asset_info_ip = remove_duplicates_from_list(asset_info_ip)
    asset_info_domain = remove_duplicates_from_list(asset_info_domain)
    domain_info_dict_list = remove_duplicates_from_dict_list(domain_info_dict_list)
    ip_info_dict_list = remove_duplicates_from_dict_list(ip_info_dict_list)
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