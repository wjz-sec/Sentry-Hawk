from app.models import Asset_info,Scan_info
from plugin.vuln_scan_plugin.afrog_test import afrog_scan
from plugin.vuln_scan_plugin.nuclei_test import nuclei_scan
from plugin.vuln_scan_plugin.xray_test import xray_scan



def vuln_scan(scan_id):

    print(scan_id)
    Scan_info_instance = Scan_info.objects.filter(scan_id=scan_id)
    project_id = Scan_info_instance.first().project_id_id
    print(project_id)
    target_list = Asset_info.objects.filter(asset_project_id=project_id).values_list('asset', flat=True)
    xray_if = Scan_info_instance.first().xray_scan_if
    nuclei_if = Scan_info_instance.first().nuclei_scan_if
    afrog_if = Scan_info_instance.first().afrog_scan_if

    if xray_if:
        xray_scan(target_list,project_id)
    if nuclei_if:
        nuclei_scan(target_list,project_id)
    if afrog_if:
        afrog_scan(target_list,project_id)


