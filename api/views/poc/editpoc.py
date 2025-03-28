from django.http import JsonResponse
from django.views import View
from app.models import Poc_info, Poctags
from django import forms
from api.views.login import clean_form
import ast
import os
import yaml

class BaseAssetForm(forms.Form):
    id = forms.CharField(required=False)
    poc_name = forms.CharField(error_messages={'required': '请输入要添加的POC的名称'}, required=True)
    author = forms.CharField(error_messages={'required': '请输入要添加的POC的作者'}, required=True)
    cvss_score = forms.CharField(error_messages={'required': '请输入要添加的POC的CVSS评分'}, required=True)
    severity = forms.CharField(error_messages={'required': '请选择要添加的POC的威胁等级'}, required=True)
    vendor = forms.CharField(error_messages={'required': '请输入要添加的POC的供应商'}, required=True)
    product = forms.CharField(error_messages={'required': '请输入要添加的POC的产品'}, required=True)
    tags = forms.CharField(error_messages={'required': '请选择要添加的POC标签'}, required=True)
    content = forms.CharField(error_messages={'required': '请输入要添加的POC内容'}, required=True)

class AssetForm(BaseAssetForm):
    def clean_severity(self):
        severity = self.cleaned_data['severity']
        if severity:
            if severity not in ['高危', '中危', '低危']:
                return self.add_error('severity', '请检查漏洞类型格式是否正确')
        return severity

class editpoc(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "添加成功",
            'self': None,
        }
        data = request.data
        
        # 如果是获取POC信息的请求
        if data.get('id') and not data.get('content'):
            poc = Poc_info.objects.get(id=data['id'])
            file_path = poc.content  # 获取存储的文件路径
            
            if not file_path or not os.path.exists(file_path):
                res['msg'] = "文件路径不存在"
                return JsonResponse(res)
            
            # 读取YAML文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                yaml_content = yaml.safe_load(file_content)
                
            # 从YAML中读取值
            severity_map = {'high': '高危', 'medium': '中危', 'low': '低危'}
            
            # 构建返回数据
            poc_data = {
                'id': poc.id,
                'poc_name': yaml_content['id'],
                'author': yaml_content['info']['author'],
                'cvss_score': yaml_content['info']['classification']['cvss-score'],
                'severity': severity_map.get(yaml_content['info']['severity'], '高危'),
                'vendor': yaml_content['info']['metadata']['vendor'],
                'product': yaml_content['info']['metadata']['product'],
                'tags': yaml_content['info']['tags'].split(',') if isinstance(yaml_content['info']['tags'], str) else yaml_content['info']['tags'],
                'content': file_content
            }
            res['data'] = poc_data
            res['code'] = 200
            return JsonResponse(res)
        
        # 如果是更新POC信息的请求
        form = AssetForm(data)
        if not form.is_valid():
            res['self'], res['msg'] = clean_form(form)
            return JsonResponse(res)
            
        tags_list = ast.literal_eval(form.cleaned_data.pop('tags', None))
        
        # 更新数据库记录
        pocinfo = Poc_info.objects.get(id=form.cleaned_data['id'])
        
        # 将severity转换为英文
        severity_map = {'高危': 'high', '中危': 'medium', '低危': 'low'}
        severity_en = severity_map.get(form.cleaned_data['severity'])
        
        # 读取原始YAML内容
        yaml_content = yaml.safe_load(form.cleaned_data['content'])
        original_content = form.cleaned_data['content']
        
        # 获取原始文件路径
        old_file_path = pocinfo.content
        old_poc_name = yaml_content['id']  # 从YAML中获取原始POC名称
        new_poc_name = form.cleaned_data['poc_name']
        
        # 在原始内容中替换值
        original_content = original_content.replace(f'id: {old_poc_name}', f'id: {new_poc_name}')
        original_content = original_content.replace(f'name: {old_poc_name}', f'name: {new_poc_name}')
        original_content = original_content.replace(f'author: {yaml_content["info"]["author"]}', f'author: {form.cleaned_data["author"]}')
        original_content = original_content.replace(f'severity: {yaml_content["info"]["severity"]}', f'severity: {severity_map.get(form.cleaned_data["severity"])}')
        original_content = original_content.replace(f'cvss-score: {yaml_content["info"]["classification"]["cvss-score"]}', f'cvss-score: {form.cleaned_data["cvss_score"]}')
        original_content = original_content.replace(f'vendor: {yaml_content["info"]["metadata"]["vendor"]}', f'vendor: {form.cleaned_data["vendor"]}')
        original_content = original_content.replace(f'product: {yaml_content["info"]["metadata"]["product"]}', f'product: {form.cleaned_data["product"]}')
        original_content = original_content.replace(f'tags: {yaml_content["info"]["tags"]}', f'tags: {",".join(tags_list)}')
        
        form.cleaned_data['content'] = original_content
        
        # 如果POC名称发生变化，需要更新文件名
        if old_poc_name != new_poc_name:
            # 构建新的文件路径
            new_file_path = os.path.join(os.path.dirname(old_file_path), f"{new_poc_name}.yaml")
            
            # 如果新文件名已存在，返回错误
            if os.path.exists(new_file_path) and old_file_path != new_file_path:
                res['msg'] = f"文件 {new_poc_name}.yaml 已存在"
                return JsonResponse(res)
            
            # 删除旧文件
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            
            # 使用新文件路径
            file_path = new_file_path
        else:
            file_path = old_file_path
        
        # 保存更新后的内容到新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(form.cleaned_data['content'])
        
        # 更新数据库记录
        Poc_info.objects.filter(id=form.cleaned_data['id']).update(
            poc_name=new_poc_name,
            content=file_path,
            author=form.cleaned_data['author'],
            cvss_score=form.cleaned_data['cvss_score'],
            severity=form.cleaned_data['severity'],
            vendor=form.cleaned_data['vendor'],
            product=form.cleaned_data['product']
        )
        
        # 更新标签
        tags = yaml_content['info']['tags']
        if isinstance(tags, str):
            tags = tags.split(',')
        tags_objects = [Poctags.objects.get_or_create(name=tag.strip())[0] for tag in tags]
        pocinfo.tags.set(tags_objects)
        
        res['code'] = 200
        res['msg'] = "更新成功"
        
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})