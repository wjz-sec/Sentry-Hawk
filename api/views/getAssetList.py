from django.http import JsonResponse
from django.views import View
from app.models import Asset_info
from django import forms
from api.views.login import clean_form
from api.serializers import Asset_infoSerializer
from django.core.paginator import Paginator

# 基础资产查询
class BaseAssetSearchForm(forms.Form):
    projectId = forms.IntegerField(required=False)
    asset = forms.CharField(required=False)
    asset_type = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)
# 资产查询数据清洗
class AssetSearchForm(BaseAssetSearchForm):
    def clean_asset_type(self):
        asset_type = self.cleaned_data['asset_type']
        if asset_type:
            if asset_type not in ['URL', 'IP', 'Domain']:
                return self.add_error('asset_type', '请检查资产类型格式是否正确')
        return asset_type
# 资产查询视图
class getAssetList(View):
    def post(self, request):
        res = {
            'code': 500,
            'data': {
                'list': [],
                'pageSize': '',
                'pageNum': '',
                'total': ''
            },
        }
        data = request.data
        form = AssetSearchForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)
        projectId = form.cleaned_data['projectId']
        filter_kwargs = {}
        if projectId:
            filter_kwargs['asset_project'] = projectId
        if form.cleaned_data['asset']:
            filter_kwargs['asset__icontains'] = form.cleaned_data['asset']
        if form.cleaned_data['asset_type']:
            filter_kwargs['asset_type'] = form.cleaned_data['asset_type']
        if filter_kwargs:
            contact_list = Asset_info.objects.filter(**filter_kwargs).order_by('asset_id')
        else:
            contact_list = Asset_info.objects.all().order_by('asset_id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        asset_info_list = Asset_infoSerializer(instance=page_obj, many=True).data
        res['data']['list'] = asset_info_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})