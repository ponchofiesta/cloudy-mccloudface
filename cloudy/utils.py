import os
import pathlib
import mimetypes
import base64

from datetime import datetime
from shutil import rmtree

from django.http import HttpResponse, Http404


class Storage:
    """
    Handle storage operations for a user
    """
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
        """
        get files and folders in a directory
        :param path: directory to get children from
        :return: list with all elements
        """
        if os.path.isfile(self.base_path + os.sep + path):
            params = Storage.get_path_params(path)
            path = params['parents'][0]['path']
            if path == os.sep:
                path = ''
        entries = []
        items = os.listdir(self.base_path + os.sep + path)
        for item in items:
            # build element item
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
        """
        get details about a single file
        :param path: path to the file
        :return: dict with element details
        """
        filepath = ''
        if os.path.isfile(self.base_path):
            filepath = self.base_path
        elif os.path.isfile(self.base_path + os.sep + path):
            filepath = self.base_path + os.sep + path
        else:
            return {}

        item_path = pathlib.Path(filepath)
        item_type = mimetypes.guess_type(filepath)[0]

        # read binary content
        with open((filepath), "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode('ascii')

        # read text content
        text = ''
        if 'text' in item_type:
            f = open(filepath)
            text = f.read()
            f.close()

        # build element details item
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
        """
        create a folder
        :param path: parent path of the folder
        :param foldername: folder name to create
        :return:
        """
        abs_path = self.base_path + os.sep + path + os.sep + foldername
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

    def update_folder(self, path, foldername):
        """
        rename directory
        :param path: path of the directory
        :param foldername: folder name to rename
        :return:
        """
        abs_path = self.base_path + os.sep + path
        new_path = abs_path.rsplit(os.sep, 1)[0] + os.sep + foldername
        os.rename(abs_path, new_path)

    def save_file(self, path, file):
        """
        save a file
        :param path: path of the file
        :param file: file name to save
        :return:
        """
        abs_path = self.base_path + os.sep + path + os.sep + file.name
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def update_file(self, path, name, content):
        """
        rename a file
        :param path: path of the file
        :param name: new name of the file
        :param content: content to be written to file
        :return:
        """
        abs_path = self.base_path + os.sep + path

        # write content to file
        f = open(abs_path, 'r+')
        f.truncate(0)
        f.write(content)
        f.close()

        # rename file
        new_path = abs_path.rsplit(os.sep, 1)[0] + os.sep + name
        os.rename(abs_path, new_path)

    def download_file(self, path):
        """
        download a file
        :param path: path to the file
        :return:
        """

        # find the correct path
        abs_path = ''
        if os.path.isfile(self.base_path):
            abs_path = self.base_path
        elif os.path.isfile(self.base_path + os.sep + path):
            abs_path = self.base_path + os.sep + path
        else:
            raise Http404

        if os.path.exists(abs_path):
            # send file
            with open(abs_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(abs_path))
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(abs_path)
                return response
        raise Http404

    def delete_file(self, path):
        """
        delete a file
        :param path: path to the file
        :return:
        """
        abs_path = self.base_path + os.sep + path
        if os.path.exists(abs_path):
            if os.path.isfile(abs_path):
                # delete single file
                os.remove(abs_path)
            else:
                # delete directory with all its contents
                rmtree(abs_path)

    @staticmethod
    def get_path_params(path):
        """
        get basic information for a path
        :param path:
        :return:
        """
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

    def search(self, pattern):
        """
        search files and directories
        :param pattern:
        :return: list of found files and directories
        """

        # list of found elements
        found = []

        def search_element(path, element, pattern, is_dir):
            """
            check a specific element
            :param path: parent directory
            :param element: the file or directory to check
            :param pattern: search pattern
            :param is_dir: file or directory
            :return:
            """
            if pattern.lower() in element.lower():
                dirname = os.path.dirname(os.path.join(path, element))
                if dirname == '':
                    dirname = os.sep
                fullpath = os.path.join(dirname, element)
                found.append({
                    'path': dirname,
                    'fullpath': fullpath,
                    'name': os.path.basename(os.path.join(path, element)),
                    'is_dir': is_dir
                })

        # loop through all elements in users storage
        for root, dirs, files in os.walk(self.base_path):
            path = root[len(self.base_path):]
            for dir in dirs:
                search_element(path, dir, pattern, True)
            for file in files:
                search_element(path, file, pattern, False)

        return found
