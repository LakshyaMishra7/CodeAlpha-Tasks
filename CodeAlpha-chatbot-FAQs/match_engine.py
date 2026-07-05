"""
match_engine.py
Matches a learner's question against the FAQ bank using TF-IDF vectors and
cosine similarity, with basic NLTK preprocessing (tokenising, stopword
removal, lemmatising).
"""

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from faq_data import FAQS


class StudyDeskEngine:
    """Finds the closest-matching FAQ for a free-text question."""

    MATCH_THRESHOLD = 0.16   # below this, we admit we don't know

    def __init__(self):
        self._lemmatizer = WordNetLemmatizer()
        self._stopwords = set(stopwords.words("english"))
        self.questions = [q for q, _ in FAQS]
        self.answers = [a for _, a in FAQS]
        self._vectorizer = TfidfVectorizer(
            preprocessor=self._clean,
            ngram_range=(1, 2),
            min_df=1,
        )
        self._matrix = self._vectorizer.fit_transform(self.questions)

    def _clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = word_tokenize(text)
        kept = [
            self._lemmatizer.lemmatize(tok)
            for tok in tokens
            if tok not in self._stopwords and len(tok) > 1
        ]
        return " ".join(kept)

    def ask(self, question: str):
        """Returns (answer_text, confidence_0_to_1_or_None, matched_question_or_None)."""
        if not question.strip():
            return "Write a question in the box and I'll look it up.", None, None

        vec = self._vectorizer.transform([question])
        scores = cosine_similarity(vec, self._matrix).flatten()
        best_i = int(np.argmax(scores))
        best_score = float(scores[best_i])

        if best_score < self.MATCH_THRESHOLD:
            return (
                "That one's not in my notes yet. Try rephrasing it, or pick a "
                "topic tab on the left — I currently cover LLM basics, model "
                "internals, prompting/fine-tuning, and safety/agents.",
                None,
                None,
            )
        return self.answers[best_i], best_score, self.questions[best_i]

    def top_matches(self, question: str, k: int = 3):
        """Returns up to k (question, score) pairs, best first, for suggestions."""
        vec = self._vectorizer.transform([question])
        scores = cosine_similarity(vec, self._matrix).flatten()
        order = np.argsort(scores)[::-1][:k]
        return [(self.questions[i], float(scores[i])) for i in order if scores[i] > 0]


if __name__ == "__main__":
    engine = StudyDeskEngine()
    for q in [
        "what is an llm",
        "explain hallucination",
        "how does rag work",
        "difference between gpt and bert",
        "explain quantum computing",
    ]:
        answer, score, matched = engine.ask(q)
        pct = f"{score*100:.0f}%" if score else "—"
        print(f"\nQ: {q}\nmatched: {matched}\nA ({pct}): {answer[:90]}...")