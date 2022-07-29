from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('saveFile/', views.saveFile, name='saveFile'),
    path('getFile/', views.getFile, name='getFile'),
    path('getAllCreations/', views.getAllCreations, name='getAllCreations'),
    path('getAllUserCreations/', views.getAllUserCreations, name='getAllUserCreations'),
    path('updateRating/', views.updateRating, name='updateRating'),
    path('updateVisibility/', views.updateVisibility, name='updateVisibility'),
    path('submitCreation/', views.submitCreation, name='submitCreation'),
    path('getAllSubmissions/', views.getAllSubmissions, name='getAllSubmissions'),
    path('getSubmission/', views.getSubmission, name='getSubmission'),
    path('deleteCreation/', views.deleteCreation, name='deleteCreation'),
    path('cleanFirebase/', views.cleanFirebase, name='cleanFirebase'),
    path('report/', views.report, name='report'),
    path('getReported/', views.getReported, name='getReported'),
    path('unreport/', views.unreport, name='unreport')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)