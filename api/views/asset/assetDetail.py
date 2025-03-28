from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

from django.views import View
from app.models import Asset_info, Ehole_info, Domain_ip, Ip_info, Domain_info
from api.serializers import UrlInfoSerializer, IpInfoSerializer, Asset_infoSerializer, DomainInfoSerializer


class AssetDetail(View):
    def get(self,request):
        res = {
            'code': 500,
            'msg': "获取成功",
            'data': [],
        }
        asset_id = request.GET.get('id')
        asset_interface = Asset_info.objects.get(asset_id=asset_id)
        assetInfo = Asset_infoSerializer(asset_interface).data
        
        # 获取Ehole指纹信息
        ehole_fingerprints = []
        if Ehole_info.objects.filter(target=asset_id).exists():
            ehole_info = Ehole_info.objects.get(target=asset_id)
            if ehole_info.ehole_result:
                ehole_fingerprints.extend(ehole_info.ehole_result.split('\n'))
        # if ehole_fingerprints:
        assetInfo['ehole_fingerprints'] = list(set(ehole_fingerprints))
        
        # 获取Tide指纹信息
        from app.models import Tide_result
        tide_fingerprints = []
        if Tide_result.objects.filter(target=asset_id).exists():
            tide_info = Tide_result.objects.get(target=asset_id)
            if tide_info.finger:
                tide_fingerprints.extend(tide_info.finger.split('\n'))
        # if tide_fingerprints:
        assetInfo['tide_fingerprints'] = list(set(tide_fingerprints))
        
        if asset_interface.asset_type == 'URL':
            if Ehole_info.objects.filter(target=asset_id).exists():
                url_info_interface = Ehole_info.objects.get(target=asset_id)
                assetInfo['url_info_list'] = UrlInfoSerializer(instance=url_info_interface).data
        elif asset_interface.asset_type == 'IP':
            if Ip_info.objects.filter(target=asset_id).exists():
                ip_info_interface = Ip_info.objects.filter(target=asset_id)
                assetInfo['ip_info_list'] = IpInfoSerializer(instance=ip_info_interface, many=True).data
                #assetInfo['ip_info_list'] = [ip_info['port'] for ip_info in IpInfoSerializer(instance=ip_info_interface, many=True).data]

                # 获取端口信息
                ports = []
                for ip_info in ip_info_interface:
                    if ip_info.port:
                        ports.extend(ip_info.port.split('\n'))
                if ports:
                    assetInfo['ports'] = list(set(ports))
        elif asset_interface.asset_type == 'Domain':
            if Domain_info.objects.filter(target=asset_id).exists():
                domain_info_list = Domain_info.objects.filter(target=asset_id).values_list('subdomain', flat=True)
                assetInfo['subdomain'] = '\n\r'.join(domain_info_list)
                
                # 获取Domain资产的端口信息
                if Ip_info.objects.filter(target=asset_id).exists():
                    ip_info_interface = Ip_info.objects.filter(target=asset_id)
                    assetInfo['ip_info_list'] = IpInfoSerializer(instance=ip_info_interface, many=True).data
                    
                    # 获取端口信息
                    ports = []
                    for ip_info in ip_info_interface:
                        if ip_info.port:
                            ports.extend(ip_info.port.split('\n'))
                    if ports:
                        assetInfo['ports'] = list(set(ports))
        else:
            res['msg'] = '资产类型不存在'
            return JsonResponse(res)
        
        res['data'] = assetInfo
        res['code'] = 200
        return JsonResponse(res,safe=False, json_dumps_params={'ensure_ascii': False})
