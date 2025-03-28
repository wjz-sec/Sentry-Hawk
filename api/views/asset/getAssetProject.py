from django.http import JsonResponse
from django.views import View
from api.serializers import ProjectsSerializer
from app.models import Projects


class getAssetProject(View):
    def get(self, request):
        res = {
            'code': 200,
            'data': [],
        }
        projects = Projects.objects.all()
        projects_data = ProjectsSerializer(instance=projects, many=True).data
        res['data'] = projects_data
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})