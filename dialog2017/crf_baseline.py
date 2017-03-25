# -*- coding: utf-8 -*-
import json
from pathlib import Path
from itertools import chain
import argparse

import joblib
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_predict
from tqdm import tqdm
from pymorphy2 import MorphAnalyzer
from pymorphy2.cache import memoized_with_single_argument
from morphine import features
from morphine.feature_extractor import FeatureExtractor
from sklearn_crfsuite import CRF

from dialog2017 import conll, evaluate

_cache = {}

morph = MorphAnalyzer()


class TaggerFeatureExtractor(FeatureExtractor):
    IGNORE = set()

    def __init__(self):
        super(TaggerFeatureExtractor, self).__init__(
            token_features=[
                features.bias,
                features.token_lower,
                features.Grammeme(threshold=0.01, add_unambig=True, ignore=self.IGNORE),
                # features.GrammemePair(threshold=0.0, add_unambig=True, ignore=self.IGNORE),
            ],
            global_features=[
                features.sentence_start,
                features.sentence_end,

                features.Pattern([-1, 'token_lower']),
                features.Pattern([-2, 'token_lower']),

                features.Pattern([-1, 'Grammeme']),
                features.Pattern([+1, 'Grammeme']),

                # features.Pattern([-2, 'Grammeme'], [-1, 'Grammeme']),
                # features.Pattern([-1, 'Grammeme'], [0, 'Grammeme']),
                # features.Pattern([-1, 'Grammeme'], [0, 'GrammemePair']),
                #
                # features.Pattern([-1, 'GrammemePair']),
                # features.Pattern([+1, 'GrammemePair']),
            ],
        )


# def flatten_result(X):
#     return [ItemSequence(xseq).items() for xseq in X]


@memoized_with_single_argument(_cache)
def parse_token(tok):
    return morph.parse(tok)


def parse_sent(morph, sent):
    tokens = [r[0] for r in sent]
    parsed_tokens = [parse_token(tok) for tok in tokens]
    return tokens, parsed_tokens


def parse_corpus(morph, sents):
    return [parse_sent(morph, sent) for sent in tqdm(sents)]


def flatten(s):
    return list(chain.from_iterable(s))


def join_tag(pos, tags):
    return "%s %s" % (pos, conll.tag2conll(tags))


def get_y(corpus):
    return [[join_tag(r[2], r[3]) for r in sent] for sent in corpus]


def parse_tag_str(tag_str):
    pos, tags = tag_str.split()
    return pos, conll.parse_tag(tags)


def load_corpus(path, take_first=0):
    corpus = conll.read_sents(path)
    if take_first:
        corpus = corpus[:take_first]
    X_raw = parse_corpus(morph, corpus)
    y = get_y(corpus)
    return corpus, X_raw, y


def y_pred_to_sents_pred(sents_gold, y_pred):
    return [
        [
            [r[0], r[1], *parse_tag_str(tag)]
            for (r, tag) in zip(s, yseq)
        ]
        for (s, yseq) in zip(sents_gold, y_pred)
    ]


def main(path_train, path_test, path_pred, path_crf, take_first, dev_size):
    print("loading train corpus..")
    _, X_raw, y = load_corpus(path_train, take_first=take_first)
    print("extracting features from train corpus..")
    fe = TaggerFeatureExtractor()
    X = fe.fit_transform(tqdm(X_raw))
    print("training..")
    crf = CRF(algorithm='ap', verbose=True, max_iterations=10)
    if dev_size:
        X, X_dev, y, y_dev = train_test_split(X, y, test_size=dev_size)
    else:
        X_dev, y_dev = None, None
    crf.fit(X, y, X_dev, y_dev)

    print("saving..")
    joblib.dump({'fe': fe, 'crf': crf}, path_crf, compress=2)

    print("loading test corpus..")
    corpus, X_test_raw, y_test = load_corpus(path_test)
    print("extracting features from test corpus..")
    X_test = fe.transform(X_test_raw)
    print("predicting..")
    y_pred = crf.predict(tqdm(X_test))

    print("saving results..")
    sents_pred = y_pred_to_sents_pred(corpus, y_pred)
    conll.write_sents(sents_pred, path_pred)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("path_train", help="path to a training corpus file in conll or json format")
    p.add_argument("path_test", help="path to a testing corpus file in conll or json format")
    p.add_argument("path_pred", help="path to a corpus file to be created")
    p.add_argument("path_crf", help="path to a model file to be created, "
                                    "e.g. model.joblib")
    p.add_argument("--take-first", type=int, default=0,
                   help="use only first N sentences. 0 => 'use all sentences'.")
    p.add_argument("--dev-size", type=float, default=0.0)
    p.add_argument("--no-eval", type=bool, default=False)
    args = p.parse_args()
    main(
        path_train=args.path_train,
        path_test=args.path_test,
        path_pred=args.path_pred,
        path_crf=args.path_crf,
        take_first=args.take_first,
        dev_size=args.dev_size
    )

    if not args.no_eval:
        print("evaluating...")
        evaluate.main(args.path_test, args.path_pred)
