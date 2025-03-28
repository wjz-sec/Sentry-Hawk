from django.http import JsonResponse
from django.views import View
from app.models import Vuln_info, Asset_info
from django import forms
from api.views.login import clean_form
from api.serializers import VulnInfoSerializer
from django.core.paginator import Paginator

# 基础漏洞查询
class BaseVulnSearchForm(forms.Form):
    projectId = forms.IntegerField(required=False)
    vuln_name = forms.CharField(required=False)
    target = forms.CharField(required=False)
    vuln_level = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)
# 漏洞查询数据清洗
class VulnSearchForm(BaseVulnSearchForm):
    def clean_asset_type(self):
        vuln_level = self.cleaned_data['vuln_level']
        if vuln_level:
            if vuln_level not in ['高危', '中危', '低危']:
                return self.add_error('asset_type', '请检查漏洞类型格式是否正确')
        return vuln_level
# 漏洞查询视图
class getVulnList(View):
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
        form = VulnSearchForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)
        projectId = form.cleaned_data['projectId']
        filter_kwargs = {}
        if projectId:
            filter_kwargs['project'] = projectId
        if form.cleaned_data['vuln_name']:
            filter_kwargs['vuln_name__icontains'] = form.cleaned_data['vuln_name']
        if form.cleaned_data['target']:
            if Asset_info.objects.filter(asset__icontains=form.cleaned_data['target']).exists():
                target = Asset_info.objects.filter(asset__icontains=form.cleaned_data['target']).first()
                filter_kwargs['target'] = target
        if form.cleaned_data['vuln_level']:
            filter_kwargs['vuln_level'] = form.cleaned_data['vuln_level']
        if filter_kwargs:
            contact_list = Vuln_info.objects.filter(**filter_kwargs).order_by('id')
        else:
            contact_list = Vuln_info.objects.all().order_by('id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        vuln_info_list = VulnInfoSerializer(instance=page_obj, many=True).data
        res['data']['list'] = vuln_info_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})