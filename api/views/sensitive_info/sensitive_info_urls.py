from django.urls import path
from api.views.sensitive_info import deleteSensitive_info, getSensitive_infoList

urlpatterns = [
    path('delete/', deleteSensitive_info.deleteSensitive_info.as_view()),
    path('list/', getSensitive_infoList.getSensitive_infoList.as_view()),
]