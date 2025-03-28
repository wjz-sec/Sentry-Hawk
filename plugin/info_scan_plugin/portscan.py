import re, os
import subprocess

from django.db.models import Q

from app.models import Asset_info, Ip_info

def get_ips_from_db(asset_project_id):
    ip_and_domain_assets = Asset_info.objects.filter(
    asset_project_id=asset_project_id
).filter(
    Q(asset_type='IP') | Q(asset_type='Domain')
)
    ip_addresses = [asset.asset for asset in ip_and_domain_assets]
    return ip_addresses, ip_and_domain_assets

def insert_scan_result(asset, port, status, service, version):
    ip_entry, created = Ip_info.objects.get_or_create(
        target_id=asset.asset_id,
        port=port,
        status=status,
        service=service,
        version=version,
    )
    if not created:
        ip_entry.status = status
        ip_entry.service = service
        ip_entry.version = version
        ip_entry.save()

    print(f"rustscan扫描{asset}结果保存完成")
def scan_port(ip_address, asset):
    rustscan_path = os.path.join(os.path.dirname(__file__), '../tools/rustscan/rustscan')
    command = [rustscan_path, '-a', ip_address, '-r', '1-65535','--','-sV']
    print(f"rustscan 开始扫描{ip_address}")
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    extracted_info = extract_info(result.stdout, ip_address)
    print(extracted_info)
    for ip, port, status, service, version in extracted_info:
        insert_scan_result(asset, port, status, service, version)

def extract_info(output, ip_address):
    # 正则表达式：匹配端口、状态、服务和版本信息
    pattern = r"(\d+/tcp)\s+(open|filtered)\s+(\S+)(?:\s+(?:\S+\s+\S+)\s+(.+))?"
    # 匹配所有符合条件的行
    relevant_lines = [line for line in output.split('\n') if re.match(r'\d+/tcp', line)]
    print(relevant_lines)
    # 解析匹配结果
    result = []
    for line in relevant_lines:
        match = re.search(pattern, line)
        if match:
            port, state, service, version = match.groups()
            if version:
                # 如果版本以数字开头，删除开头的数字
                version = re.sub(r"^\d+\s*", "", version)
            # 添加到结果列表
            result.append((ip_address, port, state, service, version))
    return result


def port_scan(asset_project_id):
    ip_list, assets = get_ips_from_db(asset_project_id)
    for ip, asset in zip(ip_list, assets):
        scan_port(ip, asset)

