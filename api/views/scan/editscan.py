from django.views import View
from django.http import JsonResponse
from django import forms
from app.auth import is_login_method
from app.models import Scan_info, UserInfo, Projects
from api.views.login import clean_form


class BaseScanForm(forms.Form):
    id = forms.IntegerField(error_messages={'required': '请输入扫描模板id'}, required=True)
    scan_name = forms.CharField(error_messages={'required': '请输入扫描模板名称'}, required=True)
    project_id = forms.CharField(error_messages={'required': '请选择对应的项目'}, required=True)
    asset_scan_if = forms.BooleanField(required=False)
    info_scan_if = forms.BooleanField(required=False)
    vuln_scan_if = forms.BooleanField(required=False)
    xray_scan_if = forms.BooleanField(required=False)
    nuclei_scan_if = forms.BooleanField(required=False)
    afrog_scan_if = forms.BooleanField(required=False)
    awvs_scan_if = forms.BooleanField(required=False)
    crt_sh_scan_if = forms.BooleanField(required=False)
    Ksubdomain_scan_if = forms.BooleanField(required=False)
    port_scan_if = forms.BooleanField(required=False)
    EHole_scan_if = forms.BooleanField(required=False)
    TideFinger_scan_if = forms.BooleanField(required=False)
    Wih_scan_if= forms.BooleanField(required=False)
    JSFinder_scan_if = forms.BooleanField(required=False)
    Dirsearch_scan_if = forms.BooleanField(required=False)
    Oneforall_scan_if = forms.BooleanField(required=False)
    quake_if = forms.BooleanField(required=False)
    fofa_if = forms.BooleanField(required=False)
    hunter_if = forms.BooleanField(required=False)


class ScanForm(BaseScanForm):

    def clean_project_id(self):
        project_id = Projects.objects.filter(name=self.cleaned_data['project_id']).first()
        old_scan = Scan_info.objects.filter(project_id=project_id,
                                            scan_name=self.data.get('scan_name'),
                                            asset_scan_if=self.data['asset_scan_if'],
                                            info_scan_if=self.data['info_scan_if'],
                                            vuln_scan_if=self.data['vuln_scan_if'],
                                            xray_scan_if=self.data['xray_scan_if'],
                                            nuclei_scan_if=self.data['nuclei_scan_if'],
                                            afrog_scan_if=self.data['afrog_scan_if'],
                                            awvs_scan_if=self.data['awvs_scan_if'],
                                            crt_sh_scan_if=self.data['crt_sh_scan_if'],
                                            Ksubdomain_scan_if=self.data['Ksubdomain_scan_if'],
                                            port_scan_if=self.data['port_scan_if'],
                                            EHole_scan_if=self.data['EHole_scan_if'],
                                            TideFinger_scan_if=self.data['TideFinger_scan_if'],
                                            Wih_scan_if=self.data['Wih_scan_if'],
                                            JSFinder_scan_if = self.data['JSFinder_scan_if'],
                                            Dirsearch_scan_if = self.data['Dirsearch_scan_if'],
                                            quake_if=self.data['quake_if'],
                                            fofa_if=self.data['fofa_if'],
                                            hunter_if=self.data['hunter_if'])
        if old_scan.exists():
            return self.add_error(None, '扫描模板未修改,请确认修改数据')
        return project_id


class editScan(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': '扫描任务编辑成功',
        }

        data = request.data

        # 检查项目是否存在
        try:
            project_identifier = data.get('project_id')
            if not project_identifier:
                res['msg'] = '项目不能为空'
                return JsonResponse(res)

            # 尝试通过ID查找项目
            try:
                project_id = int(project_identifier)
                project = Projects.objects.filter(id=project_id).first()
            except (ValueError, TypeError):
                # 如果不是有效的ID，则通过名称查找
                project = Projects.objects.filter(name=project_identifier).first()

            if not project:
                res['msg'] = f'项目 "{project_identifier}" 不存在'
                return JsonResponse(res)

            data['project_id'] = project.name  # 使用项目名称，因为表单验证期望名称

        except Exception as e:
            res['msg'] = f'查找项目时出错: {str(e)}'
            return JsonResponse(res)

        form = ScanForm(data)
        if not form.is_valid():
            res['self'], res['msg'] = clean_form(form)
            return JsonResponse(res)

        # 使用已验证的项目实例
        form.cleaned_data['project_id'] = project
        scan_id = form.cleaned_data.pop('id')
        Scan_info.objects.filter(scan_id=scan_id).update(**form.cleaned_data)

        res['code'] = 200
        return JsonResponse(res)
