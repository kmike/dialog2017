#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import codecs
import argparse

import tqdm

from dialog2017 import conll


def convert(input_path, output_path):
    print("reading json corpus...")
    with codecs.open(input_path, 'r', encoding='utf8') as f:
        sents = json.load(f)

    print("converting to conll format...")
    with codecs.open(output_path, 'w', encoding='utf8') as f:
        for sent in tqdm.tqdm(sents, unit=' sentences'):
            for idx, (word, lemma, pos, tags) in enumerate(sent, start=1):
                line = conll.conll_line(idx, word, lemma, pos, tags)
                f.write(line+"\n")
            f.write("\n")
    print("done.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("input_path", help="path to input .json corpus")
    p.add_argument("result_path", help="path to .txt conll result to create")
    args = p.parse_args()
    convert(args.input_path, args.result_path)
