from django.http import JsonResponse
from django.views import View
from app.models import Poc_info, Poctags
from django import forms
from api.views.login import clean_form
import os
import yaml
from django.conf import settings

class BasePocForm(forms.Form):
    poc_name = forms.CharField(error_messages={'required': '请输入要添加的POC的名称'}, required=True)
    author = forms.CharField(error_messages={'required': '请输入要添加的POC的作者'}, required=True)
    cvss_score = forms.CharField(error_messages={'required': '请输入要添加的POC的CVSS评分'}, required=True)
    severity = forms.CharField(error_messages={'required': '请选择要添加的POC的威胁等级'}, required=True)
    vendor = forms.CharField(error_messages={'required': '请输入要添加的POC的供应商'}, required=True)
    product = forms.CharField(error_messages={'required': '请输入要添加的POC的产品'}, required=True)
    tags = forms.CharField(error_messages={'required': '请选择要添加的POC标签'}, required=True)
    content = forms.CharField(error_messages={'required': '请输入要添加的POC内容'}, required=True)

# 资产查询数据清洗
class PocForm(BasePocForm):
    def clean_poc_name(self):
        poc_name = self.cleaned_data['poc_name']
        if Poc_info.objects.filter(poc_name=poc_name).exists():
            return self.add_error('poc_name', 'POC名称已存在，请重新输入')
        return poc_name

    def clean_severity(self):
        severity = self.cleaned_data['severity']
        if severity:
            if severity not in ['高危', '中危', '低危']:
                return self.add_error('severity', '请检查漏洞类型格式是否正确')
        return severity

# 资产添加视图
class addpoc(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "添加成功",
            'self': None,
        }
        data = request.data
        form = PocForm(data)
        if not form.is_valid():
            res['self'], res['msg'] = clean_form(form)
            return JsonResponse(res)

        # 创建poc存储目录
        poc_dir = os.path.join(settings.BASE_DIR, 'pocs')
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)

        # 准备POC内容
        poc_content = form.cleaned_data.pop('content')
        poc_name = form.cleaned_data['poc_name']

        # 生成文件名和路径
        file_name = f"{poc_name}.yaml"
        file_path = os.path.join(poc_dir, file_name)

        # 将POC内容写入yaml文件
        try:
            with open(file_path, 'wb') as f:
                f.write(poc_content.encode('utf-8'))
        except Exception as e:
            res['msg'] = f"保存POC文件失败: {str(e)}"
            return JsonResponse(res)

        # 将文件路径存入数据库
        form.cleaned_data['content'] = file_path

        # 处理tags
        tags_list = form.cleaned_data.pop('tags', '').split(',')
        tags_objects = [Poctags.objects.get_or_create(name=tag.strip())[0] for tag in tags_list]

        # 创建POC记录
        poc_info = Poc_info.objects.create(**form.cleaned_data)
        poc_info.tags.set(tags_objects)

        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})