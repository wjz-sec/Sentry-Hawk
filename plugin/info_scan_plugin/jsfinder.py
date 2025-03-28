import re
import subprocess
import os, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from app.models import Sensitive_dir,Sensitive_info, Asset_info


dirsearch_path = os.path.join(os.path.dirname(__file__), '../tools/jsfinder')  # 计算 wih 工具的目录

def run_jsfinder(target):

    print(f"jsfinder开始扫描: {target}")

    # 判断target是否以http或https开头，如果不是，则添加http或https进行测试
    if not target.startswith(('http://', 'https://')):
        for protocol in ['http://', 'https://']:
            test_target = f"{protocol}{target}"
            try:
                # 尝试连接目标，检查是否存活
                result = subprocess.run(['curl', '-I', test_target], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        timeout=5)
                if result.returncode == 0:
                    target = test_target
                    print(f"使用协议: {protocol}")
                    break
            except subprocess.TimeoutExpired:
                print(f"连接超时: {test_target}")
            except Exception as e:
                print(f"连接失败: {test_target}, 错误: {e}")
    else:
        print(f"目标已包含协议: {target}")

    command = [
        'python','JSFinder.py',
        '-u', target
    ]
    # 执行命令并捕获输出
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dirsearch_path)
    output = result.stdout.decode('utf-8')
    return output

def extract_urls(result):
    """
    从输入文本中提取 URL 和域名
    参数:
        result (str): 输入的文本内容
    返回:
        tuple: (unique_urls, unique_domains)
            unique_urls: 去重后的 URL 列表
            unique_domains: 去重后的域名列表
    """
    # 匹配完整的 URL（包括路径）
    url_pattern = r'https?://[^\s/]+(?:/[^\s]*)*'
    # 匹配域名（包括子域名），排除路径部分
    domain_pattern = r'(https?:\/\/)?([a-zA-Z0-9][a-zA-Z0-9-]{0,62}(?:\.[a-zA-Z0-9][a-zA-Z0-9-]{0,62})+)(?:\/[^\s]*)?'
    # 匹配 URL
    url_matches = re.findall(url_pattern, result)
    # 匹配域名
    domain_matches = re.findall(domain_pattern, result)
    # 提取域名部分
    domains = [match[1] for match in domain_matches]
    # 去重
    unique_urls = list(set(url_matches))
    unique_domains = list(set(domains))

    # 返回结果
    return unique_urls, unique_domains


def jsfinder_scan(project_id):
    targets = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    results = {}
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_jsfinder, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result = future.result()
            results[target] = result
            # 提取 URL 和域名
            urls, domains = extract_urls(result)
            # 获取 Asset_info 实例
            asset_info_instance = Asset_info.objects.filter(asset=target, asset_project=project_id).first()
            if asset_info_instance:
                # 处理提取的 URL
                for url in urls:
                    title, status_code = get_page_info(url)
                    if url.endswith('.js'):
                        # 检查是否存在，如果不存在则插入
                        if not Sensitive_info.objects.filter(target_id=asset_info_instance, js_info=url).exists():
                            Sensitive_info.objects.create(
                                target_id=asset_info_instance.asset_id,
                                project_id=project_id,
                                js_info=url,
                            )
                    else:
                        # 使用 update_or_create 处理 Sensitive_dir 记录
                        Sensitive_dir.objects.update_or_create(
                            target_id=asset_info_instance.asset_id,
                            project_id=project_id,
                            url=url,
                            defaults={
                                'title': title,
                                'status': status_code
                            }
                        )
                # 处理提取的域名
                for domain in domains:
                    # 检查是否存在，如果不存在则插入
                    if not Sensitive_info.objects.filter(target_id=asset_info_instance, other=domain).exists():
                        Sensitive_info.objects.create(
                            target_id=asset_info_instance.asset_id,
                            project_id=project_id,
                            other=domain,
                        )
    print(f"jsfinder 扫描结果写入完成")
    return results


def get_page_info(url):
    """
    获取 URL 页面的标题和响应码
    """
    try:
        # 发送 HTTP 请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        # 解析页面标题
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No Title"
        return title, response.status_code
    except Exception as e:
        print(f"Failed to get page info for {url}: {e}")
        return "No Title", None