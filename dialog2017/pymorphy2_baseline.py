# -*- coding: utf-8 -*-
"""
Simple pymorphy2 baseline: no context-based disabmiguation.
"""
from __future__ import absolute_import
import argparse

from tqdm import tqdm
import pymorphy2
from pymorphy2.shapes import is_punctuation
from pymorphy2.cache import memoized_with_single_argument
from russian_tagsets import dialog2017

from dialog2017 import conll, evaluate
from dialog2017.utils import write_json


def _normalized_for_gikrya(p):
    # Если действовать по ГИКРЯ, то
    # причастия надо нормализовывать в причастия.
    # в OpenCorpora и НКРЯ - в глагол.
    if p.tag.POS in {'PRTS', 'PRTF'}:
        return p.inflect({'PRTF', 'sing', 'masc', 'nomn'})

    # todo: он/она/они
    return p.normalized


def _pymorphy2_to_dialog(p, word):
    pos, tag = dialog2017.from_opencorpora(str(p.tag), word).split()
    norm = _normalized_for_gikrya(p)
    return word, norm.word, pos, conll.parse_tag(tag)


def pymorphy2_best_parse(morph, word):
    word_orig = word
    if word.endswith('.') and not is_punctuation(word):
        word = word[:-1]  # abbreviation
    return _pymorphy2_to_dialog(morph.parse(word)[0], word_orig)


def parse_corpus(sents):
    morph = pymorphy2.MorphAnalyzer()

    @memoized_with_single_argument({})
    def parse(word):
        return pymorphy2_best_parse(morph, word)

    return [[parse(row[0]) for row in sent] for sent in tqdm(sents)]


def main(path_gold, path_pred):
    print("reading...")
    sents_gold = conll.read_sents(path_gold)
    print("parsing...")
    sents_pred = parse_corpus(sents_gold)
    print("saving...")
    if path_pred.endswith('.json'):
        write_json(sents_pred, path_pred)
    else:
        conll.write_sents(sents_pred, path_pred)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("path_gold", help="path to a file in conll or json format")
    p.add_argument("path_pred", help="path to a file to be created")
    p.add_argument("--no-eval", help="don't run evaluation", default=False)
    args = p.parse_args()
    main(args.path_gold, args.path_pred)

    if not args.no_eval:
        print("evaluating...")
        evaluate.main(args.path_gold, args.path_pred, 0)
