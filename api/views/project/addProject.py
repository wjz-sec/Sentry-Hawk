from django.http import JsonResponse
from django.views import View
from app.models import Projects, Tags
from django import forms
from api.views.login import clean_form

class BaseProjectForm(forms.Form):
    project_name = forms.CharField(error_messages={'required': '请输入要添加的单位'}, required=True)
    project_tag = forms.CharField(error_messages={'required': '请选择项目类型'}, required=True)

# 资产查询数据清洗
class projectForm(BaseProjectForm):
    def clean_project_name(self):
        project_name = self.cleaned_data['project_name']
        if self.data.get('project_tag'):
            if Projects.objects.filter(name=project_name, tag=self.data['project_tag']).exists():
                return self.add_error('project_name', '项目已存在，请重新输入')
        return project_name

    def clean_project_tag(self):
        project_tag = self.cleaned_data['project_tag']
        if project_tag:
            if not Tags.objects.filter(id=project_tag).exists():
                return self.add_error('project_tag', '请检查项目类型格式是否正确')
        return project_tag

# 资产添加视图
class addProject(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "添加成功",
            'self': None,
        }
        data = request.data
        print(data)
        if not data.get('asset_type'):
            data['asset_type'] = ''
        form = projectForm(data)
        if not form.is_valid():
            res['self'],res['msg'] = clean_form(form)
            return JsonResponse(res)
        tag_instance = Tags.objects.get(id=form.cleaned_data['project_tag'])
        Projects.objects.create(name=form.cleaned_data['project_name'], tag=tag_instance)
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})