# -*- coding: utf-8 -*-
import json
import codecs


def read_json(path):
    with codecs.open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def write_json(obj, path):
    with codecs.open(path, 'w', encoding='utf8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)


def read_lines(path):
    with open(path, 'rb') as f:
        return f.read().decode('utf8').splitlines()

