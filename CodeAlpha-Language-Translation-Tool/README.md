# Task 1 - Language Translation Tool

**Author:** Lakshya Mishra
**Internship:** CodeAlpha

## About

"Postscript" is a browser-based language translator, designed around a small
post-office / airmail letter theme: you write a message, address it from one
language "to" another, send it, and it comes back translated with a postmark
stamped on it.

## Features

- Text input with source and target language selection (45+ languages, plus
  auto-detect for the source).
- One-click language swap.
- Calls the MyMemory Translation API to translate the text.
- Displays the translated text clearly, with an animated postmark stamp
  showing the detected/source language, target language, and date.
- Copy-to-clipboard button and text-to-speech playback for both the
  original and translated text.
- A "Recently sent" strip that keeps the last few translations as little
  postcards you can click to reload.
- Live character counter and a `Ctrl + Enter` shortcut to send.

## Tech

Plain HTML/CSS/JavaScript, no build step or dependencies. Fonts are pulled
from Google Fonts (Fraunces, Special Elite, IBM Plex Sans). Translation is
handled by the free MyMemory Translation API (no key required); swapping in
Google Cloud Translation or Microsoft Translator would only mean changing
the `translate()` function's fetch call.

## Run it

Just open `index.html` in a browser  no server or install needed.
