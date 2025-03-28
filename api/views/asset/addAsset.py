from django.http import JsonResponse
from django.views import View
from app.models import Asset_info, Projects
from django import forms
from api.views.login import clean_form

class BaseAssetForm(forms.Form):
    asset = forms.CharField(error_messages={'required': '请输入要添加的资产'}, required=True)
    asset_type = forms.CharField(error_messages={'required': '请选择资产类型'}, required=True)
    asset_project = forms.CharField(error_messages={'required': '请选择资产所属的项目'}, required=True)
# 资产查询数据清洗
class AssetForm(BaseAssetForm):
    def clean_asset(self):
        asset = self.cleaned_data['asset']
        if self.data['asset_project']:
            if Asset_info.objects.filter(asset=asset, asset_project=self.data['asset_project']).exists():
                return self.add_error('asset', '资产已存在，请重新输入')
        return asset

    def clean_asset_type(self):
        asset_type = self.cleaned_data['asset_type']
        if asset_type:
            if asset_type not in ['URL', 'IP', 'Domain']:
                return self.add_error('asset_type', '请检查资产类型格式是否正确')
        return asset_type

    def clean_asset_project(self):
        asset_project = self.cleaned_data['asset_project']
        if asset_project:
            exists = Projects.objects.filter(id=asset_project).exists()
            if not exists:
                return self.add_error('asset_project', '该项目不存在,请先在项目管理中新建项目')
        return asset_project
# 资产添加视图
class addAsset(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "添加成功",
            'self': None,
        }
        data = request.data
        if not data.get('asset_project'):
            data['asset_project'] = ''
        if not data.get('asset_type'):
            data['asset_type'] = ''
        form = AssetForm(data)
        if not form.is_valid():
            res['self'],res['msg'] = clean_form(form)
            return JsonResponse(res)
        form.cleaned_data['asset_project'] = Projects.objects.get(id=form.cleaned_data['asset_project'])
        Asset_info.objects.create(**form.cleaned_data)
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})