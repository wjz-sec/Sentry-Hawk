from django.http import JsonResponse
from django.views import View
from app.models import Sensitive_dir, Asset_info
from django import forms
from api.views.login import clean_form
from api.serializers import Sensitive_dirSerializer
from django.core.paginator import Paginator


# 基础漏洞查询
class BaseSensitive_dirForm(forms.Form):
    projectId = forms.CharField(required=False)
    info = forms.CharField(required=False)
    target_id = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)


# 漏洞查询数据清洗
class Sensitive_dirForm(BaseSensitive_dirForm):
    pass


# 漏洞查询视图
class getSensitive_dirList(View):
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
        form = Sensitive_dirForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)
        projectId = form.cleaned_data['projectId']
        filter_kwargs = {}
        if projectId:
            filter_kwargs['project'] = projectId
        if form.cleaned_data['info']:
            filter_kwargs['info__icontains'] = form.cleaned_data['info']
        if form.cleaned_data['target_id']:
            target_id = form.cleaned_data['target_id']
            filter_kwargs['target_id'] = target_id
        if filter_kwargs:
            contact_list = Sensitive_dir.objects.filter(**filter_kwargs).order_by('id')
        else:
            contact_list = Sensitive_dir.objects.all().order_by('id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        sensitive_dir_list = Sensitive_dirSerializer(instance=page_obj, many=True).data
        res['data']['list'] = sensitive_dir_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})