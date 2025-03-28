import re,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from app.models import Vuln_info, Asset_info

nuclei_path = os.path.join(os.path.dirname(__file__), '../tools/nuclei/')  # 计算nuclei.exe的目录
temp = os.path.join(os.path.dirname(__file__), '../tools/nuclei_templates')

#temp = 'D:\code\python\Sentry-Hawk\Sentry-Hawk\plugin\\tools\\nuclei\\1.yaml'
#测试目标 = http://106.15.56.37:8008, http://oa.e-melody.cn:8008

def run_nuclei(target):
    print(f"nuclei开始扫描:{target}")
    command = [
        'nuclei',
        '-u', target,
        '-t', temp,
    ]
    str = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=nuclei_path)
    output = str.stdout.decode('utf-8')
    result = handle_result(output)
    return result

def nuclei_scan(targets,project_id):
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_nuclei, target): target for target in targets}
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
                        'vuln_name': item[0],
                        'protocol': item[1],
                        'severity': item[2],
                        'url': item[3]
                    }
                    extracted_results.append(extracted_parts)


            print("开始将nuclei_result写入数据库")
            asset_info_instance = Asset_info.objects.filter(asset=target,
                                                            asset_project=project_id).first()  # 获取对应的 Asset_info 实例
            if asset_info_instance:  # 确保实例存在
                for extracted_result in extracted_results:
                    existing_results = Vuln_info.objects.filter(target=asset_info_instance.asset_id,vuln_name=extracted_result['vuln_name'])
                    if existing_results.exists():
                            # 更新所有现有结果
                            existing_results.update(vuln_name=extracted_result['vuln_name'],
                                                    vuln_level=extracted_result['severity'],
                                                    vuln_url=extracted_result['url'])  # 直接更新
                    else:
                            # 创建新记录
                            Vuln_info.objects.create(
                                target=asset_info_instance,  # 使用项目实例
                                vuln_name=extracted_result['vuln_name'],
                                vuln_level=extracted_result['severity'],
                                vuln_url=extracted_result['url'],
                                project_id=project_id,
                                vuln_from='nuclei'
                            )
            print(f'nuclei扫描{target}完成')
    return results


def handle_result(result):
    pattern = r'\[(?:\x1b\[.*?m)?(.+?)\x1b\[0m\] \[(?:\x1b\[.*?m)?(.+?)\x1b\[0m\] \[(?:\x1b\[.*?m)?(.+?)\x1b\[0m\] (http[^\n]+)'
    results = []
    matches = re.findall(pattern, result)

    for match in matches:
        if match:
            # 提取出各个部分并存储在一个列表中
            extracted_parts = [
                match[0],
                match[1],
                match[2],
                match[3]
            ]
            results.append(extracted_parts)
        else:
            print("没有匹配项")

    #打印提取出的结果
    print("nuclei扫描结果:", results)

    return results

