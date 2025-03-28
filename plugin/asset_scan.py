from app.models import Scan_info
from plugin.asset_scan_plugin import quake
from plugin.asset_scan_plugin.fofa import fofa

def asset_scan(scan_id):
    scan_info = Scan_info.objects.filter(scan_id=scan_id).first()

    if scan_info:
        project_id = scan_info.project_id_id
        
        if scan_info.quake_if:
            quake.quake(project_id)
            
        if scan_info.fofa_if:
            fofa.fofa(project_id)