import subprocess,re,os
from concurrent.futures import ThreadPoolExecutor

from app.models import Asset_info, Vuln_info
from django.db import close_old_connections

#测试目标 http://testphp.vulnweb.com

afrog_path = os.path.join(os.path.dirname(__file__), '../tools/afrog')
def run_afrog(target):

    print(f"afrog开始扫描:{target}")
    str = subprocess.run(f'afrog -target {target}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=afrog_path)
    output = str.stdout.decode('utf-8')
    result = handle_result(output)
    return result

def afrog_scan(target_list,project_id):
    results = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(run_afrog, target): target for target in target_list}
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
                        'severity': item[1],
                        'url': item[2]
                    }
                    extracted_results.append(extracted_parts)

            close_old_connections()
            asset_info_instance = Asset_info.objects.filter(asset=target,
                                                            asset_project=project_id).first()  # 获取对应的 Asset_info 实例
            if asset_info_instance:  # 确保实例存在
                print(f"{target}扫描完成将afrog_result写入数据库")
                for extracted_result in extracted_results:
                    existing_results = Vuln_info.objects.filter(target=asset_info_instance.asset_id,vuln_name=extracted_result['vuln_name'])
                    if existing_results.exists():
                            # 更新所有现有结果
                            existing_results.update(vuln_name=extracted_result['vuln_name'],
                                                    vuln_level=extracted_result['severity'].lower(),
                                                    vuln_url=extracted_result['url'])
                    else:
                            # 创建新记录
                            Vuln_info.objects.create(
                                target=asset_info_instance,  # 使用项目实例
                                vuln_name=extracted_result['vuln_name'],
                                vuln_url=extracted_result['url'],
                                vuln_level=extracted_result['severity'].lower(),
                                project_id=project_id,
                                vuln_from='afrog'
                            )
            print(f'afrog扫描{target}完成')
    return results

def handle_result(result):
    # 定义正则表达式
    pattern = r'\x1b\[92m(.*?)\x1b\[0m \x1b\[91m(\w+)\x1b\[0m (http://\S+)'

    # 查找所有匹配项
    matches = re.findall(pattern, result)

    # 初始化一个列表以收集结果
    results = []

    # 遍历匹配项并提取所有信息
    for match in matches:
        if match:
            # 提取出各个部分并存储在一个列表中
            extracted_parts = [
                match[0],
                match[1],
                match[2],
            ]
            results.append(extracted_parts)
        else:
            print("没有匹配项")

    #打印提取出的结果
    print("afrog扫描结果:", results)

    return results
