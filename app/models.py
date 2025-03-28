from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser  # django的auth表


# 用户表
class UserInfo(AbstractUser):  # 继承django的auth表
    nid = models.AutoField(primary_key=True)
    nick_name = models.CharField(max_length=16, verbose_name='昵称', null=True, blank=True)
    token = models.CharField(verbose_name='id', help_text='其他平台的唯一登录id', max_length=64, null=True, blank=True)
    ip = models.GenericIPAddressField(verbose_name='ip地址', default='120.228.2.238', null=True, blank=True)
    addr = models.TextField(verbose_name='用户地址信息', null=True, blank=True)
    phone_num = models.BigIntegerField(verbose_name='手机号', unique=True, blank=True, null=True, )
    mail = models.EmailField(verbose_name='邮箱', max_length=255, unique=True, blank=True, null=True, )

    class Meta:
        verbose_name_plural = '用户'


# 资产详情表
class Asset_info(models.Model):
    asset_id = models.AutoField(primary_key=True, verbose_name='id')
    asset = models.CharField(max_length=255, verbose_name='资产')
    asset_project = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属单位'
    )
    URL = 'URL'
    Domain = 'Domain'
    IP = 'IP'
    small_program = '小程序'
    APP = 'APP'
    CHOICES = (
        (URL, 'URL'),
        (Domain, 'Domain'),
        (IP, 'IP'),
        (small_program, '小程序'),
        (APP, 'APP'),
    )
    asset_type = models.CharField(max_length=10, choices=CHOICES, verbose_name='资产类型')
    asset_add_time = models.DateTimeField(auto_now_add=True, verbose_name='资产创建时间', blank=True, null=True)
    asset_editor_time = models.DateTimeField(auto_now=True, verbose_name='资产最新修改时间', blank=True, null=True)
    asset_note = models.CharField(max_length=64, verbose_name='备注', blank=True, null=True)

    def __str__(self):
        return self.asset

    class Meta():
        verbose_name_plural = '输入资产详情'


class Asset_scan_input(models.Model):
    asset_id = models.AutoField(primary_key=True, verbose_name='id')
    asset = models.CharField(max_length=255, verbose_name='资产')
    asset_project = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属单位'
    )
    URL = 'URL'
    Domain = 'Domain'
    IP = 'IP'
    small_program = '小程序'
    APP = 'APP'
    CHOICES = (
        (URL, 'URL'),
        (Domain, 'Domain'),
        (IP, 'IP'),
        (small_program, '小程序'),
        (APP, 'APP'),
    )
    asset_type = models.CharField(max_length=10, choices=CHOICES, verbose_name='资产类型')
    asset_add_time = models.DateTimeField(auto_now_add=True, verbose_name='资产创建时间', blank=True, null=True)
    asset_editor_time = models.DateTimeField(auto_now=True, verbose_name='资产最新修改时间', blank=True, null=True)
    asset_note = models.CharField(max_length=64, verbose_name='备注', blank=True, null=True)

    def __str__(self):
        return self.asset

    class Meta():
        verbose_name_plural = '扫描资产详情'


# 扫描任务表
class Scan_info(models.Model):
    scan_id = models.AutoField(primary_key=True, verbose_name='id')
    scan_name = models.CharField(max_length=255, verbose_name='扫描模板名称', unique=True)
    scan_schedule = models.IntegerField(verbose_name='扫描进度', default=0, blank=True, null=True)
    project_id = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属项目'
    )
    asset_scan_if = models.BooleanField(verbose_name='资产收集调用', default=True)
    info_scan_if = models.BooleanField(verbose_name='信息收集调用', default=True)
    vuln_scan_if = models.BooleanField(verbose_name='漏洞扫描调用', default=True)
    xray_scan_if = models.BooleanField(verbose_name='xray调用', default=True)
    nuclei_scan_if = models.BooleanField(verbose_name='nuclei调用', default=True)
    afrog_scan_if = models.BooleanField(verbose_name='afrog调用', default=True)
    awvs_scan_if = models.BooleanField(verbose_name='awvs调用', default=True)
    crt_sh_scan_if = models.BooleanField(verbose_name='crt_sh调用', default=True)
    Ksubdomain_scan_if = models.BooleanField(verbose_name='Ksubdomain调用', default=True)
    port_scan_if = models.BooleanField(verbose_name='端口扫描调用', default=True)
    EHole_scan_if = models.BooleanField(verbose_name='EHole调用', default=True)
    TideFinger_scan_if = models.BooleanField(verbose_name='TideFinger调用', default=True)
    JSFinder_scan_if = models.BooleanField(verbose_name='JSFinder调用', default=True)
    Dirsearch_scan_if = models.BooleanField(verbose_name='Dirsearch调用', default=True)
    Wih_scan_if = models.BooleanField(verbose_name='wih调用', default=True)
    # URLfinder_scan_if = models.BooleanField(verbose_name='URLfinder', default=True)
    Oneforall_scan_if = models.BooleanField(verbose_name='Oneforall调用', default=True)
    quake_if = models.BooleanField(verbose_name='quake调用', default=True)
    fofa_if = models.BooleanField(verbose_name='fofa调用', default=True)
    hunter_if = models.BooleanField(verbose_name='hunter调用', default=True)
    scan_add_time = models.DateTimeField(auto_now_add=True, verbose_name='扫描创建时间', blank=True, null=True)
    scan_start_time = models.DateTimeField(verbose_name='扫描开始时间', blank=True, null=True)
    scan_end_time = models.DateTimeField(verbose_name='扫描结束时间', blank=True, null=True)

    def __str__(self):
        return self.scan_name

    class Meta:
        verbose_name_plural = '扫描任务'


# 计划任务表
class Planned_task(models.Model):
    plan_id = models.AutoField(primary_key=True, verbose_name='id')
    plan_name = models.CharField(max_length=255, verbose_name='计划任务名称', unique=True, blank=True, null=True)
    plan_time = models.CharField(max_length=255, verbose_name='计划时间设置', blank=True, null=True)
    plan_scan = models.ForeignKey(
        to='Scan_info',
        to_field='scan_id',
        on_delete=models.SET_NULL,  # 如果删除了头像，那么用户对应的这个字段就为 null
        verbose_name='计划扫描任务',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name_plural = '计划任务'


# 项目管理表
class Projects(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    name = models.CharField(max_length=255, verbose_name='项目名称', unique=True)
    tag = models.ForeignKey(
        to='Tags',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='项目标签',
    )
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='项目创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='项目最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '项目管理'

# 项目标签表
class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16, verbose_name='标签名字')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '项目标签'

# POC标签表
class Poctags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16, verbose_name='标签名字')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'POC标签'

# ip详情表
class Ip_info(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    port = models.CharField(max_length=100, verbose_name='端口', blank=True, null=True)
    status = models.CharField(max_length=50, verbose_name='端口状态', default='open', blank=True, null=True)
    service = models.CharField(max_length=1000, verbose_name='端口服务', blank=True, null=True)  # 新增字段，用于存储服务名称
    version = models.CharField(max_length=1000, verbose_name='服务信息', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'ip资产详情'

# domain详情表，target改为指向Asset_scan_input
class Domain_info(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',  # 指向Asset_scan_input
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    subdomain = models.CharField(max_length=255, verbose_name='子域名', null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'domain资产详情'


# domain_ip关系对应表，target改为指向Asset_scan_input
class Domain_ip(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',  # 指向Asset_scan_input
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='ip',
    )
    domain = models.CharField(max_length=255, verbose_name='域名', null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'domain_ip关系对应表'


# Url详情表
class Ehole_info(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.OneToOneField(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    ehole_result = models.CharField(max_length=1024, verbose_name='网站标题', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'url资产详情'


class Tide_result(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    finger = models.TextField(max_length=1024, verbose_name='指纹信息', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'Tide输出'


# 敏感目录表
class Sensitive_dir(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    project = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属单位'
    )
    url = models.CharField(max_length=1024, verbose_name='敏感目录', blank=True, null=True)
    status = models.CharField(max_length=64,verbose_name="状态码", blank=True, null=True)
    title = models.CharField(max_length=1024, verbose_name='标题', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = '敏感目录'




# 敏感信息泄露表
class Sensitive_info(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    project = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属单位'
    )
    js_info = models.CharField(max_length=1024,verbose_name='敏感js文件', blank=True, null=True)
    other = models.CharField(max_length=1024,verbose_name='敏感api接口', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = '敏感信息'


# 漏洞管理表
class Vuln_info(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='漏洞目标',
    )
    project = models.ForeignKey(
        to='Projects',
        to_field='id',
        on_delete=models.CASCADE,
        verbose_name='所属单位'
    )
    vuln_name = models.CharField(max_length=64, verbose_name='漏洞名称', blank=True, null=True)
    vuln_url = models.CharField(max_length=2048, verbose_name='漏洞url', blank=True, null=True)

    xray_result = 'xray扫描结果'
    nuclei_result = 'nuclei扫描结果'
    afrog_result = 'afrog扫描结果'
    Labour_add = '人工添加'

    CHOICES = (
        (xray_result, 'xray扫描结果'),
        (nuclei_result, 'nuclei扫描结果'),
        (afrog_result, 'afrog扫描结果'),
        (Labour_add, '人工添加'),
    )
    vuln_from = models.CharField(max_length=10, choices=CHOICES, verbose_name='漏洞来源', blank=True, null=True)

    high = '高危'
    middle = '中危'
    low = '低危'
    info = '信息'

    Level_CHOICES = (
        (high, '高危'),
        (middle, '中危'),
        (low, '低危'),
        (info, '信息')
    )
    vuln_level = models.CharField(max_length=64, choices=Level_CHOICES, verbose_name='漏洞危害级别', blank=True, null=True)
    # vlun_description = models.TextField(verbose_name='漏洞描述', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = '漏洞信息'


#POC管理表
class Poc_info(models.Model):
    id = models.AutoField(primary_key=True)
    poc_name = models.CharField(max_length=128, verbose_name='POC名称', unique=True)
    content = models.CharField(max_length=128000, verbose_name='POC内容', blank=True, null=True)
    author = models.CharField(max_length=128, verbose_name='作者', blank=True, null=True)

    low = '低危'
    middle = '中危'
    high = '高危'

    SEVERITY_CHOICES = (
        (low, '低危'),
        (middle, '中危'),
        (high, '高危'),
    )
    severity = models.CharField(max_length=128, choices=SEVERITY_CHOICES,  verbose_name='威胁等级',  blank=True, null=True)
    cvss_score = models.FloatField(verbose_name='CVSS评分', null=True, blank=True)
    vendor = models.CharField(max_length=255, verbose_name='供应商', blank=True, null=True)
    product = models.CharField(max_length=255, verbose_name='产品', blank=True, null=True)
    tags = models.ManyToManyField(
        to='Poctags',
        verbose_name='标签',
        blank=True
    )
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.poc_name

    class Meta:
        verbose_name_plural = 'POC管理'


class Wih_result(models.Model):
    id = models.AutoField(primary_key=True)
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
        null=True
    )
    type = models.TextField(max_length=1024,verbose_name='类型',null=True)
    content = models.TextField(max_length=1024,verbose_name='内容',null=True)

    def __str__(self):
        return self.target
    class Meta():
        verbose_name = 'wih扫描结果'

class OneforallResult(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    target = models.ForeignKey(
        to='Asset_info',
        to_field='asset_id',
        on_delete=models.CASCADE,
        verbose_name='扫描目标',
    )
    url = models.CharField(max_length=1024, verbose_name='URL', blank=True, null=True)
    ip = models.CharField(max_length=100, verbose_name='IP地址', blank=True, null=True)
    status = models.CharField(max_length=50, verbose_name='状态', blank=True, null=True)
    title = models.CharField(max_length=1024, verbose_name='标题', blank=True, null=True)
    addr = models.CharField(max_length=1024, verbose_name='地址', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', blank=True, null=True)
    editor_time = models.DateTimeField(auto_now=True, verbose_name='最新修改时间', blank=True, null=True)

    def __str__(self):
        return self.target.asset

    class Meta:
        verbose_name_plural = 'OneForall扫描结果'

