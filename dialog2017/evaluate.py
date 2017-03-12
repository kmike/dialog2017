# -*- coding: utf-8 -*-
""" Evaluation utilities """
import argparse
from typing import Dict, List

from . import conll


POS_TO_MEASURE = ["NOUN", "ADV", "PRON", "DET", "ADJ", "VERB", "NUM"]
DOUBT_ADVERBS = {"как", "когда", "пока", "так", "где"}
CATS_TO_MEASURE = {
    "NOUN": {"Gender", "Number", "Case"},
    "ADJ": {"Gender", "Number", "Case", "Variant", "Degree"},
    "PRON": {"Gender", "Number", "Case"},
    "DET": {"Gender", "Number", "Case"},
    "VERB": {"Gender", "Number", "VerbForm", "Mood", "Tense"},
    "ADV": {"Degree"},
    "NUM": {"Gender", "Number", "Case", "NumForm"},
}


def simplify_pos(pos: str) -> str:
    if pos == 'PROPN':
        pos = 'NOUN'
    return pos


def simplify_tags(
        pos: str,
        tags: Dict[str, str],
    ) -> Dict[str, str]:
    tags = tags.copy()
    cats_to_measure = CATS_TO_MEASURE.get(pos, set())
    for g in list(tags.keys()):
        if g not in cats_to_measure:
            del tags[g]

    # if pos == 'VERB' and tags.get('Tense') in {'Pres', 'Fut'}:
    #     tags['Tense'] = 'Notpast'

    if tags.get('Variant') == 'Short':
        tags['Variant'] = 'Brev'

    return tags


def should_match_parses(
        word: str,
        pos_gold: str,
        tags_gold: Dict[str, str],
    ) -> bool:
    pos = simplify_pos(pos_gold)
    if pos not in POS_TO_MEASURE:
        return False
    if pos == 'ADV' and word.lower() in DOUBT_ADVERBS:
        return False
    return True


def parses_match(
        word: str,
        pos_gold: str,
        tags_gold: Dict[str, str],
        pos_pred: str,
        tags_pred: Dict[str, str],
        verbose: bool,
    ) -> bool:
    if not should_match_parses(word, pos_gold, tags_gold):
        return True

    pos_gold = simplify_pos(pos_gold)
    pos_pred = simplify_pos(pos_pred)

    if pos_gold != pos_pred:
        if verbose:
            print("%s: %s != %s" % (word, pos_gold, pos_pred))
        return False

    tags_gold = simplify_tags(pos_gold, tags_gold)
    tags_pred = simplify_tags(pos_pred, tags_pred)

    if tags_gold == tags_pred:
        return True

    if set(tags_gold.values()) <= set(tags_pred.values()):
        # this is how official script works - extra tags are allowed
        # in prediction result
        return True

    if verbose:
        print("%s (%s): %s != %s, diff=%r" % (
            word, pos_gold, tags_gold, tags_pred,
            set(tags_gold.items()) ^ set(tags_pred.items())
        ))
    return False


def rows_match(row_gold: List, row_pred: List, verbose: bool=False) -> bool:
    assert row_gold[0] == row_pred[0]
    return parses_match(
        word=row_gold[0],
        pos_gold=row_gold[2],
        tags_gold=row_gold[3],
        pos_pred=row_pred[2],
        tags_pred=row_pred[3],
        verbose=verbose,
    )


def should_match_rows(row_gold: List, row_pred: List) -> bool:
    assert row_gold[0] == row_pred[0]
    return should_match_parses(
        word=row_gold[0],
        pos_gold=row_gold[2],
        tags_gold=row_gold[3],
    )


def measure_sents(sents_gold: List[List], sents_pred: List[List],
                  verbose_max_errors=0):
    measured, total, correct = 0, 0, 0

    for sent_gold, sent_pred in zip(sents_gold, sents_pred):
        for row_gold, row_pred in zip(sent_gold, sent_pred):
            total += 1
            if should_match_rows(row_gold, row_pred):
                measured += 1
                verbose = (measured - correct) <= verbose_max_errors
                if rows_match(row_gold, row_pred, verbose=verbose):
                    correct += 1

    return measured, total, correct


def measure_conll(path_gold: str, path_pred: str, verbose_max_errors=0):
    sents_gold = conll.read_sents(path_gold)
    sents_pred = conll.read_sents(path_pred)
    assert len(sents_gold) == len(sents_pred)
    return measure_sents(sents_gold, sents_pred, verbose_max_errors)


def main(path_gold, path_pred, n_errors):
    measured, total, correct = measure_conll(path_gold, path_pred,
                                             verbose_max_errors=n_errors)
    print("{} out of {} (skipped: {}); accuracy: {:.2%}".format(
        correct, measured, total-measured, correct / measured
    ))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("path_gold", help="path to a file in conll or json format")
    p.add_argument("path_pred", help="path to a file in conll or json format")
    p.add_argument("--n-errors", default=0, type=int,
                   help="print first N errors")
    args = p.parse_args()
    main(args.path_gold, args.path_pred, args.n_errors)
