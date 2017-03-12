#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from dialog2017 import conll
from dialog2017.utils import write_json


def convert(input_path, output_path, opencorpora):
    print("reading & parsing...")
    sents = conll.read_sents_conll(input_path, opencorpora=opencorpora)
    print("saving to json...")
    write_json(sents, output_path)
    print("done.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("input_path", help="path to an unpacked corpus file")
    p.add_argument("result_path", help="path to the .json result to create")
    p.add_argument("--opencorpora", help="apply a fix for opencorpora export",
                   action="store_true")
    args = p.parse_args()
    convert(args.input_path, args.result_path, args.opencorpora)
