from app.models import Scan_info  # 替换为你的 Django 应用和模型
from plugin.info_scan_plugin import crtsh, dnsub, portscan, tidefinger,ehole,jsfinder,dirsearch,WIH,oneforall   # 导入你的插件脚本，包括 TideFinger

# 从数据库中获取扫描信息
def info_scan(scan_id):
    scan_info = Scan_info.objects.get(scan_id=scan_id)  # 直接获取扫描信息
    project_id = scan_info.project_id_id  # 获取项目 ID

    # 输出扫描信息
    print(scan_info)

    # 检查并调用相应的扫描函数
    if scan_info.crt_sh_scan_if:
        crtsh.process_domains(project_id)  # 调用 crtsh 的扫描函数

    if scan_info.port_scan_if:
        portscan.port_scan(project_id)  # 调用 portscan 的扫描函数

    if scan_info.TideFinger_scan_if:
        # print(scan_info.TideFinger_scan_if)
        tidefinger.tide_scan(project_id)  # 调用 TideFinger 的扫描函数

    if scan_info.EHole_scan_if:
        ehole.ehole_scan(project_id)  # 调用 EHole 的扫描函数

    if scan_info.Ksubdomain_scan_if:
        dnsub.process_domains(project_id)  # 调用 Ksubdomain 的扫描函数

    if scan_info.JSFinder_scan_if:
        jsfinder.jsfinder_scan(project_id)  # 调用 JSFinder 的扫描函数

    if scan_info.Dirsearch_scan_if:
        dirsearch.dirsearch_scan(project_id)  # 调用 Dirsearch 的扫描函数

    if scan_info.Wih_scan_if:
        WIH.wih_scan(project_id) # 调用 wih 的扫描函数

    if scan_info.Oneforall_scan_if:
        oneforall.find_sdomain(project_id) # 调用 Oneforall 的扫描函数




