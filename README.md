# CodeAlpha — Artificial Intelligence Internship Tasks

**Author:** Lakshya Mishra
**Internship:** CodeAlpha — Artificial Intelligence Internship
**Repository:** [github.com/LakshyaMishra7](https://github.com/LakshyaMishra7)

This repository holds three independent projects built for the CodeAlpha AI
internship task list. Each one lives in its own folder with its own
dependencies and its own README — this file is a map of the whole
repository: what each project is, what it's built with, and how to run it.

```
CodeAlpha-Tasks/
├── CodeAlpha_Language_Translation_Tool/   → Task 1: Language Translation Tool
├── CodeAlpha_Chatbot_FAQS/                → Task 2: Chatbot for FAQs
└── CodeAlpha_Object_Tracking/             → Task 4: Object Detection & Tracking
```

---

## Task 1 — Language Translation Tool · "Postscript"
📁 `CodeAlpha_Language_Translation_Tool/`

A browser-based translator built around a small post-office / airmail
theme — you write a message, address it "from" one language "to" another,
send it, and it comes back translated with an animated postmark stamped on
it.

**Tech stack:** plain HTML, CSS, and JavaScript — no build step, no
framework, no dependencies. Translation is handled by the free **MyMemory
Translation API** (no key required).

**Highlights**
- Text input with source/target language selection across 45+ languages,
  plus auto-detect for the source language.
- One-click language swap and a live character counter.
- Translated text arrives with an animated postmark showing the
  source/target language and date.
- Copy-to-clipboard and text-to-speech playback for both original and
  translated text.
- A "Recently sent" strip of the last few translations, styled as little
  postcards you can click to reload.
- `Ctrl + Enter` keyboard shortcut to send.

**Run it:** open `index.html` directly in any browser — nothing to install.

---

## Task 2 — Chatbot for FAQs · "StudyDesk"
📁 `CodeAlpha_Chatbot_FAQS/`

A desktop FAQ chatbot covering **Generative AI & Large Language Models**
(LLM basics, model internals, prompting & fine-tuning, safety & agents),
styled like a warm-paper notebook — graph-paper backdrop, ruled separators,
and sticky-note style chat bubbles, with topic tabs down the side styled
like binder index cards.

**Tech stack:** Python + **Tkinter** for the desktop UI, **NLTK** for text
preprocessing (tokenising, stopword removal, lemmatising), and
**scikit-learn** for TF-IDF vectorisation + cosine-similarity matching
against the FAQ bank.

**Highlights**
- 25 original Q&A pairs covering LLMs, Transformers, attention, RAG,
  fine-tuning, RLHF, embeddings, tokenisation, quantisation, and more.
- Free-text question matching via TF-IDF + cosine similarity, with a
  confidence score shown per answer.
- Four topic tabs (LLM Basics, Model Internals, Prompting & Tuning,
  Safety & Agents) that fire a sample question when clicked.
- "Jotting a reply…" typing indicator and a pencil-style confidence meter.

**Run it:**
```bash
cd CodeAlpha_Chatbot_FAQS
pip install -r requirements.txt
python studydesk_app.py
```
NLTK will silently download the small `punkt`, `stopwords`, and `wordnet`
corpora it needs on first run.

---

## Task 4 — Object Detection & Tracking · "TrailScope"
📁 `CodeAlpha_Object_Tracking/`

A real-time object detection and multi-object tracking tool with a
viewfinder-style HUD: corner-bracket bounding boxes, fading motion trails
behind each tracked object, and a bottom dashboard with FPS, live object
count, and a mini bar-chart breakdown by class.

**Tech stack:** Python, **OpenCV** for video I/O and rendering, **YOLOv8**
(Ultralytics) for detection, and **ByteTrack** (Ultralytics' built-in
tracker) for persistent identity tracking across frames.

**Highlights**
- Works on a live webcam feed or any video file.
- Colours each bounding box by *tracked identity* rather than by class, so
  the same object keeps one colour for the whole clip.
- Optional class filtering (`--classes person,car`), annotated video export
  (`--save output.mp4`), and a detection-only mode (`--no-track`).
- Snapshot capture with the `S` key while the preview window is focused;
  `Q` to quit.

**Run it:**
```bash
cd CodeAlpha_Object_Tracking
pip install -r requirements.txt

# Webcam
python trailscope.py

# A video file
python trailscope.py --source sample.mp4
```
The first run auto-downloads the YOLOv8n weights (~6 MB) if they aren't
already present.

---

## Notes on originality

Each of these three projects was designed and built from scratch as its own
piece of work — its own visual identity, its own project structure, and (for
Task 2) its own original FAQ content — while still satisfying the same core
technical requirements set out in the CodeAlpha task brief for that task
(the UI/API flow for Task 1, the NLTK + cosine-similarity matching approach
for Task 2, and the YOLO + OpenCV + tracking pipeline for Task 4).

## Author

**Lakshya Mishra**
B.Tech Computer Science, Noida Institute of Engineering and Technology (NIET)
GitHub: [github.com/LakshyaMishra7](https://github.com/LakshyaMishra7)
