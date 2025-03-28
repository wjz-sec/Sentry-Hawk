from django.http import JsonResponse
from django.views import View
from app.models import Wih_result, Asset_info
from django import forms
from api.views.login import clean_form
from api.serializers import Wih_resultSerializer
from django.core.paginator import Paginator

# 基础查询
class BaseWihResultForm(forms.Form):
    projectId = forms.CharField(required=False)
    type = forms.CharField(required=False)
    content = forms.CharField(required=False)
    target_id = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)

# 数据清洗
class WihResultForm(BaseWihResultForm):
    pass

# 查询视图
class getSensitive_infoList(View):
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
        form = WihResultForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)

        filter_kwargs = {}
        if form.cleaned_data['type']:
            filter_kwargs['type__icontains'] = form.cleaned_data['type']
        if form.cleaned_data['content']:
            filter_kwargs['content__icontains'] = form.cleaned_data['content']
        if form.cleaned_data['target_id']:
            target_id = form.cleaned_data['target_id']
            filter_kwargs['target_id'] = target_id

        if filter_kwargs:
            contact_list = Wih_result.objects.filter(**filter_kwargs).order_by('id')
        else:
            contact_list = Wih_result.objects.all().order_by('id')

        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        wih_result_list = Wih_resultSerializer(instance=page_obj, many=True).data
        res['data']['list'] = wih_result_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})