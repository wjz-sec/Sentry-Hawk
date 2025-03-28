from rest_framework import serializers
from dateutil import parser
from app.models import Tags
import os
import logging
from app.models import Poc_info

logger = logging.getLogger(__name__)

class ProjectsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class TagsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class Asset_infoSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='asset_id')
    asset = serializers.CharField()
    asset_type = serializers.CharField()
    asset_project = serializers.CharField()
    asset_editor_time = serializers.CharField()
    asset_note = serializers.CharField()
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 将 asset_editor_time 格式化为 "某年某月某日某时某分某秒" 的格式
        ret['asset_editor_time'] = parser.parse(ret['asset_editor_time']).strftime('%Y.%m.%d  %H:%M:%S')
        return ret

class ProjectsInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_name = serializers.CharField(source='name')
    project_tag = serializers.PrimaryKeyRelatedField(source='tag', read_only=True)


class ScanInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='scan_id')
    scan_name = serializers.CharField()
    scan_schedule = serializers.CharField()
    project_id = serializers.CharField()
    asset_scan_if = serializers.BooleanField()
    info_scan_if = serializers.BooleanField()
    vuln_scan_if = serializers.BooleanField()
    xray_scan_if = serializers.BooleanField()
    nuclei_scan_if = serializers.BooleanField()
    afrog_scan_if = serializers.BooleanField()
    awvs_scan_if = serializers.BooleanField()
    crt_sh_scan_if = serializers.BooleanField()
    Ksubdomain_scan_if = serializers.BooleanField()
    port_scan_if = serializers.BooleanField()
    EHole_scan_if = serializers.BooleanField()
    TideFinger_scan_if = serializers.BooleanField()
    Wih_scan_if = serializers.BooleanField()
    JSFinder_scan_if = serializers.BooleanField()
    Dirsearch_scan_if = serializers.BooleanField()
    Oneforall_scan_if = serializers.BooleanField()
    quake_if = serializers.BooleanField()
    fofa_if = serializers.BooleanField()
    hunter_if = serializers.BooleanField()
    scan_start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    scan_end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)


class IpInfoSerializer(serializers.Serializer):
    port = serializers.CharField()
    status = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()


class UrlInfoSerializer(serializers.Serializer):
    # title = serializers.CharField()
    ehole_result = serializers.CharField()
    # status = serializers.CharField()


class DomainInfoSerializer(serializers.Serializer):
    subdomain = serializers.CharField()


class VulnInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    target = serializers.CharField()
    vuln_name = serializers.CharField()
    vuln_from = serializers.CharField()
    vuln_level = serializers.CharField()
    editor_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)


class Sensitive_dirSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    target = serializers.CharField()
    # info = serializers.CharField()
    url = serializers.CharField()
    status = serializers.CharField()
    title = serializers.CharField()
    editor_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)


class Sensitive_infoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    target = serializers.CharField()
    # info = serializers.CharField()
    js_info = serializers.CharField()
    other = serializers.CharField()
    editor_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

class TagsSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('name',)  # 只包含name字段

class PocInfoSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    add_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    editor_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Poc_info
        fields = ['id', 'poc_name', 'content', 'author', 'severity', 'cvss_score', 
                 'vendor', 'product', 'tags', 'add_time', 'editor_time']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class Wih_resultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    content = serializers.CharField()
    target_id = serializers.CharField()
