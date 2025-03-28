from django.urls import path, include, re_path
from api.views import login, register, getAssetOrganization, demo, getAssetList, getProjectList, startscan, getScanList
from api.views import getPoclist, getVulnList, getAuthButtonList, getAuthMenuList, getAsset_inputlist
from api.views.sensitive_dir import getSensitive_dirList
from api.views.sensitive_info import getSensitive_infoList
urlpatterns = [
    path('login/', login.LoginViews.as_view()),  # 登录视图
    path('logout/',login.LogoutViews.as_view()),  # 注销
    path('menu/list/', getAuthMenuList.getAuthMenuList.as_view()),  # 获取菜单列表
    path('auth/buttons/', getAuthButtonList.getAuthButtonList.as_view()),  # 获取按钮权限
    path('edit_password/', login.EditPasswordView.as_view()),  # 改密视图

    path('register/',register.signViews.as_view()),  # 注册视图
    path('getAssetOrganization/', getAssetOrganization.getAssetOrganization.as_view()),  # 获取用户单位
    path('getAssetlist/', getAssetList.getAssetList.as_view()),  # 获取单位资产
    path('getProjectList/', getProjectList.getProjectList.as_view()),  # 获取项目管理
    path('getScanList/', getScanList.getScanList.as_view()),
    path('getPoclist/', getPoclist.getPoclist.as_view()),
    path('getVulnlist/', getVulnList.getVulnList.as_view()),
    path('getSensitive_dirList/', getSensitive_dirList.getSensitive_dirList.as_view()),
    path('getSensitive_infoList/', getSensitive_infoList.getSensitive_infoList.as_view()),
    path('getAsset_inputlist/', getAsset_inputlist.getAsset_inputList.as_view()),
    

    path('startScan/', startscan.StartScan.as_view()),

    path('getAssetAddDemo/', demo.getAssetAddDemo.as_view()),


    re_path('^asset/', include('api.views.asset.asset_urls')),
    re_path('^asset_input/', include('api.views.asset_input.asset_input_urls')),
    re_path('^project/', include('api.views.project.project_urls')),
    re_path('^scan/', include('api.views.scan.scan_urls')),
    re_path('^poc/', include('api.views.poc.poc_urls')),
    re_path('^vuln/', include('api.views.vuln.vuln_urls')),
    re_path('^sensitive_dir/', include('api.views.sensitive_dir.sensitive_dir_urls')),
    re_path('^sensitive_info/', include('api.views.sensitive_info.sensitive_info_urls')),

    # path('sign/', login.signViews.as_view()),
]
