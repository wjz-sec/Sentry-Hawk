from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
import json

class DecodeMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if request.method != 'GET' and request.META.get('CONTENT_TYPE') == 'application/json':
            data = json.loads(request.body)
            request.data =data