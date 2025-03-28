from django.http import JsonResponse
from django.views import View
from app.models import Asset_info

# 资产删除视图
class deleteAsset(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "删除成功",
            'self': None,
        }

        data = request.data
        if not data.get('id'):
            res['self'] = 'asset'
            res['msg'] = '请选择对应资产'
            return JsonResponse(res)

        id_list = data.get('id')
        for id in id_list:
            Asset_info.objects.filter(asset_id=id).delete()
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})