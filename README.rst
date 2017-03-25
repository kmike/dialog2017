Morphological Disambiguation for Russian language.
See https://github.com/dialogue-evaluation/morphoRuEval-2017.

Requirements
============

Scripts use Python 3.4+.
Install ``requirements.txt`` using pip.


Data preparation
================

To unify training data unpack it, then use ``python -m dialog2017.to_json``
to convert to JSON. For OpenCorpora export it should be called
with "--opencorpora" flag::

    python -m dialog2017.to_json ../morphoRuEval-2017/train/RNCgoldInUD_Morpho.conll data/rnc.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/gikrya_fixed.txt data/gikrya.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/syntagrus_full_fixed.ud data/syntagrus.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/unamb_sent_14_6.conllu data/opencorpora.json --opencorpora

To convert JSON data back to CONLL format use ``dialog2017.to_conll`` script, e.g.::

    python -m dialog2017.to_conll data/gikrya.json data/gikrya.txt

Evaluation
==========

Alternative evaluation script::

    python -m dialog2017.evaluate corpus_gold.txt corpus_pred.txt

It works both with CONLL and JSON corpora and allows to print errors.
Metrics are the same. Lemmatization quality measurment is not implemented yet.

pymorphy2 baseline
==================

``python -m dialog2017.pymorphy2_baseline`` script takes first pymorphy2
prediction and converts resulting tag to Dialog 2017 format.

::

    $ python -m dialog2017.pymorphy2_baseline ../morphoRuEval-2017/Baseline/source/gikrya_test.txt ./data/gikrya-pred-test.txt
    reading...
    parsing...
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 20787/20787 [00:05<00:00, 4022.44it/s]
    saving...
    evaluating...
    130443 out of 171550 (skipped: 98714); accuracy: 76.04%

    $ python -m dialog2017.pymorphy2_baseline ../morphoRuEval-2017/Baseline/source/syntagrus_test.txt ./data/syntagrus-pred-test.txt
    reading...
    parsing...
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 12529/12529 [00:05<00:00, 2475.93it/s]
    saving...
    evaluating...
    109688 out of 146817 (skipped: 85066); accuracy: 74.71%

    $ python -m dialog2017.pymorphy2_baseline ./data/opencorpora.txt ./data/opencorpora-pred.txt
    reading...
    parsing...
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 38508/38508 [00:09<00:00, 4184.98it/s]
    saving...
    evaluating...
    224714 out of 270063 (skipped: 187520); accuracy: 83.21%

    $ python -m dialog2017.pymorphy2_baseline ./data/rnc.txt ./data/rnc-pred.txt
    reading...
    parsing...
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 98892/98892 [00:15<00:00, 6233.93it/s]
    saving...
    evaluating...
    544275 out of 797823 (skipped: 547467); accuracy: 68.22%


CRF baseline
============

This is a "obvious" CRF-based baseline: features are grammemes extracted using
pymorphy2 + words themselves + grammemes of nearby words + nearby words;
output tags are just tags as-is (so there is ~300 output labels).

::

    python -m dialog2017.crf_baseline \
        ../morphoRuEval-2017/Baseline/source/gikrya_train.txt \
        ../morphoRuEval-2017/Baseline/source/gikrya_test.txt \
        ./data/gikrya-pred-test-crf.txt \
        model.joblib
    <..snip..>
    evaluating...
    evaluated 171550 tokens out of 270264 (63.47%)
    full tags: 162213 correct; accuracy=94.56%
    POS: 169297 correct; accuracy=98.69%
