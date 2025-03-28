from django.urls import path
from api.views.scan import addscan, editscan, deletescan

urlpatterns = [
    path('add/', addscan.addScan.as_view()),
    path('edit/', editscan.editScan.as_view()),
    path('delete/', deletescan.deleteScan.as_view()),
]