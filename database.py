#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ruamel.yaml


class Database(dict):
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    def __init__(self, filename, default={}):
        self.filename = filename
        if not os.path.isfile(filename):
            Database.yaml.dump(default, open(filename, 'wt'))
            super().__init__(default)
            self.save()
        else:
            super().__init__(Database.yaml.load(open(self.filename, 'rt')))

    def __iter__(self):
        return super().__iter__()

    def save(self):
        Database.yaml.dump(dict(self), open(self.filename, 'wt'))
