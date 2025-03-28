from django.urls import path
from api.views.sensitive_dir import deleteSensitive_dir, getSensitive_dirList

urlpatterns = [
    path('delete/', deleteSensitive_dir.deleteSensitive_dir.as_view()),
    path('list/', getSensitive_dirList.getSensitive_dirList.as_view()),
]