# -*- coding: utf-8 -*-
"""
Module with utilities for reading dialog2017 annotated corpora.

Parse a corpus::

    corpus_lines = read_lines('corpus.txt')
    sents = list(iter_sentences(corpus_lines))
    
"""


def read_lines(name):
    with open(name, 'rb') as f:
        return f.read().decode('utf8').splitlines()


def is_token_line(line):
    if not line.strip():
        return False
    if line == "==newfile==" or line.startswith("==>"):
        # see https://github.com/dialogue-evaluation/morphoRuEval-2017/issues/5
        return False
    return True


def parse_tag(tag):
    return tag.split("|") if tag != "_" else []


def to_token(line, opcorpora=False):
    parts = line.split('\t')[1:]
    if opcorpora:
        # see https://github.com/dialogue-evaluation/morphoRuEval-2017/issues/5
        parts = parts[:3] + parts[4:5]
    parts[1] = parts[1]  # lemma
    parts[3] = parse_tag(parts[3])  # tag
    # parts[4] = parse_tag(parts[4])  # extra tags
    return parts


def iter_sentences(corpus, opencorpora=False):
    sent = []
    for line in corpus:
        if not is_token_line(line):
            if sent:
                yield sent
            sent = []
        else:
            try:
                sent.append(to_token(line, opencorpora))
            except Exception:
                print(line)
                raise
    if sent:
        yield sent


def conll_line(idx, word, lemma, pos, tags):
    if isinstance(tags, list):
        if tags:
            tags = "|".join(tags)
        else:
            tags = "_"
    return "\t".join([str(idx), word, lemma, pos, tags])
