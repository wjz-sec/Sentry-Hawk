import subprocess
import re
import os
import time
from app.models import Asset_info, Domain_info, Domain_ip  # 请根据你的应用名称进行修改

dnsub_path = os.path.join(
    os.path.dirname(__file__),
    '../tools/subdomain/dnsub/dnsub')
cwd_path = os.path.join(os.path.dirname(__file__), '../tools/subdomain/dnsub')


# 获取指定 project_id 的域名资产
def get_domain_assets(project_id):
    return Asset_info.objects.filter(
        asset_project_id=project_id,
        asset_type='Domain')


# 插入子域名到 Domain_info 表
def insert_domain_info(domain, asset_id):
    try:
        domain_info = Domain_info(subdomain=domain, target_id=asset_id)
        domain_info.save()
        print(f"成功插入子域名: {domain} 到 Domain_info")
    except Exception as e:
        print(f"插入错误: {e}")


# 插入新的 IP 到 Asset_info 表
def insert_asset(asset_project_id, ip):
    try:
        asset = Asset_info(
            asset=ip,  # 将新的 IP 地址存入 asset 字段
            asset_project_id=asset_project_id,  # 关联到相应的 project_id
            asset_type=Asset_info.IP  # 设置资产类型为 IP
        )
        asset.save()
        print(f"成功插入资产 {ip}，类型为 IP")
        return asset.asset_id  # 返回新插入资产的 ID
    except Exception as e:
        print(f"插入错误: {e}")
        return None  # 返回 None 表示插入失败


# 子域名爆破函数
def subdomain_bruteforce(domain, asset_id, asset_project_id):  # 添加 asset_project_id 参数
    try:
        process = subprocess.Popen(
            [dnsub_path, '-d', domain],  # 直接使用完整的域名
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=cwd_path
        )

        start_time = time.time()  # 记录开始时间

        # 逐行读取输出
        while True:
            line = process.stdout.readline()  # 逐行读取输出
            if not line:  # 如果没有输出，退出循环
                break

            # 使用正则表达式提取域名和IP
            pattern = r'(\S+)\s+(\d+\.\d+\.\d+\.\d+)'  # 匹配格式: 域名    IP地址
            matches = re.findall(pattern, line)

            for match in matches:
                subdomain, ip_address = match
                print(f"提取到子域名: {subdomain}, IP: {ip_address}")  # 调试输出
                insert_domain_info(subdomain, asset_id)  # 插入到 Domain_info 表

                # 插入新的 IP，并获取其 asset_id
                new_asset_id = insert_asset(
                    asset_project_id, ip_address)  # 传入 project_id
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

            # 检查是否超过1分钟
            if time.time() - start_time >= 60:
                print(f"1分钟已到，停止子域名爆破: {domain}")
                process.terminate()  # 终止子进程
                break

        return_code = process.wait()
        if return_code != 0:
            print(f"错误: {process.stderr.read()}")

    except Exception as e:
        print(f"发生错误: {e}")


# 主函数：接收 project_id，获取域名资产并进行子域名爆破
def process_domains(project_id):
    domain_assets = get_domain_assets(project_id)
    for asset in domain_assets:
        subdomain_bruteforce(
            asset.asset,
            asset.asset_id,
            asset.asset_project_id)
