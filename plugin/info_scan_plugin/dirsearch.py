import re
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from pygments.lexer import default

from app.models import Sensitive_dir, Asset_info


dirsearch_path = os.path.join(os.path.dirname(__file__), '../tools/dirsearch/')  # 计算 wih 工具的目录

def run_dirsearch(target):
    """
    调用 WIH 工具扫描指定目标
    """
    print(f"dirsearch开始扫描: {target}")
    default_result = ['no dirsearch']
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
                return default_result,test_target
            except Exception as e:
                print(f"连接失败: {test_target}, 错误: {e}")
    else:
        print(f"目标已包含协议: {target}")

    command = [
        'python','dirsearch.py',
        '-u', target,'-i 200,403,401,302'
    ]
    # 执行命令并捕获输出
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dirsearch_path)
    output = result.stdout.decode('utf-8')
    parsed_results = handle_result(output)
    return parsed_results,target

def handle_result(result):
    # 正则表达式匹配每行中的状态码和路径
    pattern = r'\[\d{2}:\d{2}:\d{2}\] (\d{3}) - \s*\d+\w{1,2} \s*- (.*)$'
    results = []
    matches = re.findall(pattern, result, re.MULTILINE)
    if matches:
        for match in matches:
            extracted_parts = [
                match[0].strip(),  # 状态码
                match[1].strip()   # 路径
            ]
            results.append(extracted_parts)
    else:
        print("没有匹配项")
        results.append("no dirsearch")
    print("dirsearch 扫描结果:", results)
    return results


def dirsearch_scan(project_id):
    targets = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    """
    使用线程池并发扫描多个目标，并将结果保存到数据库
    """
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_dirsearch, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result,handle_url = future.result()
            results[target] = result

            extracted_results = []
            default_results = ['no dirsearch']
            if result == default_results:
                extracted_parts = {
                    'status': 500,
                    'url': handle_url,
                }
                extracted_results.append(extracted_parts)
            else:
                for item in result:
                    extracted_parts = {
                        'status': item[0],
                        'url': item[1],
                    }
                    extracted_results.append(extracted_parts)

            print("开始将 dirsearch结果写入数据库")
            asset_info_instance = Asset_info.objects.filter(asset=target, asset_project=project_id).first()
            if asset_info_instance:
                for extracted_result in extracted_results:
                    if extracted_result['status'] == 500:
                        full_url = extracted_result['url']
                        page_title = 'no title'
                    else:
                        # 拼接 URL
                        full_url = handle_url.rstrip('/') + extracted_result['url']
                        # 获取网页标题
                        page_title = get_page_title(full_url)
                    existing_results = Sensitive_dir.objects.filter(target=asset_info_instance.asset_id, url=extracted_result['url'])
                    if existing_results.exists():
                        # 更新现有记录
                        existing_results.update(
                            status=extracted_result['status'],
                            url=full_url,
                            title=page_title,
                        )
                    else:
                        # 创建新记录
                        Sensitive_dir.objects.create(
                            target=asset_info_instance,
                            status=extracted_result['status'],
                            url=full_url,
                            title=page_title,
                            project_id=project_id
                        )
            print(f"{target}dirsearch扫描结果写入完成")
    return results


def get_page_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else None
        return title
    except requests.RequestException:
        return 'no title'