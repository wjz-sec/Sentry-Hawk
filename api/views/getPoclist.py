from django.http import JsonResponse
from django.views import View
from app.models import Poc_info, Asset_info, Tags
from django import forms
from api.views.login import clean_form
from api.serializers import PocInfoSerializer
from django.core.paginator import Paginator
import os

# 基础POC查询
class BasePocSearchForm(forms.Form):
    author = forms.CharField(required=False)
    poc_name = forms.CharField(required=False)
    tags = forms.CharField(required=False)
    vendor = forms.CharField(required=False)
    product = forms.CharField(required=False)
    severity = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)
# 漏洞查询数据清洗
class PocSearchForm(BasePocSearchForm):
    def clean_severity(self):
        severity = self.cleaned_data['severity']
        if severity:
            if severity not in ['高危', '中危', '低危']:
                return self.add_error('severity', '请检查漏洞类型格式是否正确')
        return severity
# 漏洞查询视图
class getPoclist(View):
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
        form = PocSearchForm(data)
        if not form.is_valid():
            res['msg'] = clean_form(form)
            return JsonResponse(res)

        filter_kwargs = {}
        if form.cleaned_data['severity']:
            filter_kwargs['severity'] = form.cleaned_data['severity']
        if form.cleaned_data['product']:
            filter_kwargs['product__icontains'] = form.cleaned_data['product']
        if form.cleaned_data['vendor']:
            filter_kwargs['vendor__icontains'] = form.cleaned_data['vendor']
        if form.cleaned_data['poc_name']:
            filter_kwargs['poc_name__icontains'] = form.cleaned_data['poc_name']
        if form.cleaned_data['author']:
            filter_kwargs['author__icontains'] = form.cleaned_data['author']
        if form.cleaned_data['tags']:
                filter_kwargs['tags__name__icontains'] = form.cleaned_data['tags']
        if filter_kwargs:
            contact_list = Poc_info.objects.filter(**filter_kwargs).order_by('id')
        else:
            contact_list = Poc_info.objects.all().order_by('id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        Poc_info_list = PocInfoSerializer(instance=page_obj, many=True).data
        for poc_info in Poc_info_list:
            poc_info_instance = Poc_info.objects.filter(id=poc_info['id']).first()
            file_path = poc_info['content']
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 保持原始文本格式，不进行YAML解析和重新序列化
                        poc_info['content'] = f.read().strip()
                except Exception as e:
                    poc_info['content'] = f"读取文件失败：{str(e)}"
            
            tags_list = poc_info_instance.tags.all()
            poc_info['tags'] = [tag.name.strip() for tag in tags_list]
            
            # 格式化时间
            if poc_info_instance.add_time:
                poc_info['add_time'] = poc_info_instance.add_time.strftime("%Y-%m-%d %H:%M:%S")
            if poc_info_instance.editor_time:
                poc_info['editor_time'] = poc_info_instance.editor_time.strftime("%Y-%m-%d %H:%M:%S")
            
        res['data']['list'] = Poc_info_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})