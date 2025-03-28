from django.http import JsonResponse
from django.views import View
from app.models import Poc_info, Poctags
from django import forms
import yaml
import os
from django.conf import settings
import re
import zipfile
from io import BytesIO


# 添加表单类
class BatchPocForm(forms.Form):
    file = forms.FileField(required=True)

    def clean_file(self):
        file = self.cleaned_data['file']
        
        # 验证文件格式
        if not any(file.name.lower().endswith(ext) for ext in ['.yaml', '.yml', '.zip']):
            return self.add_error('file', '请上传YAML或ZIP格式的文件')
            
        # 验证文件大小
        MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
        if file.size > MAX_UPLOAD_SIZE:
            return self.add_error('file', '文件大小超过限制（最大5MB）')
            
        # 如果是zip文件，验证内容
        if file.name.lower().endswith('.zip'):
            zip_file = zipfile.ZipFile(BytesIO(file.read()))
            all_files = [f for f in zip_file.namelist() 
                        if not f.endswith('/') 
                        and not f.startswith('__MACOSX/') 
                        and not f.startswith('.')]
                        
            # 检查是否包含非yaml文件
            non_yaml_files = [f for f in all_files if not any(f.lower().endswith(ext) for ext in ['.yaml', '.yml'])]
            if non_yaml_files:
                return self.add_error('file', f'ZIP文件中包含非YAML文件: {", ".join(non_yaml_files)}')
                
            # 检查是否有yaml文件
            if not any(f.lower().endswith(('.yaml', '.yml')) for f in all_files):
                return self.add_error('file', 'ZIP文件中未找到YAML文件')
                
            file.seek(0)  # 重置文件指针
            
        return file


class batchaddpoc(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "批量添加成功",
            'self': None,
        }

        form = BatchPocForm(request.POST, request.FILES)

        # 检查文件是否存在于请求中
        if 'file' not in request.FILES:
            res['msg'] = "请选择要导入的文件"
            return JsonResponse(res)

        file = request.FILES.get('file')
        if not file:
            res['msg'] = "请选择要导入的文件"
            return JsonResponse(res)

        # 验证文件格式
        for file in [file]:
            # 转换文件名为小写进行检查
            filename_lower = file.name.lower()
            if not (filename_lower.endswith('.yaml') or filename_lower.endswith('.zip')):
                res['msg'] = "文件格式不正确，仅支持YAML和ZIP格式"
                return JsonResponse(res)

            # 如果是zip文件，验证其中是否只包含yaml文件
            if filename_lower.endswith('.zip'):
                file.seek(0)  # 重置文件指针
                try:
                    zip_file = zipfile.ZipFile(BytesIO(file.read()))
                    all_files = zip_file.namelist()
                except zipfile.BadZipFile:
                    res['msg'] = "无效的ZIP文件格式"
                    return JsonResponse(res)
                except Exception as e:
                    res['msg'] = f"处理ZIP文件时出错: {str(e)}"
                    return JsonResponse(res)
                
                # 过滤出所有实际文件（排除目录和系统文件）
                actual_files = []
                for f in all_files:
                    if (not f.endswith('/') and 
                        not f.startswith('__MACOSX/') and 
                        not f.startswith('.')):
                        actual_files.append(f)
                
                # 检查是否所有文件都是yaml
                non_yaml_files = [f for f in actual_files if not f.lower().endswith('.yaml')]
                if non_yaml_files:
                    res['msg'] = f"ZIP文件中包含非YAML文件: {', '.join(non_yaml_files)}"
                    return JsonResponse(res)
                
                # 如果没有任何yaml文件
                yaml_files = [f for f in actual_files if f.lower().endswith('.yaml')]
                if not yaml_files:
                    res['msg'] = "ZIP文件中未找到YAML文件"
                    return JsonResponse(res)
                
                file.seek(0)  # 再次重置文件指针，为后续处理做准备

        # 创建poc存储目录
        poc_dir = os.path.join(settings.BASE_DIR, 'pocs')
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)

        MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB限制

        def process_yaml_file(yaml_content, filename):
            # 验证YAML格式
            yaml_data = yaml.safe_load(yaml_content)
            
            # 验证必要字段
            if 'id' not in yaml_data:
                return False, form.add_error('file', '请确保YAML文件包含id字段')
            
            # 验证POC名称格式
            if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', yaml_data['id']):
                return False, form.add_error('file', '请确保POC名称格式正确（仅允许字母、数字、下划线和连字符）')

            # 定义severity映射
            severity_map = {'high': '高危', 'medium': '中危', 'low': '低危'}
            
            # 构建poc_data用于数据库
            poc_data = {
                'poc_name': yaml_data['id'],
                'author': yaml_data.get('info', {}).get('author'),
                'cvss_score': yaml_data.get('info', {}).get('classification', {}).get('cvss-score'),
                'severity': severity_map.get(yaml_data.get('info', {}).get('severity'), '高危'),
                'vendor': yaml_data.get('info', {}).get('metadata', {}).get('vendor'),
                'product': yaml_data.get('info', {}).get('metadata', {}).get('product')
            }
            
            # 验证poc_name唯一性
            if Poc_info.objects.filter(poc_name=poc_data['poc_name']).exists():
                return False, form.add_error('file', f"POC {poc_data['poc_name']} 已存在")

            # 保存POC文件
            file_name = f"{poc_data['poc_name']}.yaml"
            file_path = os.path.join(poc_dir, file_name)
            
            # 写入文件内容
            with open(file_path, 'wb') as f:
                if isinstance(yaml_content, str):
                    f.write(yaml_content.encode('utf-8'))
                else:
                    f.write(yaml_content)
            
            # 保存到数据库
            poc_data['content'] = file_path
            poc_info = Poc_info.objects.create(**poc_data)
            
            # 处理tags
            tags = yaml_data.get('info', {}).get('tags', '')
            if isinstance(tags, str):
                tags = tags.split(',')
            tags_objects = [Poctags.objects.get_or_create(name=tag.strip())[0] for tag in tags]
            poc_info.tags.set(tags_objects)
            
            return True, {'msg': f"POC {poc_data['poc_name']} 导入成功"}

        # 处理文件
        success_count = 0
        error_messages = []
        
        for file in [file]:
            filename_lower = file.name.lower()  # 转换为小写进行检查
            if file.size > MAX_UPLOAD_SIZE:
                error_messages.append({'self': 'file', 'msg': f"文件大小超过限制（最大5MB）"})
                continue
            
            if any(filename_lower.endswith(ext) for ext in ['.yaml', '.yml']):  # 支持.yaml和.yml，不区分大小写
                file.seek(0)
                yaml_content = file.read().decode('utf-8')
                success, message = process_yaml_file(yaml_content, file.name)
                if success:
                    success_count += 1
                error_messages.append(message)
            
            elif filename_lower.endswith('.zip'):
                file.seek(0)
                try:
                    zip_file = zipfile.ZipFile(BytesIO(file.read()))
                    yaml_files = [f for f in zip_file.namelist() 
                                if f.lower().endswith(('.yaml', '.yml'))  # 支持.yaml和.yml，不区分大小写
                                and not f.startswith('__MACOSX/') 
                                and not f.startswith('.')]
                except zipfile.BadZipFile:
                    res['msg'] = "无效的ZIP文件格式"
                    return JsonResponse(res)
                except Exception as e:
                    res['msg'] = f"处理ZIP文件时出错: {str(e)}"
                    return JsonResponse(res)
                
                for yaml_file in yaml_files:
                    yaml_content = zip_file.read(yaml_file).decode('utf-8')
                    success, message = process_yaml_file(yaml_content, yaml_file)
                    if success:
                        success_count += 1
                    error_messages.append(message)

        # 构建最终消息
        if success_count > 0:
            res['code'] = 200
            res['msg'] = f"成功导入 {success_count} 个POC"
            return JsonResponse(res)
        else:
            res['msg'] = "导入失败，请检查文件格式是否正确"
            return JsonResponse(res) 