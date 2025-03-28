from django.http import JsonResponse
from django.views import View
from app.models import Projects, Asset_info, Tags
from django import forms
from api.views.login import clean_form
from api.serializers import ProjectsInfoSerializer
from django.core.paginator import Paginator

# 基础客户单位查询
class BaseProjectSearchForm(forms.Form):
    project_name = forms.CharField(required=False)
    project_tag = forms.CharField(required=False)
    pageNum = forms.IntegerField(error_messages={'required': '请选择对应的页面'}, required=True)
    pageSize = forms.IntegerField(error_messages={'required': '请选择对应的页面大小'}, required=True)
# 客户单位查询数据清洗
class ProjectSearchForm(BaseProjectSearchForm):
    def clean_asset_type(self):
        project_tag = self.cleaned_data['project_tag']
        if project_tag:
            if not Tags.objects.filter(id=project_tag).exists():
                return self.add_error('asset_type', '请检查项目类型格式是否正确')
        return project_tag
# 客户单位查询视图
class getProjectList(View):
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
        if form.cleaned_data['project_name']:
            filter_kwargs['name__icontains'] = form.cleaned_data['project_name']
        if form.cleaned_data['project_tag']:
            filter_kwargs['tag'] = form.cleaned_data['project_tag']
        if filter_kwargs:
            contact_list = Projects.objects.filter(**filter_kwargs).order_by('id')
        else:
            contact_list = Projects.objects.all().order_by('id')
        page_size = form.cleaned_data['pageSize']
        paginator = Paginator(contact_list, page_size)  # Show 25 contacts per page.
        page_number = form.cleaned_data['pageNum']
        page_obj = paginator.get_page(page_number)
        project_info_list = ProjectsInfoSerializer(instance=page_obj, many=True).data

        for project_info in project_info_list:
            project_id = project_info['id']
            ip_num = Asset_info.objects.filter(asset_project=project_id, asset_type='IP').count()
            domain_num = Asset_info.objects.filter(asset_project=project_id, asset_type='Domain').count()
            url_num = Asset_info.objects.filter(asset_project=project_id, asset_type='URL').count()
            project_info['url_num'] = url_num
            project_info['domain_num'] = domain_num
            project_info['ip_num'] = ip_num
        res['data']['list'] = project_info_list
        res['data']['pageSize'] = page_obj.paginator.num_pages
        res['data']['pageNum'] = page_obj.number
        res['data']['total'] = page_obj.paginator.count
        res['code'] = 200
        # print(res)
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})