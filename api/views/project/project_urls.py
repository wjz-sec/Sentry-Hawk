from django.urls import path
from api.views.project import addProject, editProject, deleteProject

urlpatterns = [
    path('add/', addProject.addProject.as_view()),
    path('edit/', editProject.editProject.as_view()),
    path('delete/', deleteProject.deleteProject.as_view()),
]