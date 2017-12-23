import pathlib

import os
from django.shortcuts import render

from cloudy.utils import Storage
from cloudymccloudface import settings


def index(request):

    if request.user.is_authenticated:
        if 'path' in request.GET:
            path = request.GET['path']
        else:
            path = ''
        storage = Storage(settings.STORAGE_BASE, request.user)
        items = storage.get_items(path)
        vars = {
            'items': items,
            'parents': [
                {
                    'name': ppath.name,
                    'path': str(ppath)
                }
                for ppath in pathlib.Path(path).parents
            ],
            'path': path,
            'name': os.path.basename(path)
        }

        return render(request, 'index/index.html', vars)
    else:
        return render(request, 'index/index.html')
