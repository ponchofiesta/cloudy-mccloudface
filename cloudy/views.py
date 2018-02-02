from datetime import timedelta, datetime

import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from cloudy.models import Share
from cloudy.utils import Storage
from cloudymccloudface import settings


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def index(request):
    if request.user.is_authenticated:
        if 'path' in request.GET:
            path = request.GET['path']
            if path == os.sep:
                path = ''
        else:
            path = ''
        storage = Storage(settings.STORAGE_BASE, request.user)
        items = storage.get_items(path)
        params = Storage.get_path_params(path)
        details = storage.get_file_details(path)
        params['details'] = details
        params['items'] = items
        params['yesterday'] = datetime.now() - timedelta(1)

        return render(request, 'index/index.html', params)
    else:
        return render(request, 'index/index.html')


def newfolder(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        if request.method == 'GET':
            params = Storage.get_path_params(path)
            return render(request, 'index/newfolder.html', params)

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
            params = Storage.get_path_params(path)
            return render(request, 'index/upload.html', params)

        elif request.method == 'POST':
            storage = Storage(settings.STORAGE_BASE, request.user)
            storage.save_file(path, request.FILES['file'])
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def download(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        storage = Storage(settings.STORAGE_BASE, request.user)
        return storage.download_file(path)

    else:
        return render(request, 'index/index.html')


def delete(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        storage = Storage(settings.STORAGE_BASE, request.user)
        storage.delete_file(path)
        params = Storage.get_path_params(path)
        path = params['parents'][0]['path']
        return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def edit(request):
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        # Show file for editing
        if request.method == 'GET':
            storage = Storage(settings.STORAGE_BASE, request.user)
            params = Storage.get_path_params(path)
            details = storage.get_file_details(path)
            params['details'] = details
            return render(request, 'index/edit.html', params)

        # Save edited file
        elif request.method == 'POST':
            storage = Storage(settings.STORAGE_BASE, request.user)
            content = request.POST.get("filecontent", "")
            storage.update_file(path, content)
            params = Storage.get_path_params(path)
            path = params['parents'][0]['path']
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def share(request):
    if request.user.is_authenticated:
        path = request.GET.get('path', default='')
        share_path = request.GET.get('share_path', default='')
        share = Share.objects.filter(user=request.user, path=share_path)
        if len(share) > 0:
            share = share[0]
        else:
            share = Share.objects.create(user=request.user, path=share_path)
            share.save()
        params = Storage.get_path_params(path)
        params['share_path'] = share_path
        params['share_url'] = request.build_absolute_uri('/')[:-1] + reverse('share') + '/' + str(share.url_id)
        params['url_id'] = share.url_id
        return render(request, 'index/share.html', params)

    else:
        return render(request, 'index/index.html')


def share_delete(request, url_id):
    if request.user.is_authenticated:
        share = Share.objects.filter(user=request.user, url_id=url_id)
        path = ''
        if len(share) > 0:
            share = share[0]
            params = Storage.get_path_params(share.path)
            path = params['parents'][0]['path']
            share.delete()
        return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def share_view(request, url_id):
    share = Share.objects.filter(url_id=url_id)

    if len(share) > 0:
        share = share[0]
    else:
        return render(request, 'index/index.html')

    path = request.GET.get('path', default='')
    storage = Storage(settings.STORAGE_BASE, request.user)
    storage.set_base_path(storage.base_path + os.sep + share.path)
    details = storage.get_file_details(path)
    if 'is_file' in details and details['is_file']:
        return storage.download_file(path)

    items = storage.get_items(path)
    params = Storage.get_path_params(path)
    params['details'] = details
    params['items'] = items
    params['yesterday'] = datetime.now() - timedelta(1)
    params['is_share'] = True
    params['url_id'] = url_id

    return render(request, 'index/share_view.html', params)

