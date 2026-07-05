"""
studydesk_app.py
StudyDesk — a Generative AI & LLM FAQ helper styled like a notebook / index-card desk.
Theme: warm paper, ruled lines, highlighter accents, sticky-note chat bubbles.
Run with: python studydesk_app.py
"""

import tkinter as tk
import threading
import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from match_engine import StudyDeskEngine

# ── Palette: warm paper + highlighter accents ──────────────────────────────
PAPER        = "#F6F1E4"   # notebook page
PAPER_DARK   = "#EDE6D3"   # sidebar / recessed paper
RULE_BLUE    = "#C9DCE6"   # faint ruled line
MARGIN_RED   = "#D8846B"   # margin rule, used sparingly
INK          = "#2E2A24"   # main text, warm near-black
INK_SOFT     = "#8A8375"   # muted caption text
CARD_WHITE   = "#FFFDF6"   # index card surface

HILITE_YELLOW = "#F2C14E"  # bot accent (highlighter yellow)
HILITE_BLUE   = "#6FA3C7"  # user accent (highlighter blue)
TAB_GREEN     = "#7FA97A"  # topic tab accent
TAB_CORAL     = "#D8846B"
TAB_LILAC     = "#9B8AC4"
TAB_TEAL      = "#5FA3A0"

FONT_DISPLAY = ("Georgia", 19, "bold")
FONT_HEADING = ("Georgia", 12, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_NOTE    = ("Georgia", 11)
FONT_SMALL   = ("Segoe UI", 9)
FONT_TAG     = ("Consolas", 9, "bold")
FONT_INPUT   = ("Segoe UI", 11)


# ── Graph-paper backdrop ─────────────────────────────────────────────────────
class GraphPaper(tk.Canvas):
    """A quiet grid-lined page background, like a page torn from a workbook."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", PAPER)
        kw.setdefault("highlightthickness", 0)
        super().__init__(master, **kw)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("grid")
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        step = 26
        for x in range(0, w, step):
            self.create_line(x, 0, x, h, fill=RULE_BLUE, width=1, tags="grid")
        for y in range(0, h, step):
            self.create_line(0, y, w, y, fill=RULE_BLUE, width=1, tags="grid")
        self.create_line(46, 0, 46, h, fill=MARGIN_RED, width=1, tags="grid")
        self.tag_lower("grid")


# ── Hand-drawn-ish rule (separator) ─────────────────────────────────────────
class SketchRule(tk.Canvas):
    def __init__(self, master, color=INK_SOFT, **kw):
        kw.setdefault("height", 10)
        kw.setdefault("bg", kw.pop("panel_bg", PAPER))
        kw.setdefault("highlightthickness", 0)
        super().__init__(master, **kw)
        self._color = color
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("rule")
        w = self.winfo_width() or 400
        y = 5
        pts = []
        x = 0
        while x <= w:
            jitter = random.uniform(-1.4, 1.4)
            pts.extend([x, y + jitter])
            x += 14
        if len(pts) >= 4:
            self.create_line(*pts, fill=self._color, width=1.4, smooth=True, tags="rule")


# ── Confidence meter, drawn like a pencil-shaded bar ────────────────────────
class PencilMeter(tk.Canvas):
    def __init__(self, master, **kw):
        kw.setdefault("height", 10)
        kw.setdefault("bg", PAPER)
        kw.setdefault("highlightthickness", 0)
        super().__init__(master, **kw)
        self._pct = 0.0
        self.bind("<Configure>", lambda e: self.set(self._pct))

    def set(self, pct):
        self._pct = max(0.0, min(1.0, pct))
        self.delete("meter")
        w = self.winfo_width() or 200
        h = self.winfo_height() or 10
        self.create_rectangle(0, 0, w, h, outline=INK_SOFT, fill=PAPER_DARK, tags="meter")
        fill_w = int(w * self._pct)
        if fill_w > 0:
            color = TAB_GREEN if self._pct >= 0.4 else MARGIN_RED
            self.create_rectangle(0, 0, fill_w, h, outline="", fill=color, tags="meter")
            for x in range(0, fill_w, 5):
                self.create_line(x, 0, x, h, fill=PAPER, width=1, tags="meter")


# ── Typing indicator: three pencil taps ──────────────────────────────────────
class PencilTapping(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=PAPER)
        self._dots = []
        for _ in range(3):
            d = tk.Label(self, text="•", font=("Georgia", 16, "bold"), fg=INK_SOFT, bg=PAPER)
            d.pack(side=tk.LEFT, padx=2)
            self._dots.append(d)
        self._running = False

    def start(self):
        self._running = True
        self._animate(0)

    def stop(self):
        self._running = False

    def _animate(self, i):
        if not self._running:
            return
        for j, d in enumerate(self._dots):
            d.config(fg=INK if j == i % 3 else INK_SOFT)
        self.after(280, lambda: self._animate(i + 1))


# ── Scrollable notebook page for the conversation ───────────────────────────
class NotebookScroll(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=PAPER, **kw)
        self.canvas = GraphPaper(self, highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 troughcolor=PAPER_DARK, bg=PAPER_DARK)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.canvas, bg=PAPER)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_scroll)

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._win, width=event.width)

    def _on_scroll(self, event):
        self.canvas.yview_scroll(int(-event.delta / 40), "units")

    def scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)


# ── Main application ─────────────────────────────────────────────────────────
class StudyDeskApp(tk.Tk):
    TOPICS = [
        ("LLM Basics", "What is a large language model?", TAB_TEAL),
        ("Model Internals", "How does the attention mechanism work?", TAB_LILAC),
        ("Prompting & Tuning", "What is prompt engineering?", TAB_CORAL),
        ("Safety & Agents", "What is RLHF or reinforcement learning from human feedback?", TAB_GREEN),
    ]

    def __init__(self):
        super().__init__()
        self.title("StudyDesk — Gen AI & LLM FAQ Helper")
        self.geometry("1180x760")
        self.minsize(880, 560)
        self.configure(bg=PAPER)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.engine = StudyDeskEngine()
        self.msg_count = 0
        self.confidence_total = 0.0
        self.confidence_hits = 0

        self._build_sidebar()
        self._build_main()

        self._post_bot_note(
            "Hi, I'm StudyDesk. Ask me anything about large language models, "
            "generative AI, or how these systems are built and trained — or tap a "
            "tab on the left for a starter question.",
            confidence=None, matched=None,
        )

    # ── Sidebar: binder tabs + stats ────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self, bg=PAPER_DARK, width=260)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        head = tk.Frame(sb, bg=PAPER_DARK, pady=22)
        head.pack(fill=tk.X)
        tk.Label(head, text="\U0001F4D6  StudyDesk", font=FONT_DISPLAY,
                 fg=INK, bg=PAPER_DARK).pack(padx=18, anchor="w")
        tk.Label(head, text="GEN AI & LLM FAQ HELPER", font=FONT_TAG,
                 fg=INK_SOFT, bg=PAPER_DARK).pack(padx=18, anchor="w", pady=(2, 0))

        SketchRule(sb, panel_bg=PAPER_DARK).pack(fill=tk.X, padx=16, pady=6)

        tk.Label(sb, text="OPEN A TAB", font=FONT_TAG, fg=INK_SOFT,
                 bg=PAPER_DARK).pack(anchor="w", padx=18, pady=(6, 4))

        for label, sample_q, color in self.TOPICS:
            self._make_tab(sb, label, sample_q, color)

        SketchRule(sb, panel_bg=PAPER_DARK).pack(fill=tk.X, padx=16, pady=10)

        stats = tk.Frame(sb, bg=PAPER_DARK)
        stats.pack(fill=tk.X, padx=18)
        tk.Label(stats, text="NOTES FILED", font=FONT_TAG, fg=INK_SOFT,
                 bg=PAPER_DARK).grid(row=0, column=0, sticky="w")
        self.count_label = tk.Label(stats, text="0", font=FONT_HEADING,
                                     fg=TAB_TEAL, bg=PAPER_DARK)
        self.count_label.grid(row=1, column=0, sticky="w", pady=(0, 10))

        tk.Label(stats, text="AVG. CONFIDENCE", font=FONT_TAG, fg=INK_SOFT,
                 bg=PAPER_DARK).grid(row=2, column=0, sticky="w")
        self.avg_label = tk.Label(stats, text="—", font=FONT_HEADING,
                                   fg=TAB_CORAL, bg=PAPER_DARK)
        self.avg_label.grid(row=3, column=0, sticky="w")

        tk.Label(sb, text="4 sections indexed · 25 notes\nLLMs · Techniques · Internals · Ecosystem",
                 font=FONT_SMALL, fg=INK_SOFT, bg=PAPER_DARK, justify="left"
                 ).pack(side=tk.BOTTOM, anchor="w", padx=18, pady=18)

    def _make_tab(self, parent, label, sample_q, color):
        card = tk.Frame(parent, bg=CARD_WHITE, highlightthickness=1,
                         highlightbackground=color)
        card.pack(fill=tk.X, padx=14, pady=4)

        stripe = tk.Frame(card, bg=color, width=5)
        stripe.pack(side=tk.LEFT, fill=tk.Y)

        body = tk.Frame(card, bg=CARD_WHITE)
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
        tk.Label(body, text=label, font=FONT_HEADING, fg=INK, bg=CARD_WHITE,
                 anchor="w").pack(anchor="w")
        tk.Label(body, text=sample_q, font=FONT_SMALL, fg=INK_SOFT, bg=CARD_WHITE,
                 anchor="w", wraplength=170, justify="left", cursor="hand2"
                 ).pack(anchor="w", pady=(2, 0))

        def _enter(e):
            card.config(bg="#FFFFFF")
            body.config(bg="#FFFFFF")
            for w in body.winfo_children():
                w.config(bg="#FFFFFF")
        def _leave(e):
            card.config(bg=CARD_WHITE)
            body.config(bg=CARD_WHITE)
            for w in body.winfo_children():
                w.config(bg=CARD_WHITE)

        for w in (card, stripe, body, *body.winfo_children()):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", lambda e, q=sample_q: self._send(q))

    # ── Main notebook page ───────────────────────────────────────────────────
    def _build_main(self):
        main = tk.Frame(self, bg=PAPER)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(2, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = tk.Frame(main, bg=PAPER, pady=14)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="Today's page: Generative AI & LLM Q&A",
                 font=FONT_HEADING, fg=INK, bg=PAPER).pack(side=tk.LEFT, padx=18)
        tk.Label(header, text="clear page", font=FONT_SMALL, fg=HILITE_BLUE,
                 bg=PAPER, cursor="hand2").pack(side=tk.RIGHT, padx=18)
        header.winfo_children()[-1].bind("<Button-1>", lambda e: self._clear_page())

        SketchRule(main).grid(row=1, column=0, sticky="ew", padx=6)

        self.chat = NotebookScroll(main)
        self.chat.grid(row=2, column=0, sticky="nsew")

        self.meter_row = tk.Frame(main, bg=PAPER, pady=6)
        self.meter_row.grid(row=3, column=0, sticky="ew", padx=18)
        tk.Label(self.meter_row, text="LAST MATCH CONFIDENCE", font=FONT_TAG,
                 fg=INK_SOFT, bg=PAPER).pack(side=tk.LEFT)
        self.meter = PencilMeter(self.meter_row, width=180)
        self.meter.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        input_row = tk.Frame(main, bg=PAPER, pady=14)
        input_row.grid(row=4, column=0, sticky="ew", padx=18)
        input_row.grid_columnconfigure(0, weight=1)

        entry_wrap = tk.Frame(input_row, bg=CARD_WHITE, highlightthickness=1,
                               highlightbackground=INK_SOFT)
        entry_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry = tk.Entry(entry_wrap, font=FONT_INPUT, bg=CARD_WHITE, fg=INK,
                               relief="flat", insertbackground=INK,
                               highlightthickness=0, bd=10)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.insert(0, "Ask about LLMs, generative AI, RAG, fine-tuning…")
        self.entry.config(fg=INK_SOFT)
        self.entry.bind("<FocusIn>", self._clear_placeholder)

        send_btn = tk.Label(input_row, text="Send  \u270E", font=FONT_HEADING,
                             fg=INK, bg=HILITE_YELLOW, padx=18, pady=10, cursor="hand2")
        send_btn.grid(row=0, column=1)
        send_btn.bind("<Button-1>", lambda e: self._send())

        clear_btn = tk.Label(input_row, text="Clear", font=FONT_BODY,
                              fg=INK_SOFT, bg=PAPER, padx=10, pady=10, cursor="hand2")
        clear_btn.grid(row=0, column=2)
        clear_btn.bind("<Button-1>", lambda e: self.entry.delete(0, tk.END))

    def _clear_placeholder(self, event):
        if self.entry.get().startswith("Ask about"):
            self.entry.delete(0, tk.END)
            self.entry.config(fg=INK)

    # ── Conversation rendering ───────────────────────────────────────────────
    def _post_user_note(self, text):
        row = tk.Frame(self.chat.inner, bg=PAPER, pady=6)
        row.pack(fill=tk.X, padx=20)
        wrap = tk.Frame(row, bg=PAPER)
        wrap.pack(anchor="e")
        tk.Label(wrap, text="YOU", font=FONT_TAG, fg=INK_SOFT, bg=PAPER
                 ).pack(anchor="e", padx=4)
        card = tk.Frame(wrap, bg=HILITE_BLUE, highlightthickness=0)
        card.pack(anchor="e")
        tk.Label(card, text=text, font=FONT_BODY, fg="#0F2233", bg=HILITE_BLUE,
                 wraplength=420, justify="left", padx=14, pady=10).pack()
        self.chat.scroll_to_bottom()

    def _post_bot_note(self, text, confidence, matched):
        row = tk.Frame(self.chat.inner, bg=PAPER, pady=6)
        row.pack(fill=tk.X, padx=20)

        hdr = tk.Frame(row, bg=PAPER)
        hdr.pack(anchor="w", padx=4)
        tk.Label(hdr, text="STUDYDESK", font=FONT_TAG, fg=TAB_TEAL, bg=PAPER
                 ).pack(side=tk.LEFT)
        if confidence is not None:
            tk.Label(hdr, text=f"  ·  matched \u201c{matched}\u201d  \u00b7  {confidence*100:.0f}% match",
                     font=FONT_SMALL, fg=INK_SOFT, bg=PAPER).pack(side=tk.LEFT)

        card = tk.Frame(row, bg=CARD_WHITE, highlightthickness=1,
                         highlightbackground=HILITE_YELLOW)
        card.pack(anchor="w", fill=tk.X, padx=4, pady=(4, 0))
        stripe = tk.Frame(card, bg=HILITE_YELLOW, height=4)
        stripe.pack(fill=tk.X)
        tk.Label(card, text=text, font=FONT_NOTE, fg=INK, bg=CARD_WHITE,
                 wraplength=560, justify="left", anchor="w", padx=16, pady=12
                 ).pack(anchor="w", fill=tk.X)

        self.chat.scroll_to_bottom()

        if confidence is not None:
            self.meter.set(confidence)
            self.confidence_total += confidence
            self.confidence_hits += 1
            self.avg_label.config(
                text=f"{(self.confidence_total / self.confidence_hits) * 100:.0f}%"
            )

    def _post_typing(self):
        row = tk.Frame(self.chat.inner, bg=PAPER, pady=6)
        row.pack(fill=tk.X, padx=20)
        tk.Label(row, text="STUDYDESK is jotting a reply", font=FONT_SMALL,
                 fg=INK_SOFT, bg=PAPER).pack(anchor="w", padx=4)
        dots = PencilTapping(row)
        dots.pack(anchor="w", padx=4)
        dots.start()
        self.chat.scroll_to_bottom()
        return row, dots

    # ── Send / receive ───────────────────────────────────────────────────────
    def _send(self, forced_text=None):
        text = forced_text if forced_text is not None else self.entry.get().strip()
        if not text or text.startswith("Ask about"):
            return
        self.entry.delete(0, tk.END)
        self._post_user_note(text)
        self.msg_count += 1
        self.count_label.config(text=str(self.msg_count))

        typing_row, dots = self._post_typing()

        def worker():
            time.sleep(random.uniform(0.35, 0.8))
            answer, score, matched = self.engine.ask(text)
            self.after(0, lambda: self._finish_reply(typing_row, dots, answer, score, matched))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_reply(self, typing_row, dots, answer, score, matched):
        dots.stop()
        typing_row.destroy()
        self._post_bot_note(answer, score, matched)

    def _clear_page(self):
        for child in list(self.chat.inner.winfo_children()):
            child.destroy()
        self.meter.set(0)
        self._post_bot_note(
            "Page cleared. Ask me anything about LLMs and generative AI.",
            confidence=None, matched=None,
        )


if __name__ == "__main__":
    app = StudyDeskApp()
    app.mainloop()