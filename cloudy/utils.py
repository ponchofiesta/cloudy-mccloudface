import os
import pathlib
import mimetypes
import base64

from datetime import datetime
from shutil import rmtree

from django.http import HttpResponse, Http404


class Storage:
    base_path = ''

    def __init__(self, base_path, user):
        self.base_path = base_path + os.sep + user.profile.storage_path
        self.user = user

        # create users storage folder if not exists
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def set_base_path(self, base_path):
        self.base_path = base_path

    def get_items(self, path=''):
        if os.path.isfile(self.base_path + os.sep + path):
            params = Storage.get_path_params(path)
            path = params['parents'][0]['path']
        entries = []
        items = os.listdir(self.base_path + os.sep + path)
        for item in items:
            item_path = pathlib.Path(self.base_path + os.sep + path + os.sep + item)
            entry = {
                'is_dir': item_path.is_dir(),
                'path': self.base_path + os.sep + path + os.sep + item,
                'webpath': path + os.sep + item,
                'name': item,
                'type': mimetypes.guess_type(path + os.sep + item)[0]
            }
            entries.append(entry)

        return entries

    def get_file_details(self, path=''):
        filepath = ''
        if os.path.isfile(self.base_path):
            filepath = self.base_path
        elif os.path.isfile(self.base_path + os.sep + path):
            filepath = self.base_path + os.sep + path
        else:
            return {}

        item_path = pathlib.Path(filepath)
        item_type = mimetypes.guess_type(filepath)[0]
        with open((filepath), "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode('ascii')
        text = ''
        if 'text' in item_type:
            f = open(filepath)
            text = f.read()
            f.close()
        details = {
            'is_file': item_path.is_file(),
            'type': item_type,
            'name': item_path.name,
            'size': item_path.stat().st_size,
            'mdate': datetime.fromtimestamp(item_path.stat().st_mtime),
            'data': encoded_string,
            'text': text
        }
        return details

    def create_folder(self, path, foldername):
        abs_path = self.base_path + os.sep + path + os.sep + foldername
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

    def update_folder(self, path, foldername):
        abs_path = self.base_path + os.sep + path
        new_path = abs_path.rsplit(os.sep, 1)[0] + os.sep + foldername
        os.rename(abs_path, new_path)

    def save_file(self, path, file):
        abs_path = self.base_path + os.sep + path + os.sep + file.name
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def update_file(self, path, name, content):
        abs_path = self.base_path + os.sep + path
        f = open(abs_path, 'r+')
        f.truncate(0)
        f.write(content)
        f.close()
        new_path = abs_path.rsplit(os.sep, 1)[0] + os.sep + name
        os.rename(abs_path, new_path)

    def download_file(self, path):
        abs_path = ''
        if os.path.isfile(self.base_path):
            abs_path = self.base_path
        elif os.path.isfile(self.base_path + os.sep + path):
            abs_path = self.base_path + os.sep + path
        else:
            raise Http404
        if os.path.exists(abs_path):
            with open(abs_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(abs_path))
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(abs_path)
                return response
        raise Http404

    def delete_file(self, path):
        abs_path = self.base_path + os.sep + path
        if os.path.exists(abs_path):
            if os.path.isfile(abs_path):
                os.remove(abs_path)
            else:
                rmtree(abs_path)

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
