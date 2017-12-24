import pathlib

import os
from django.shortcuts import render, redirect
from django.urls import reverse

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


def newfolder(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        if request.method == 'GET':
            vars = {
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
            return render(request, 'index/newfolder.html', vars)

        elif request.method == 'POST':
            foldername = request.POST.get('foldername', default='')
            if 'foldername' == '':
                return redirect(reverse('index') + '?path=' + path)

            storage = Storage(settings.STORAGE_BASE, request.user)
            storage.create_folder(path, foldername)
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')

def upload(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        if request.method == 'GET':
            vars = {
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
            return render(request, 'index/upload.html', vars)

        elif request.method == 'POST':
            storage = Storage(settings.STORAGE_BASE, request.user)
            storage.save_file(path, request.FILES['file'])
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')