from datetime import timedelta, datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from cloudy.utils import Storage
from cloudymccloudface import settings
from cloudy.models import Profile


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
        else:
            path = ''
        storage = Storage(settings.STORAGE_BASE, request.user)
        items = storage.get_items(path)
        params = Storage.get_path_params(path)
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