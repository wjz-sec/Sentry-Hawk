from django.urls import path
from api.views.poc import deletepoc, addpoc, getpoctags, editpoc, batchaddpoc

urlpatterns = [
    path('add/', addpoc.addpoc.as_view()),
    path('getpoctags/', getpoctags.get_poc_tags.as_view()),
    path('edit/', editpoc.editpoc.as_view()),
    path('delete/', deletepoc.deletepoc.as_view()),
    path('batchadd/', batchaddpoc.batchaddpoc.as_view()),
]