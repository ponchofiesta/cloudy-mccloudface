from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('newfolder', views.newfolder, name='newfolder'),
    path('upload', views.upload, name='upload'),
    path('download', views.download, name='download'),
    path('delete', views.delete, name='delete'),
    path('edit', views.edit, name='edit'),
    path('share', views.share, name='share'),
    path('share/<uuid:url_id>', views.share_view, name='share_view'),
    path('share/<uuid:url_id>/delete', views.share_delete, name='share_delete'),
    path('search', views.search, name='search'),
]