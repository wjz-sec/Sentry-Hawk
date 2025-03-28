import re,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from app.models import Asset_info, Vuln_info
from django.db import close_old_connections

xray_path = os.path.join(os.path.dirname(__file__), '../tools/xray/')

def handle_result(output):
    # 定义正则表达式
    pattern = r'\[(Vuln: .*?)\](.*?)\n\n'
    # 查找所有匹配项
    matches = re.findall(pattern, output, re.DOTALL)
    # 初始化一个列表以收集结果
    results = []
    # 遍历匹配项并提取所有信息
    for match in matches:
        vuln = match[0]
        lines = match[1].strip().split('\n')
        vuln_info = {}
        # results.append(f"[{vuln}]")
        for line in lines:
            # 使用空格分隔行，提取字段名和值
            parts = line.split('"')
            if len(parts) > 1:
                key = parts[0].strip()  # 获取字段名
                value = parts[1]  # 获取字段值
                vuln_info[key] = value  # 存储到字典中

        level = vuln_info.get('level')
        if level is not None:
            extracted_parts = [
                vuln_info['Target'],
                vuln_info['VulnType'],
                vuln_info['level'],
            ]
        else:
            extracted_parts = [
                vuln_info['Target'],
                vuln_info['VulnType'],
                'low',
            ]

        results.append(extracted_parts)

    print(results)
    return results


def start_scan(target):
    print(f"xray开始扫描:{target}")
    str = subprocess.run(
        f'xray ws -u {target}',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=xray_path
    )
    output = str.stdout.decode('utf-8')
    result = handle_result(output)
    return result



def xray_scan(targets,project_id):
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(start_scan, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result = future.result()
            results[target] = result

            # 初始化一个列表来存储提取的结果
            extracted_results = []

            # 处理匹配项
            for item in result:
                if item:
                    # 提取出各个部分并存储在一个字典中
                    extracted_parts = {
                        'url': item[0],
                        'vuln_name': item[1],
                        'severity': item[2]
                    }
                    extracted_results.append(extracted_parts)

            asset_info_instance = Asset_info.objects.filter(asset=target,
                                                            asset_project=project_id).first()  # 获取对应的 Asset_info 实例
            if asset_info_instance:  # 确保实例存在

                for extracted_result in extracted_results:
                    existing_results = Vuln_info.objects.filter(target=asset_info_instance.asset_id,vuln_name=extracted_result['vuln_name'])
                    if existing_results.exists():
                            # 更新所有现有结果
                            existing_results.update(vuln_name=extracted_result['vuln_name'],
                                                    vuln_level=extracted_result['severity'],
                                                    vuln_url=extracted_result['url'])
                    else:
                            # 创建新记录
                            Vuln_info.objects.create(
                                target=asset_info_instance,
                                vuln_name=extracted_result['vuln_name'],
                                vuln_level=extracted_result['severity'],
                                vuln_url=extracted_result['url'],
                                project_id=project_id,
                                vuln_from='xray',
                            )
            print(f"xray扫描{target}完成，")
    return results



