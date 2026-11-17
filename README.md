<div align="center">

# Dolphin

### A notebook-first video search and download workflow

Search the configured video catalog, resolve playable media URLs, and download
results with a simple interactive notebook or a small Python pipeline.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/angelraymondi/dolphin/blob/main/main.ipynb)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![HTTPX](https://img.shields.io/badge/HTTPX-client-4B8BBE)](https://www.python-httpx.org/)
[![Last commit](https://img.shields.io/github/last-commit/angelraymondi/dolphin)](https://github.com/angelraymondi/dolphin/commits/main)

</div>

---

## Overview

Dolphin is a Python utility for searching the Servi catalog and downloading
video results. Its workflow separates discovery, direct-URL resolution, and
downloading, and uses a thread pool to process multiple results concurrently.

The notebook provides an interactive search form, progress indicators, and an
optional Google Drive destination when running in Colab.

## Features

- Search across result pages and filter out videos that are 20 minutes or
  longer.
- Resolve catalog pages to direct media URLs before downloading.
- Process URL resolution and downloads concurrently.
- Track each stage in an interactive Jupyter widget interface.
- Save Colab downloads to Google Drive, or choose a local output directory.

## Get started

### Google Colab

Click **Open in Colab** above. Run the setup cell first; it clones the project
into the runtime and installs its dependencies. Run the following cell to mount
Google Drive and display the search interface. Enter a query, choose an output
directory, and click **Start Download**.

> Colab runtimes are temporary. The notebook defaults to
> `MyDrive/Dolphin` so downloads are saved to mounted Drive storage.

### Run locally

```bash
git clone https://github.com/angelraymondi/dolphin.git
cd dolphin

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Open `main.ipynb` in VS Code with the Jupyter extension or in your Jupyter
environment. Alternatively, run the three-stage pipeline from the project
root:

```python
from main import find, secure, download

find("your search query")  # writes video results to videos.json
secure()                   # writes resolved media URLs to safe.json
download()                 # saves videos under downloads/
```

The pipeline functions accept optional input/output file paths and worker
counts; see [`main.py`](main.py) for their signatures.

## How it works

1. **Find** — search the configured catalog and collect video-page URLs.
2. **Resolve** — retrieve each page's direct media URL.
3. **Download** — stream the media to disk using concurrent workers.

The notebook runs these stages behind an interactive UI. The Python functions
in `main.py` expose the same workflow for scripts and automation.

## Configuration

The catalog base URL and request timeout are read from
[`config/servi.json`](config/servi.json). The scraper expects the catalog pages
to follow the HTML structure used by the Servi engine in
[`util/engines/servi.py`](util/engines/servi.py).

## Project layout

```text
.
├── config/servi.json       # Catalog URL and request timeout
├── main.ipynb              # Interactive notebook and Colab entry point
├── main.py                 # Search, resolve, and download functions
├── requirements.txt        # Python dependencies
└── util/
    ├── engines/servi.py    # Catalog search and media URL resolution
    └── fetch_video.py      # Streaming download helper
```

