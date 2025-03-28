from django.urls import path
from api.views.vuln import deletevuln

urlpatterns = [
    # path('add/', addvuln.addvuln.as_view()),
    # path('edit/', editvuln.editvuln.as_view()),
    path('delete/', deletevuln.deleteVuln.as_view()),
]