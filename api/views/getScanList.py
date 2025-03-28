from django.http import JsonResponse
from django.views import View
from app.models import Scan_info
from django import forms
from api.views.login import clean_form
from api.serializers import ScanInfoSerializer
from django.core.paginator import Paginator

# 基础客户单位查询
class BaseProjectSearchForm(forms.Form):
    scan_name = forms.CharField(required=False)
    project = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)
# 客户单位查询数据清洗
class ProjectSearchForm(BaseProjectSearchForm):
    pass
# 客户单位查询视图
class getScanList(View):
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
        form = ProjectSearchForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)

        filter_kwargs = {}
        if form.cleaned_data['scan_name']:
            filter_kwargs['scan_name__icontains'] = form.cleaned_data['scan_name']
        if form.cleaned_data['project']:
            filter_kwargs['project_id__icontains'] = form.cleaned_data['project']
        if filter_kwargs:
            contact_list = Scan_info.objects.filter(**filter_kwargs).order_by('scan_id')
        else:
            contact_list = Scan_info.objects.all().order_by('scan_id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        scan_info_list = ScanInfoSerializer(instance=page_obj, many=True).data
        res['data']['list'] = scan_info_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})