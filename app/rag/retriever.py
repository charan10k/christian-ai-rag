import re
import math
from collections import defaultdict

import pandas as pd

_bible_df = None
_index = None       # inverted index: term -> list of (doc_id, tf)
_doc_texts = None   # doc_id -> {"text": str, "citation": str}
_doc_count = 0

TEXT_COLUMN = "king_james_bible_kjv"

STOPWORDS = {
    "what", "does", "the", "say", "about", "is", "a", "an", "of",
    "to", "in", "for", "and", "or", "but", "that", "this", "it",
    "be", "are", "was", "were", "he", "she", "his", "her", "they",
    "their", "have", "has", "had", "with", "from", "how", "do",
    "did", "me", "my", "i", "we", "you", "your", "us", "can",
    "tell", "give", "show", "where", "which", "when", "who",
}

SYNONYMS = {
    "forgiveness": ["forgive", "forgiven", "merciful", "mercy", "pardon", "remission"],
    "love":        ["charity", "beloved", "loveth", "lovest", "affection", "compassion"],
    "faith":       ["believe", "belief", "trust", "confidence", "hope", "assurance"],
    "prayer":      ["pray", "praying", "supplicate", "supplication", "petition", "intercede"],
    "salvation":   ["save", "saved", "saviour", "redeemed", "redemption", "eternal life"],
    "sin":         ["iniquity", "trespass", "transgression", "wickedness", "evil", "unrighteous"],
    "peace":       ["shalom", "rest", "comfort", "tranquil", "quiet", "still"],
    "strength":    ["mighty", "power", "strong", "courage", "bold", "steadfast"],
    "wisdom":      ["understanding", "knowledge", "discernment", "prudence", "insight"],
    "fear":        ["afraid", "dread", "reverence", "tremble", "awe"],
    "joy":         ["rejoice", "gladness", "delight", "blessed", "happiness"],
    "grace":       ["favour", "favor", "gift", "mercy", "unmerited"],
    "truth":       ["righteous", "just", "honest", "faithful", "verily"],
    "holy":        ["sacred", "sanctify", "consecrate", "divine", "pure"],
    "death":       ["die", "grave", "perish", "mortal", "eternal"],
    "resurrection": ["rise", "risen", "raised", "alive", "resurrected"],
    "baptism":     ["baptize", "baptised", "water", "born again"],
    "anxiety":     ["worry", "fear", "troubled", "distress", "cast your care"],
    "anger":       ["wrath", "furious", "rage", "slow to anger", "indignation"],
    "humility":    ["humble", "meek", "lowly", "servant"],
    "money":       ["wealth", "riches", "treasure", "mammon", "gold", "silver"],
    "hope":        ["expectation", "wait", "trust", "confident", "assurance"],
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r'\w+', text.lower())


def _expand(words: list[str]) -> list[str]:
    out = []
    for w in words:
        if w not in STOPWORDS:
            out.append(w)
            if w in SYNONYMS:
                out.extend(SYNONYMS[w])
    return out


def _build_index():
    global _bible_df, _index, _doc_texts, _doc_count
    _bible_df = pd.read_csv("data/AlamoPolyglot.csv")

    _index = defaultdict(list)
    _doc_texts = {}

    valid_rows = _bible_df[_bible_df[TEXT_COLUMN].notna()].reset_index(drop=True)
    _doc_count = len(valid_rows)

    for doc_id, row in valid_rows.iterrows():
        text = str(row[TEXT_COLUMN])
        citation = f'{row["book_name"]} {row["chapter"]}:{row["verse"]}'
        tokens = _tokenize(text)
        tf = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        _doc_texts[doc_id] = {"text": text, "citation": citation}
        for term, count in tf.items():
            _index[term].append((doc_id, count))


def _get_index():
    if _index is None:
        _build_index()
    return _index, _doc_texts, _doc_count


def clean_query(query: str) -> list[str]:
    return _expand(_tokenize(query))


def retrieve_scriptures(query: str, top_k: int = 5) -> list[dict]:
    index, doc_texts, N = _get_index()
    query_terms = clean_query(query)

    scores: dict[int, float] = defaultdict(float)

    for term in set(query_terms):
        postings = index.get(term, [])
        df = len(postings)
        if df == 0:
            continue
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
        for doc_id, tf in postings:
            # BM25 k1=1.5, b=0.75, avgdl approximated as 10 tokens
            k1, b, avgdl = 1.5, 0.75, 10
            doc_len = len(_tokenize(doc_texts[doc_id]["text"]))
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avgdl))
            scores[doc_id] += idf * tf_norm

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        {
            "score": round(score, 4),
            "text": doc_texts[doc_id]["text"],
            "citation": doc_texts[doc_id]["citation"],
        }
        for doc_id, score in ranked
    ]
