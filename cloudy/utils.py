#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os

import files


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
            item_path = files.Path(self.base_path + os.sep + item)
            item_object = item_path.get()
            entry = {
                'type': item_path.type(),
                'paths': files.Path.split(self.base_path + os.sep + item),
                'path': self.base_path + item,
                'name': item_object.name
            }
            entries.append(entry)

        return entries
