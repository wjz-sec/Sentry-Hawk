from django.http import HttpResponse
from django.views import View
from app.models import Asset_info, Ip_info
from openpyxl import Workbook

# 资产导出视图
class downloadAssetInfo(View):
    def post(self, request):
        data = request.data

        projectId = data.get('projectId')
        filter_kwargs = {}
        if projectId:
            filter_kwargs['asset_project'] = projectId
        if data.get('asset'):
            filter_kwargs['asset__icontains'] = data.get('asset')
        if data.get('asset_type'):
            filter_kwargs['asset_type'] = data.get('asset_type')
        if filter_kwargs:
            contact_list = Asset_info.objects.filter(**filter_kwargs).order_by('asset_id')
        else:
            contact_list = Asset_info.objects.all().order_by('asset_id')

        # 创建一个Workbook对象
        wb = Workbook()
        ws = wb.active

        # 设置标题行
        ws.append(['资产', '端口信息', '所属单位', '资产类型', '创建时间', '备注'])

        # 填充数据行
        for contact in contact_list:
            if contact.asset_editor_time.tzinfo:
                contact.asset_editor_time = contact.asset_editor_time.strftime('%Y-%m-%d %H:%M:%S')
            # 获取端口信息
            port_info = Ip_info.objects.filter(target=contact)
            ports = ', '.join([f"{p.port}({p.service})" for p in port_info]) if port_info else ''
            
            ws.append([
                contact.asset,
                ports,
                contact.asset_project.name,
                contact.asset_type,
                contact.asset_editor_time,
                contact.asset_note
            ])

        # 将Workbook对象保存到HttpResponse对象
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="assets.xlsx"'

        wb.save(response)
        return response