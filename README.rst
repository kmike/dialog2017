Morphological Disambiguation for Russian language.
See https://github.com/dialogue-evaluation/morphoRuEval-2017.

Data preparation
================

To unify training data unpack it, then use ``scripts/to_json.py`` to convert
to json. For OpenCorpora export it should be called with --opencorpora flag::

    python -m dialog2017.to_json ../morphoRuEval-2017/train/RNCgoldInUD_Morpho.conll data/rnc.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/gikrya_fixed.txt data/gikrya.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/syntagrus_full_fixed.ud data/syntagrus.json
    python -m dialog2017.to_json ../morphoRuEval-2017/train/unamb_sent_14_6.conllu data/opencorpora.json --opencorpora
