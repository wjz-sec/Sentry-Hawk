from django.http import JsonResponse
from app.models import Asset_info, Wih_result, Vuln_info

def get_asset_counts(request):
    # 获取互联网资产数量
    total_assets = Asset_info.objects.count()
    
    # 获取URL资产数量
    url_assets = Asset_info.objects.filter(asset_type='URL').count()
    
    # 获取IP资产数量
    ip_assets = Asset_info.objects.filter(asset_type='IP').count()
    
    # 获取域名资产数量
    domain_assets = Asset_info.objects.filter(asset_type='Domain').count()
    
    # 构建返回的数据
    data = {
        'total_assets': total_assets,
        'url_assets': url_assets,
        'ip_assets': ip_assets,
        'domain_assets': domain_assets
    }
    return JsonResponse({
        'code': 200,
        'msg': "获取成功",
        'data': data,
    })


def getSensitiveCounts(request):
    # 构建返回的数据
    data = [
        {
            "name": "敏感路径泄露量",
            "value": Asset_info.objects.count(),
        },
        {
            "name": "敏感信息泄露量",
            "value": Wih_result.objects.count(),
        },
        {
            "name": "其余漏洞数量",
            "value": Vuln_info.objects.count(),
        },
    ]
    return JsonResponse({
        'code': 200,
        'msg': "获取成功",
        'data': data,
    })