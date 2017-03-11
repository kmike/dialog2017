# -*- coding: utf-8 -*-
import json
import codecs


def read_json(path):
    with codecs.open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def read_lines(path):
    with open(path, 'rb') as f:
        return f.read().decode('utf8').splitlines()

