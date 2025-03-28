from django.http import JsonResponse
from django.views import View
from api.serializers import TagsSerializer
from app.models import Poctags


class get_poc_tags(View):
    def get(self, request):
        res = {
            'code': 200,
            'data': [],
        }
        tags = Poctags.objects.all()
        projects_data = TagsSerializer(instance=tags, many=True).data
        res['data'] = projects_data
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})