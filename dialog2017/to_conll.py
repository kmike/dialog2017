#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import argparse

import tqdm

from dialog2017 import conll
from .utils import read_json


def convert(input_path, output_path):
    print("reading json corpus...")
    sents = read_json(input_path)

    print("converting to conll format...")
    with codecs.open(output_path, 'w', encoding='utf8') as f:
        conll.write_sents(tqdm.tqdm(sents, unit=' sentences'), f)
    print("done.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("input_path", help="path to input .json corpus")
    p.add_argument("result_path", help="path to .txt conll result to create")
    args = p.parse_args()
    convert(args.input_path, args.result_path)
