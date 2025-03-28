import requests,json
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor

from requests import session

# AWS API 配置
AWVS_URL = 'https://127.0.0.1:3443'
API_KEY = '1986ad8c0a5b3df4d7028d5f3c06e936cec15aaaeecfd47588584351f9557485c'
HEADERS = {
    'X-Auth': API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def add_scan(target):
    # 创建目标
    # target_id = create_target(target)

    # 创建扫描
    # start_scan(target_id)
    # 启动扫描
    # scan_id = get_scan_id(target_id)
    scan_id = '70ba71d2-2132-48b5-905c-864e4c2c3c88'
    if scan_id:
        print(f'Started scan for {target}, Scan ID: {scan_id}')

        time.sleep(2)
        #等待扫描完成
        scan_session_id = wait_for_scan(scan_id)

        #获取结果并保存
        save_results(scan_id, scan_session_id)


def create_target(target):
    url = f'{AWVS_URL}/api/v1/targets'
    data = {
        "address": target,
        "description": f'Scanning {target}',
        "criticality":"10"
    }
    response = requests.post(url, headers=HEADERS, json=data,verify=False)
    if response.status_code == 201:
        print(f'Target {target} created successfully.')
        # 返回target_id
        return response.json().get('target_id')
    else:
        print(f'Failed to create target {target}:{response.text}')


def start_scan(target_id):
    # 获取目标 ID 的逻辑
    url = f'{AWVS_URL}/api/v1/scans'
    data = {
        "target_id": target_id,
        "profile_id": "11111111-1111-1111-1111-111111111112",
        "schedule":{
            "disable": False,
            "start_date": None,
            "time_sensitive": False
        }
    }
    # 发送请求开始扫描
    response = requests.post(url, headers=HEADERS, json=data,verify=False)

    if response.status_code == 201:
        print(f'Target {target_id} created successfully.')
    else:
        print(f'Failed to initiate scan for {target_id}:{response.json()}')

def get_scan_id(target_id):
    # 实现获取目标 ID 的逻辑
    url = f'{AWVS_URL}/api/v1/scans'
    response = requests.get(url, headers=HEADERS, verify=False)
    for scan in response.json()['scans']:
        if scan.get('target_id') == target_id:
            print(f'Target {target_id} found successfully {scan.get("scan_id")}.')
            return scan.get('scan_id')

def wait_for_scan(scan_id):
    url = f'{AWVS_URL}/api/v1/scans/{scan_id}'
    response = requests.get(url, headers=HEADERS, verify=False)
    # 由scan_id 获取scan_session_id
    data = json.loads(response.text)
    scan_session_id = data['current_session']['scan_session_id']
    print(f'Scan session ID: {scan_session_id}')
    while True:
        # 持续发送请求查询扫描是否完成
        response = requests.get(url, headers=HEADERS,verify=False)
        if response.status_code == 200:
            scan_status = data['current_session']['status']
            print(f'Scan status for ID {scan_id}: {scan_status}')
            if scan_status in ['completed', 'failed']:
                break
            time.sleep(10)  # 每10秒检查一次
        else:
            print(f'Error checking scan status: {response.text}')
            break

    return scan_session_id
def save_results(scan_id, scan_session_id):
    url = f'{AWVS_URL}/api/v1/scans/{scan_id}/results/{scan_session_id}/vulnerabilities'
    response = requests.get(url, headers=HEADERS,verify=False)
    data = json.loads(response.text)
    vuln_id = []
    if response.status_code == 200:
        for vuln in data['vulnerabilities']:
            vuln_id.append(vuln['vuln_id'])
    else:
        print(f'Failed to retrieve results for scan {scan_id}: {response.text}')



def awvs_scan(targets):
    with ThreadPoolExecutor(max_workers=5) as executor:
        [executor.submit(add_scan, target)for target in targets]  # 使用多线程启动扫描

if __name__ == '__main__':
    targets = ['testphp.vulnweb.com']  # 目标列表
    awvs_scan(targets)