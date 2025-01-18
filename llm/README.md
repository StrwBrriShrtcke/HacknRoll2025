# LLM Section

## Set up

```bash
# Create venv 
$ python3 -m venv .venv

# Activate the venv
# Run this if on bash. Use other activates if on other shells.
$ source .venv/bin/activate 

# Install dependencies
$ pip3 install -r requirements.txt
```


## Crawling

### Set up 

Install the chromium browser engine for playwright

```bash
$ playwright install chromium
```

### Running the crawler

```bash
python3 just_crawl.py
```

It will crawl through a specified homepage and the results will be stored in a SQLite database

The results include the data extracted for each webpage, like the content, url, and from which url it's clicked from.

Specify the settings in the script, like the sites to crawl and the depth to crawl.

The stats for the results will also be stored.


Results stats with the following config:
```
max_crawl_depth = 2
site = "nus"
┌─────────────────────────────┬────────────────────────────┐
│ requests_finished           │ 953                        │
│ requests_failed             │ 439                        │
│ retry_histogram             │ [747, 120, 523, 0, 0, 0,   │
│                             │ 0, 0, 0, 2]                │
│ request_avg_failed_duration │ 25.037782                  │
│ request_avg_finished_durat… │ 9.131637                   │
│ requests_finished_per_minu… │ 25                         │
│ requests_failed_per_minute  │ 11                         │
│ request_total_duration      │ 19694.035785               │
│ requests_total              │ 1392                       │
│ crawler_runtime             │ 2306.548348                │
└─────────────────────────────┴────────────────────────────┘
```

## Ollama prompting

### Set up

Install [Ollama](https://ollama.com/download).

### Running the LLM prompting

```bash
$ ollama pull llama3.1:8b  
```

It will create questions based on the collected text content in SQLite data using Ollama AI models and classify each webpage into different categories. 