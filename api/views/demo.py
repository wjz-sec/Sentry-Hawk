from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook

class getAssetAddDemo(View):
    def post(self, request):
        # 创建一个Workbook对象
        wb = Workbook()
        ws = wb.active

        # 设置标题行
        ws.append(['资产', '所属单位', '资产类型', '备注'])

        # 将Workbook对象保存到HttpResponse对象
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="assets.xlsx"'

        wb.save(response)
        return response