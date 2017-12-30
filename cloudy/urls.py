from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('newfolder', views.newfolder, name='newfolder'),
    path('upload', views.upload, name='upload'),
    path('download', views.download, name='download'),
]