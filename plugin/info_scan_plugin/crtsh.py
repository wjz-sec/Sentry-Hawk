#!/usr/bin/env python
import requests
import json
import socket
from app.models import Asset_info, Domain_info, Domain_ip  # 替换为你的应用名称

BASE_URL = "https://crt.sh/?q={}&output=json"


def get_domains_from_db(asset_project_id):
    return Asset_info.objects.filter(
        asset_project_id=asset_project_id,
        asset_type='Domain')


def crtsh(domain):
    subdomains = set()  # 每次调用时重置子域名集合
    try:
        response = requests.get(BASE_URL.format(domain), timeout=25)
        response.raise_for_status()  # 检查响应状态
        jsondata = response.json()  # 直接解析 JSON 数据
        for record in jsondata:
            name_value = record['name_value']
            subname_values = name_value.split(
                '\n') if '\n' in name_value else [name_value]
            for subname_value in subname_values:
                cleaned_subname = subname_value.strip().lstrip('*.')
                subdomains.add(cleaned_subname)
    except requests.exceptions.RequestException as e:
        print(f"请求 {domain} 时出错: {e}")
    return subdomains


def get_ips(domain):
    try:
        _, _, ip_addresses = socket.gethostbyname_ex(domain)
        return ip_addresses
    except socket.gaierror:
        print(f"无法解析 {domain}")
        return []


def insert_domain_info(domain, asset_id):
    try:
        domain_info = Domain_info(subdomain=domain, target_id=asset_id)
        domain_info.save()
        print(f"成功插入子域名: {domain} 到 Domain_info")
    except Exception as e:
        print(f"插入 Domain_info 时出错: {e}")


def insert_asset(asset_project_id, ip):
    try:
        # 检查资产是否已存在
        existing_asset = Asset_info.objects.filter(
            asset=ip,
            asset_project_id=asset_project_id,
            asset_type=Asset_info.IP
        ).first()
        
        if existing_asset:
            print(f"资产 {ip} 已存在，跳过插入")
            return existing_asset.asset_id
            
        # 资产不存在，执行插入操作
        asset = Asset_info(
            asset=ip,  # 将新的 IP 地址存入 asset 字段
            asset_project_id=asset_project_id,  # 关联到相应的 project_id
            asset_type=Asset_info.IP  # 设置资产类型为 IP
        )
        asset.save()
        print(f"成功插入资产 {ip}，类型为 IP")
        return asset.asset_id  # 返回新插入资产的 ID
    except Exception as e:
        print(f"插入 Asset_info 时出错: {e}")
        return None  # 返回 None 表示插入失败


def process_domains(asset_project_id):
    domain_assets = get_domains_from_db(asset_project_id)

    for asset in domain_assets:
        subdomains = crtsh(asset.asset)  # 获取子域名
        for subdomain in subdomains:
            ips = get_ips(subdomain)  # 获取 IP 地址
            for ip in ips:
                new_asset_id = insert_asset(
                    asset_project_id, ip)  # 插入 IP 并获取新的资产 ID
                if new_asset_id is not None:
                    # 将 subdomain 和新插入的 IP 的 asset_id 插入到 Domain_ip 表
                    try:
                        domain_ip_entry = Domain_ip(
                            domain=subdomain, target_id=new_asset_id)  # 使用新插入的 IP 的 asset_id
                        domain_ip_entry.save()
                        print(
                            f"成功插入 {subdomain} 的 IP 关联到 Domain_ip 表，asset_id: {new_asset_id}")
                    except Exception as e:
                        print(f"插入 Domain_ip 表时出错: {e}")
                insert_domain_info(subdomain, asset.asset_id)  # 插入子域名信息

    print(f"处理项目 ID {asset_project_id} 完成。")
