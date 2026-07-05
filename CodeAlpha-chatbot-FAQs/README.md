# StudyDesk — Chatbot for FAQs (Task 2)

A desktop FAQ chatbot for **Generative AI & Large Language Models** (LLM
basics, model internals, prompting/fine-tuning, safety/agents) built with
Python + Tkinter. It matches a learner's free-text question against a
curated FAQ bank using **TF-IDF vectors + cosine similarity**, the same NLP
technique the task brief calls for.

## Files
- `faq_data.py` — 25 original Q&A pairs on generative AI & LLMs.
- `match_engine.py` — NLTK preprocessing (tokenise, stopword removal,
  lemmatise) + scikit-learn TF-IDF/cosine-similarity matching.
- `studydesk_app.py` — the Tkinter desktop UI: a notebook / index-card themed
  chat window with sidebar topic tabs, sticky-note style chat bubbles, and a
  pencil-style confidence meter.
- `requirements.txt` — Python dependencies.

## How it maps to the task brief
| Brief requirement | Where it's handled |
|---|---|
| Collect FAQs (Q&A pairs) | `faq_data.py` |
| Preprocess text (NLTK) | `match_engine.py: _clean()` |
| Match via cosine similarity | `match_engine.py: ask()` |
| Display best matching answer | `studydesk_app.py: _post_bot_note()` |
| Simple chat UI (optional) | `studydesk_app.py` (full desktop chat window) |

## Run it
bash
pip install -r requirements.txt
python studydesk_app.py

On first run, NLTK will silently download the small `punkt`, `stopwords`,
and `wordnet` corpora it needs.

## Design notes
 it's a warm-paper notebook theme — graph-paper backdrop, ruled separators, sticky-note
chat bubbles (blue for you, yellow for StudyDesk), and topic tabs styled like
binder index cards down the left side (LLM Basics, Model Internals, Prompting
& Tuning, Safety & Agents). Clicking a tab fires off a sample question for
that section; typing your own question works the same way.