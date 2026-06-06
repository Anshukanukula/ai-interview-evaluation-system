# modules/text_analysis.py
import json
import re
import spacy
from textblob import TextBlob

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    t = text.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def keyword_score(transcript, keywords):
    """
    Compute fraction of keywords mentioned.
    keywords: list of strings
    """
    text = clean_text(transcript)
    found = 0
    for kw in keywords:
        if kw.lower() in text:
            found += 1
    if len(keywords) == 0:
        return 0.0
    return found / len(keywords)

def clarity_score(transcript):
    """
    Very simple clarity metric: use average sentence length and noun/verb ratio as proxy.
    Returns 0..1
    """
    doc = nlp(transcript)
    sents = list(doc.sents)
    if len(sents) == 0:
        return 0.5
    avg_sent_len = sum(len(s) for s in sents) / len(sents)
    # ideal avg sentence length ~ 10-20 words; score decreased outside
    if avg_sent_len <= 10:
        sent_score = avg_sent_len / 10
    elif avg_sent_len <= 20:
        sent_score = 1.0
    else:
        sent_score = max(0.0, 1.0 - ((avg_sent_len - 20) / 40))
    # sentiment polarity as proxy for clarity (neutral is often clearer)
    blob = TextBlob(transcript)
    polarity = abs(blob.sentiment.polarity)  # 0..1
    # prefer moderate polarity -> map to clarity penalty
    polarity_penalty = min(1.0, polarity)
    # combine
    score = 0.7 * sent_score + 0.3 * (1 - polarity_penalty)
    return max(0.0, min(1.0, score))
