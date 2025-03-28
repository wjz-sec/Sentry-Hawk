import subprocess
import os
import csv
from app.models import Asset_info, Domain_info, Domain_ip, OneforallResult

# OneForAll 的路径
oneforall_path = os.path.join(
    os.path.dirname(__file__),
    '../tools/OneForAll-master/oneforall.py')

def get_target_domains(project_id):
    """从数据库中获取目标域名列表，仅包括 asset_type 为 domain 的资产"""
    target_domains = Asset_info.objects.filter(
        asset_type__in=['Domain'],
        asset_project_id=project_id).values_list(
            'asset',
            'asset_id')
    print(f"Target domains for project {project_id}: {target_domains}")
    return target_domains

def get_top_domain(domain):
    """获取顶级域名"""
    # 移除末尾的斜杠
    domain = domain.rstrip('/')
    # 分割域名部分
    parts = domain.split('.')
    # 如果域名部分少于2个，直接返回原域名
    if len(parts) < 2:
        return domain
    # 获取最后三个部分（如果存在）作为顶级域名
    if len(parts) >= 3 and parts[-2] in ['cn', 'com', 'org', 'net', 'edu', 'gov']:
        return '.'.join(parts[-3:])
    # 否则返回最后两个部分
    return '.'.join(parts[-2:])

def parse_csv_result(csv_file, target_domain, asset_id):
    """解析CSV文件并保存结果到数据库"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
    
    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    subdomain = row.get('url', '')
                    ip = row.get('ip', '')
                    status = row.get('status', '')
                    title = row.get('title', '')
                    addr = row.get('addr', '')
                    
                    # 保存到OneforallResult表
                    try:
                        oneforall_result = OneforallResult(
                            target_id=asset_id,
                            url=subdomain,
                            ip=ip,
                            status=status,
                            title=title,
                            addr=addr
                        )
                        oneforall_result.save()
                        print(f"成功保存到OneforallResult: {subdomain}")
                    except Exception as e:
                        print(f"保存到OneforallResult失败: {e}")
                return  # 如果成功解析，直接返回
        except UnicodeDecodeError:
            continue  # 如果当前编码失败，尝试下一个编码
        except Exception as e:
            print(f"解析CSV文件失败: {e}")
            continue
    
    print(f"尝试了所有编码方式后仍无法解析CSV文件: {csv_file}")

def scan_domain(domain, asset_id):
    """对单个域名执行OneForAll扫描"""
    work_dir = os.path.dirname(oneforall_path)
    # 获取顶级域名
    top_domain = get_top_domain(domain)
    csv_file = os.path.join(work_dir, 'results', f"{top_domain}.csv")
    
    try:
        # 移除域名末尾的斜杠
        domain = domain.rstrip('/')
        command = ['python', oneforall_path, '--target', domain, 'run']
        print(f"执行命令: {' '.join(command)}")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=work_dir
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"扫描失败: {stderr}")
            return
            
        print(f"扫描完成，开始解析结果: {domain}")
        
        # 检查CSV文件是否存在
        if os.path.exists(csv_file):
            parse_csv_result(csv_file, domain, asset_id)
        else:
            print(f"未找到结果文件: {csv_file}")
            
    except Exception as e:
        print(f"扫描过程中发生错误: {e}")

def find_sdomain(project_id):
    """主函数，接收project_id并执行扫描"""
    target_domains = get_target_domains(project_id)
    if not target_domains:
        print(f"No target domains found for project {project_id}")
        return

    for domain, asset_id in target_domains:
        print(f"Scanning domain: {domain}")
        scan_domain(domain, asset_id)