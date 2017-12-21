from django.shortcuts import render

from cloudy.models import Storage


def index(request):

    if request.user.is_authenticated:
        storage = Storage(request.user)
        folders = storage.get_folders()
        return render(request, 'index/index.html', {'folders': folders})
    else:
        return render(request, 'index/index.html')
