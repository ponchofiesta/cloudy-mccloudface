import os
import pathlib
import mimetypes
import base64

from datetime import datetime

from django.http import HttpResponse, Http404
from django.conf import settings


class Storage:
    def __init__(self, base_path, user):
        self.base_path = base_path + os.sep + user.profile.storage_path
        self.user = user

        # create users storage folder if not exists
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def get_items(self, path=''):
        if os.path.isfile(self.base_path + os.sep + path):
            path = path.rsplit('/', 1)
            path = path[0]
        entries = []
        items = os.listdir(self.base_path + os.sep + path)
        for item in items:
            item_path = pathlib.Path(self.base_path + os.sep + path + os.sep + item)
            entry = {
                'is_dir': item_path.is_dir(),
                'path': self.base_path + os.sep + path + os.sep + item,
                'webpath': path + os.sep + item,
                'name': item,
                'mdate': datetime.fromtimestamp(item_path.stat().st_mtime),
                'size': item_path.stat().st_size
            }
            entries.append(entry)

        return entries

    def get_file_details(self, path=''):
        details = {}
        if os.path.isfile(self.base_path + os.sep + path):
            item_path = pathlib.Path(self.base_path + os.sep + path)
            with open((self.base_path + os.sep + path), "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode('ascii')
            details = {
                'is_file': True,
                'type': mimetypes.guess_type(path)[0],
                'name': path.rsplit('/', 1)[1],
                'size': item_path.stat().st_size,
                'mdate': datetime.fromtimestamp(item_path.stat().st_mtime),
                'data': encoded_string
            }
        return details

    def create_folder(self, path, foldername):
        abs_path = self.base_path + os.sep + path + os.sep + foldername
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

    def save_file(self, path, file):
        abs_path = self.base_path + os.sep + path + os.sep + file.name
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def download_file(self, path):
        abs_path = self.base_path + os.sep + path
        if os.path.exists(abs_path):
            with open(abs_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(abs_path))
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(abs_path)
                return response
        raise Http404

    @staticmethod
    def get_path_params(path):
        return {
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
