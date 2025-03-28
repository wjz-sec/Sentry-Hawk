from django.views import View
from django.http import JsonResponse
from django import forms
from app.auth import is_login_method
from app.models import Scan_info, UserInfo, Projects
from api.views.login import clean_form

class BaseScanForm(forms.Form):
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
    Wih_scan_if = forms.BooleanField(required=False)
    JSFinder_scan_if = forms.BooleanField(required=False)
    Dirsearch_scan_if = forms.BooleanField(required=False)
    Oneforall_scan_if = forms.BooleanField(required=False)
    quake_if = forms.BooleanField(required=False)
    fofa_if = forms.BooleanField(required=False)
    hunter_if = forms.BooleanField(required=False)

class ScanForm(BaseScanForm):
    def clean_scan_name(self):
        scan_name = self.cleaned_data['scan_name']
        if Scan_info.objects.filter(scan_name=scan_name).exists():
            return self.add_error('scan_name', '扫描模板名称已存在,请重新输入')
        return scan_name

    def clean_project_id(self):
        project_id = self.cleaned_data['project_id']
        old_scan = Scan_info.objects.filter(project_id=project_id,
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
                                              JSFinder_scan_if=self.data.get('JSFinder_scan_if', False),
                                              Dirsearch_scan_if = self.data.get('Dirsearch_scan_if', False),
                                              quake_if=self.data['quake_if'],
                                              fofa_if=self.data['fofa_if'],
                                              hunter_if=self.data['hunter_if'])
        if old_scan.exists():
            return self.add_error(None, '扫描配置已经存在,可以直接选用模板: {}'.format(old_scan.first().scan_name))
        return project_id

class addScan(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': '扫描任务添加成功',
        }

        data = request.data
        parameter_list = ["asset_scan_if", "info_scan_if", "vuln_scan_if", "xray_scan_if", "nuclei_scan_if", "afrog_scan_if", "awvs_scan_if", "crt_sh_scan_if", "Ksubdomain_scan_if", "port_scan_if", "EHole_scan_if", "TideFinger_scan_if", "JSFinder_scan_if", "Dirsearch_scan_if", "quake_if", "fofa_if", "hunter_if"]
        for parameter in parameter_list:
            if not data.get(parameter):
                data[parameter] = False

        form = ScanForm(data)
        if not form.is_valid():
            res['self'], res['msg'] = clean_form(form)
            return JsonResponse(res)
        form.cleaned_data['project_id'] = Projects.objects.get(id=form.cleaned_data['project_id'])
        Scan_info.objects.create(**form.cleaned_data)

        res['code'] = 200

        return JsonResponse(res)
