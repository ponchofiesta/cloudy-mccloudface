#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os
import pathlib


class Storage:
    def __init__(self, base_path, user):
        self.base_path = base_path + os.sep + user.profile.storage_path
        self.user = user

        # create users storage folder if not exists
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def get_items(self, path=''):
        items = os.listdir(self.base_path + os.sep + path)
        entries = []
        for item in items:
            item_path = pathlib.Path(self.base_path + os.sep + item)
            entry = {
                'is_dir': item_path.is_dir(),
                'path': self.base_path + os.sep + item,
                'name': item
            }
            entries.append(entry)

        return entries

    def create_folder(self, path, foldername):
        abs_path = self.base_path + os.sep + path + os.sep + foldername
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

    def save_file(self, path, file):
        abs_path = self.base_path + os.sep + path + os.sep + file.name
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
