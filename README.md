# Graphite

Lightning-fast answers, one keystroke away.

Graphite is a minimal desktop launcher for quick answers. Type your question, get a structured response in seconds. No browser tabs. No distractions.

## Features

- **Instant Answers** — Get direct responses (AI responses may include mistakes)
- **Structured Output** — Answers formatted as What/Why/How for clarity
- **Quick Translation** — Translate text to your preferred language instantly
- **Fallback Search** — One-click Google search if you need more details
- **Copy to Clipboard** — Paste answers directly into your work
- **Configurable** — Set your API key and language preferences once
- **Minimal UI** — No clutter, no fluff, just the answer

## Requirements

- Linux with X11 (Cinnamon, GNOME, KDE, etc.)
- Python 3.6+
- API key from [Google AI Studio](https://aistudio.google.com/app/apikey) (free tier)

**Note:** Only tested on X11. Wayland and Hyprland support untested—use at your own risk.

## Pictures
- Q/A Demo
  
![ScreenShot](https://github.com/hassanmaqbool12/Graphite/blob/main/Media/Screenshot%20from%202026-05-17%2019-51-07.png)

- Translation Demo
  
![ScreenShot](https://github.com/hassanmaqbool12/Graphite/blob/main/Media/Screenshot%20from%202026-05-17%2019-55-48.png)

## Installation

### From Releases

Download the latest `.deb` from [GitHub Releases](https://github.com/your-username/graphite/releases).

```bash
sudo dpkg -i Debian-build-source.deb
```
Then launch:

```bash
graphite
```

## Getting Started

### 1. Set Your API Key

Launch Graphite and enter:

```
k your-api-key-here
```

Wait for the "API Key Updated" message.

### 2. Set Your Language

For translation mode, set a language code:

```
l ur
```

Examples: `ur` (Urdu), `es` (Spanish), `fr` (French), `de` (German), etc.

### 3. Start Asking

Type any question:

```
what is a decorator in python
```

Graphite returns a structured answer:

```
What: A function that modifies another function's behavior
Why: To add functionality without changing the original code
How: @decorator syntax above function definition
```

## Commands

| Prefix | Purpose | Example |
|--------|---------|---------|
| None | Ask a question | `list comprehension python` |
| `t` | Translate to your language | `t hello world` |
| `k` | Update API key | `k [new key]` |
| `l` | Change translation language | `l es` |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit query |
| `Esc` | Close app |
| `Ctrl+Q` | Quit |
| `Ctrl+G` | Google the last query |
| `Ctrl+P` | Copy answer to clipboard |
| `Ctrl+C` | Clear answer |

### Register a Global Shortcut (Cinnamon)

For faster access, bind Graphite to a global keyboard shortcut:

1. Open **Keyboard** settings
2. Go to **Shortcuts** → **Custom Shortcuts**
3. Click **+Add**
4. Name: `Graphite`
5. Command: `graphite`
6. Press your preferred key (e.g., `Super+/` or `Alt+G`)
7. Done. Now launch Graphite from anywhere.

## Security & Privacy

- **Your API key is stored locally** in `config.db`
- No data is sent to us—only to Google for API calls
- **Code is open source.** Review it on [GitHub](https://github.com/hassanmaqbool12/graphite/Code) if you have doubts
- Shelve database is unencrypted; use a strong API key

## What It's Good For

- Quick module/function documentation lookups
- Instant explanations of concepts
- Rapid language translation
- Getting unstuck without leaving your terminal
- Learning by example (How sections show usage)

## Limitations

- API rate limits (depends on your Google quota)
- Answers limited to 4 sentences max (by design)
- Requires internet connection
- No history or saved queries

## Feedback & Issues

Found a bug? Have an idea? [Create an issue on GitHub](https://github.com/your-username/graphite/issues).

Include:
- What you were doing
- What happened
- Your system (OS, desktop, Python version)
- Error message (if any)

## Troubleshooting

**"Invalid API key" error**
- Check that you've set the key correctly: `k your-key`
- Verify the key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Keys from Google Cloud (different service) won't work

**"Rate limit reached"**
- You've hit the free tier quota
- Wait a few hours or upgrade to a paid plan

**Translation not working**
- Ensure you've set a language, e.g `l ur`
- Check internet connection

**App won't launch**
- Install dependencies: `sudo apt install python3-gi gir1.2-gtk-3.0`
- Launch from terminal via : `graphite`, And share the logs with me.

**Wayland/Hyprland issues**
- Graphite is only tested on X11
- If you're on Wayland/Hyprland, behavior is unpredictable
- Consider switching to X11 or open an issue with details

## About

Graphite is part of the Carbon project ecosystem.

Built with Python, GTK 3, and open standards.

---

**Questions?** Open an issue. **Found a bug?** Open an issue. **Have an idea?** Open an issue.
