from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from threading import Thread
from app.auth import is_login_method
from app.models import Scan_info, UserInfo
from plugin.info_scan import info_scan
from plugin.asset_scan import asset_scan
from plugin.vuln_scan import vuln_scan


def run_scan(scan_id):

    data = {'id': scan_id}
    Scan_Settings = Scan_info.objects.filter(scan_id=scan_id)

    if not Scan_Settings:
        return

    start_time = timezone.now()
    Scan_Settings.update(scan_start_time=start_time, scan_schedule=1)

    if Scan_Settings.first().asset_scan_if:
        asset_scan(data['id'])
        Scan_Settings.update(scan_schedule=33)

    if Scan_Settings.first().info_scan_if:
        info_scan(data['id'])
        Scan_Settings.update(scan_schedule=66)

    if Scan_Settings.first().vuln_scan_if:
        vuln_scan(data['id'])

    end_time = timezone.now()
    Scan_Settings.update(scan_end_time=end_time, scan_schedule=100)

class StartScan(View):
    def post(self, request):
        res = {
            'code': 200,
            'msg': '开始扫描任务',
        }

        data = request.data
        scan_id = data['id']

        # 创建并启动一个新线程来运行扫描任务
        thread = Thread(target=run_scan, args=(scan_id,))
        thread.start()

        return JsonResponse(res)
