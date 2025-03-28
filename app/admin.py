from django.contrib import admin
from app.models import *

# 用户
admin.site.register(UserInfo)

# 项目标签
admin.site.register(Tags)

# POC标签表
admin.site.register(Poctags)

# 资产表
admin.site.register(Asset_info)
admin.site.register(Asset_scan_input)


# 计划任务表
admin.site.register(Planned_task)


# 项目表
admin.site.register(Projects)

# 扫描任务表
admin.site.register(Scan_info)


# ip攻击面信息
admin.site.register(Ip_info)

# url攻击面信息
admin.site.register(Ehole_info)

# domain攻击面信息
admin.site.register(Domain_info)

# domain_ip对应关系表
admin.site.register(Domain_ip)

# 敏感目录表
admin.site.register(Sensitive_dir)

# 敏感信息泄露表
admin.site.register(Sensitive_info)

# 漏洞管理表
admin.site.register(Vuln_info)

# WIH扫描结果表
admin.site.register(Wih_result)
