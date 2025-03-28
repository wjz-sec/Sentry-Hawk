import re
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
from app.models import Wih_result, Asset_info


wih_path = os.path.join(os.path.dirname(__file__), '../tools/wih/')  # 计算 wih 工具的目录

def run_wih(target):
    """
    调用 WIH 工具扫描指定目标
    """
    print(f"WIH 开始扫描: {target}")
    command = [
        'wih_linux_amd64',  # WIH 工具名称
        '-t', target,  # 目标
    ]
    # 执行命令并捕获输出
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=wih_path)
    output = result.stdout.decode('utf-8')
    print(output)
    parsed_results = handle_result(output)
    return parsed_results

def handle_result(result):
    """
    解析 WIH 工具的输出结果
    假设 WIH 的输出格式为表格，提取其中的 ID 和 CONTENT 列
    """
    # 正则表达式匹配表格中的 ID 和 CONTENT
    pattern = r'\| +\d+ +\| (\w+) +\| ([^|\n]+)'
    results = []
    matches = re.findall(pattern, result)
    if matches:
        for match in matches:
            extracted_parts = [
                match[0].strip(),  # ID
                match[1].strip()   # CONTENT
            ]
            results.append(extracted_parts)
    else:
        print("没有匹配项")
        results.append(None)
    print("WIH 扫描结果:", results)
    return results

def wih_scan(project_id):
    targets = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    """
    使用线程池并发扫描多个目标，并将结果保存到数据库
    """
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_wih, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result = future.result()
            results[target] = result

            extracted_results = []
            for item in result:
                if item:
                    extracted_parts = {
                        'type': item[0],  # 漏洞类型
                        'content': item[1],   # 严重性
                    }
                    extracted_results.append(extracted_parts)

            print(extracted_results)

            print("开始将 WIH 结果写入数据库")
            asset_info_instance = Asset_info.objects.filter(asset=target, asset_project=project_id).first()
            if asset_info_instance:
                for extracted_result in extracted_results:
                    #
                    existing_results = Wih_result.objects.filter(target=asset_info_instance.asset_id, content=extracted_result['content'])
                    if existing_results.exists():
                        # 更新现有记录
                        existing_results.update(
                            type=extracted_result['type'],
                            content=extracted_result['content'],
                        )
                    else:
                        # 创建新记录
                        Wih_result.objects.create(
                            target=asset_info_instance,
                            type=extracted_result['type'],
                            content=extracted_result['content']
                        )
    print("WIH扫描结果写入完成")
    return results
