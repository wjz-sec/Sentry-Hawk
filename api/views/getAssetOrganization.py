from django.http import JsonResponse
from django.views import View
from app.models import Projects,Tags
from api.serializers import ProjectsSerializer,TagsSerializer

class getAssetOrganization(View):
    def get(self,request):
        res = {
            'code': 200,
            'data': [],
        }
        tags = Tags.objects.all().order_by('id')
        tags_data = TagsSerializer(instance=tags, many=True).data
        for tag in tags_data:
            tag_id = tag['id']
            # print(tag_id)
            Organization = Projects.objects.filter(tag=tag_id).order_by('id')
            AssetOrganization_info = ProjectsSerializer(instance=Organization, many=True).data
            tag['children'] = AssetOrganization_info  # 注意这里使用的是'children'键
            res['data'].append(tag)  # 将处理后的标签数据添加到结果列表中
        # print(res)
        return JsonResponse(res,safe=False, json_dumps_params={'ensure_ascii': False})
