import re
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
from app.models import Ehole_info, Asset_info


dirsearch_path = os.path.join(os.path.dirname(__file__), '../tools/ehole_windows')  # 计算 wih 工具的目录

def run_ehole(target):

    print(f"ehole开始扫描: {target}")

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
        './ehole','finger',
        '-u', target
    ]
    # 执行命令并捕获输出
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dirsearch_path)
    output = result.stdout.decode('utf-8')
    parsed_results = handle_result(output)
    return parsed_results

def handle_result(result):
    # 正则表达式匹配每行中的状态码和路径
    pattern = r'\[ ([^|]+) \| ([^|]+) \| ([^|]+) \| (\d+) \| (\d+) \| ([^\]]+) \]'
    results = []
    matches = re.findall(pattern, result, re.MULTILINE)

    if matches:
        for match in matches:
            results.append(match)
    else:
        print("没有匹配项")
        results.append("no result")
    results = results[0]
    print("ehole 扫描结果:", results)
    return results


def ehole_scan(project_id):
    targets = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_ehole, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result = future.result()
            results[target] = result

            if result == "no result":
                ex_result = result
            else:
                ex_result = ' | '.join(result)

            print("开始将 ehole结果写入数据库")
            asset_info_instance = Asset_info.objects.filter(asset=target, asset_project=project_id).first()
            if asset_info_instance:
                    existing_results = Ehole_info.objects.filter(target=asset_info_instance.asset_id)
                    if existing_results.exists():
                        # 更新现有记录
                        existing_results.update(
                            ehole_result=ex_result,
                        )
                    else:
                        # 创建新记录
                        Ehole_info.objects.create(
                            target_id=asset_info_instance.asset_id,
                            ehole_result=ex_result,
                        )
    print("ehole扫描结果写入完成")
    return results


