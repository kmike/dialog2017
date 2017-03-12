# -*- coding: utf-8 -*-
"""
Module with utilities for reading dialog2017 annotated corpora.

Parse a corpus::
    
    sents = read_sents('corpus.txt')
    
"""
import codecs

from .utils import read_json, read_lines


def read_sents(path, opencorpora=False):
    if path.endswith(".json"):
        return read_json(path)
    else:
        return read_sents_conll(path, opencorpora=opencorpora)


def read_sents_conll(path, opencorpora=False):
    corpus_lines = read_lines(path)
    sents_iter = iter_sentences(corpus_lines, opencorpora)
    return list(sents_iter)


def is_token_line(line):
    if not line.strip():
        return False
    if line == "==newfile==" or line.startswith("==>"):
        # see https://github.com/dialogue-evaluation/morphoRuEval-2017/issues/5
        return False
    return True


def parse_tag(tag):
    tags_list = tag.split("|") if tag != "_" else []
    return dict(t.split("=") for t in tags_list)


def to_token(line, opcorpora=False):
    parts = line.split('\t')[1:]
    if opcorpora:
        # see https://github.com/dialogue-evaluation/morphoRuEval-2017/issues/5
        parts = parts[:3] + parts[4:5]
    parts[1] = parts[1]  # lemma
    parts[3] = parse_tag(parts[3])  # tag
    # parts[4] = parse_tag(parts[4])  # extra tags
    return parts[:4]


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


def tag2conll(parts):
    if not parts:
        parts = "_"
    elif isinstance(parts, (list, tuple)):
        parts = "|".join(parts)
    elif isinstance(parts, dict):
        parts = "|".join("%s=%s" % (k, v) for (k, v) in sorted(parts.items()))
    return parts


def conll_line(idx, word, lemma, pos, tags):
    return "\t".join([str(idx), word, lemma, pos, tag2conll(tags)])


def write_sents_to_file(sents, fp):
    """ Write sentences to a file ``fp`` in CONLL format """
    for sent in sents:
        for idx, (word, lemma, pos, tags) in enumerate(sent, start=1):
            line = conll_line(idx, word, lemma, pos, tags)
            fp.write(line+"\n")
        fp.write("\n")


def write_sents(sents, path):
    with codecs.open(path, 'w', encoding='utf8') as f:
        write_sents_to_file(sents, f)
