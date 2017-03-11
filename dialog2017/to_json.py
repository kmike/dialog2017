#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import codecs
import argparse

from dialog2017 import conll


def convert(input_path, output_path, opencorpora):
    print("reading & parsing...")
    sents = conll.read_sents(input_path, opencorpora=opencorpora)
    print("saving to json...")
    with codecs.open(output_path, 'w', encoding='utf8') as f:
        json.dump(sents, f, indent=2, ensure_ascii=False, sort_keys=True)
    print("done.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("input_path", help="path to an unpacked corpus file")
    p.add_argument("result_path", help="path to the .json result to create")
    p.add_argument("--opencorpora", help="apply a fix for opencorpora export",
                   action="store_true")
    args = p.parse_args()
    convert(args.input_path, args.result_path, args.opencorpora)
