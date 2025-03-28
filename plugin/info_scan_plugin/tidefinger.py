import re
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
from app.models import Tide_result, Asset_info


dirsearch_path = os.path.join(os.path.dirname(__file__), '../tools/Tide_finger')  # 计算 wih 工具的目录

def run_tide(target):

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
        './TideFinger',
        '-u', target
    ]
    # 执行命令并捕获输出
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dirsearch_path)
    output = result.stdout.decode('utf-8')
    parsed_results = handle_result(output)
    return parsed_results

def handle_result(result):
    # 定义用于匹配 ANSI 转义序列的正则表达式
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
     # 去除文本中的 ANSI 转义序列
    cleaned_text = ansi_escape.sub('', result)

    # 正则表达式匹配每行中的状态码和路径
    pattern = r'\[\+\]\s*(\[[^]]+\].*)'
    results = []
    matches = re.findall(pattern, cleaned_text)
    if matches:
        for match in matches:
            results.append(match)
    else:
        print("未找到匹配内容")
        results.append("no title")
    print(results)
    return results


def tide_scan(project_id):
    targets = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    """
    使用线程池并发扫描多个目标，并将结果保存到数据库
    """
    results = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(run_tide, target): target for target in targets}
        for future in futures:
            target = futures[future]
            result = future.result()
            results[target] = result


            print("开始将 tide 结果写入数据库")
            asset_info_instance = Asset_info.objects.filter(asset=target, asset_project=project_id).first()
            if asset_info_instance:
                    existing_results = Tide_result.objects.filter(target=asset_info_instance.asset_id)
                    if existing_results.exists():
                        # 更新现有记录
                        existing_results.update(
                            finger=result[0],
                        )
                    else:
                        # 创建新记录
                        Tide_result.objects.create(
                            target_id=asset_info_instance.asset_id,
                            finger=result[0],
                        )
    print("tide 扫描结果写入完成")
    return results
