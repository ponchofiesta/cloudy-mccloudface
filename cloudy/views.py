import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from cloudy.models import Share
from cloudy.utils import Storage
from cloudymccloudface import settings


def signup(request):
    """
    Register a new user
    :param request:
    :return:
    """
    if request.method == 'POST':
        # do register the user
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        # show register form
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def index(request):
    """
    Main page with files listing
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        if 'path' in request.GET:
            path = request.GET['path']
            if path == os.sep:
                path = ''
        else:
            path = ''
        storage = Storage(settings.STORAGE_BASE, request.user)
        params = Storage.get_path_params(path)
        details = storage.get_file_details(path)
        items = storage.get_items(path)
        params['details'] = details
        params['items'] = items

        return render(request, 'index/index.html', params)
    else:
        return render(request, 'index/index.html')


def newfolder(request):
    """
    create a new folder
    :param request:
    :return:
    """
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        if request.method == 'GET':
            # show form for folder creation
            params = Storage.get_path_params(path)
            return render(request, 'index/newfolder.html', params)

        elif request.method == 'POST':
            # do create the folder
            foldername = request.POST.get('foldername', default='')
            if 'foldername' == '':
                return redirect(reverse('index') + '?path=' + path)

            storage = Storage(settings.STORAGE_BASE, request.user)
            storage.create_folder(path, foldername)
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def upload(request):
    """
    upload a file
    :param request:
    :return:
    """
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        if request.method == 'GET':
            # show upload form
            params = Storage.get_path_params(path)
            return render(request, 'index/upload.html', params)

        elif request.method == 'POST':
            # do save the file
            storage = Storage(settings.STORAGE_BASE, request.user)
            storage.save_file(path, request.FILES['file'])
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def download(request):
    """
    download a file
    :param request:
    :return:
    """
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')

        storage = Storage(settings.STORAGE_BASE, request.user)
        return storage.download_file(path)

    else:
        return render(request, 'index/index.html')


def delete(request):
    """
    delete a file or directory
    :param request:
    :return:
    """
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
    """
    edit or rename a file or rename a directory
    :param request:
    :return:
    """
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')
        edit_path = request.GET.get('edit_path', default='')

        # Show for editing
        if request.method == 'GET':
            storage = Storage(settings.STORAGE_BASE, request.user)
            params = Storage.get_path_params(path)
            details = storage.get_file_details(edit_path)
            params['details'] = details
            params['edit_path'] = edit_path
            params['item_name'] = edit_path.rsplit(os.sep, 1)[1]
            return render(request, 'index/edit.html', params)

        # Save edited file
        elif request.method == 'POST':
            storage = Storage(settings.STORAGE_BASE, request.user)
            is_file = request.POST.get("item_type", "")
            if is_file:
                # File
                name = request.POST.get("name", "")
                content = request.POST.get("filecontent", "")
                storage.update_file(edit_path, name, content)
            else:
                # Directory
                foldername = request.POST.get("foldername", "")
                storage.update_folder(edit_path, foldername)
            return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def share(request):
    """
    share a file or directory
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        path = request.GET.get('path', default='')
        share_path = request.GET.get('share_path', default='')

        # search for an existing share for this path
        share = Share.objects.filter(user=request.user, path=share_path)
        if len(share) > 0:
            share = share[0]
        else:
            # create a new share
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
    """
    delete a share
    :param request:
    :param url_id: unique UUID for the share
    :return:
    """
    if request.user.is_authenticated:
        # search for the share
        share = Share.objects.filter(user=request.user, url_id=url_id)
        path = ''
        if len(share) > 0:
            # get params and delete share
            share = share[0]
            params = Storage.get_path_params(share.path)
            path = params['parents'][0]['path']
            share.delete()
        return redirect(reverse('index') + '?path=' + path)

    else:
        return render(request, 'index/index.html')


def share_view(request, url_id):
    """
    show shared files and folders
    :param request:
    :param url_id: unique UUID for the share
    :return:
    """

    # search for the share
    share = Share.objects.filter(url_id=url_id)

    if len(share) > 0:
        share = share[0]
    else:
        return render(request, 'index/index.html')

    path = request.GET.get('path', default='')
    storage = Storage(settings.STORAGE_BASE, share.user)

    # limit base_path to the shared folder/file
    storage.set_base_path(storage.base_path + os.sep + share.path)
    details = storage.get_file_details(path)
    if 'is_file' in details and details['is_file']:
        # if it is a shared file just download it
        return storage.download_file(path)

    items = storage.get_items(path)
    params = Storage.get_path_params(path)
    params['details'] = details
    params['items'] = items
    params['is_share'] = True
    params['url_id'] = url_id

    return render(request, 'index/share_view.html', params)


def search(request):
    """
    search for files and directories
    :param request:
    :return:
    """
    if request.user.is_authenticated:

        path = request.GET.get('path', default='')
        pattern = request.GET.get('pattern', default='')
        storage = Storage(settings.STORAGE_BASE, request.user)
        params = Storage.get_path_params(path)
        params['items'] = storage.search(pattern)
        params['pattern'] = pattern

        return render(request, 'index/search.html', params)
    else:
        return render(request, 'index/index.html')