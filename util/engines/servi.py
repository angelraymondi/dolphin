import httpx
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import re

with open(Path(__file__).resolve().parent.parent.parent / "config" / "servi.json" , 'r', encoding='utf-8') as data:
  servi_config = json.load(data)

client = httpx.Client(
  base_url=servi_config["base_url"],
  timeout=servi_config["timeout"],
  follow_redirects=False
)

def get_raw_url(video_url):
  response = client.get(video_url)
  response.raise_for_status()
  soup = BeautifulSoup(response.text, 'lxml')

  video = soup.select_one('video > source').get('src')
  
  return video

from concurrent.futures import ThreadPoolExecutor

def parse_duration(value):
  value = value.strip().lower()

  if not value:
    return None

  match = re.fullmatch(r"(\d+)\s*s(?:ec(?:ond)?s?)?", value)

  if match:
    return int(match.group(1))

  value = re.sub(r"\s*(?:min(?:ute)?s?|h(?:our)?s?)\s*$", "", value)

  parts = value.split(":")

  if not all(part.isdigit() for part in parts):
    return None

  if len(parts) == 2:
    minutes, seconds = map(int, parts)
    return minutes * 60 + seconds

  if len(parts) == 3:
    hours, minutes, seconds = map(int, parts)
    return hours * 3600 + minutes * 60 + seconds

  return None


def fetch_page(url, params=None):
  response = client.get(url, params=params)
  response.raise_for_status()
  soup = BeautifulSoup(response.text, "lxml")

  videos = soup.select(
    "#wrap-content > #content > .grid--videos > .wrap-box-escena.itrstt > .box-escena"
  )

  video_urls = []

  for video in videos:
    link = video.select_one(":scope > a")
    duration = video.select_one(":scope > .duracion")

    if not link or not duration:
      continue

    seconds = parse_duration(duration.get_text(strip=True))

    if seconds is None or seconds >= 1200:
      continue

    href = link.get("href")

    if href:
      video_urls.append(urljoin(servi_config["base_url"], href))

  next_pages = soup.select(
    "#wrap-content > #content > nav:nth-child(2) > ul > li.pagination_item:has(a.btn-pagination--selected) ~ li.pagination_item:not(.pagination_item--next) > a[href]"
  )

  next_page_urls = [a["href"] for a in next_pages]

  return video_urls, next_page_urls

def search(query, page=1, cyclic=False, max_workers=5):
  video_urls = []
  visited_urls = set()

  initial_route = "search/" if page <= 1 else f"search/page{page}.html"

  page_videos, next_page_urls = fetch_page(initial_route, params={"q": query})
  video_urls.extend(page_videos)
  visited_urls.add(initial_route)

  if not cyclic or not next_page_urls:
    return {
      "video_urls": video_urls,
      "next_page_urls": next_page_urls,
    }

  while next_page_urls:
    pending_urls = [u for u in next_page_urls if u not in visited_urls]
    if not pending_urls:
      break

    batch_urls = pending_urls[:-1]
    pivot_url = pending_urls[-1]

    if batch_urls:
      with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fetch_page, batch_urls))
      for batch_videos, _ in results:
        video_urls.extend(batch_videos)
      visited_urls.update(batch_urls)

    pivot_videos, next_page_urls = fetch_page(pivot_url)
    video_urls.extend(pivot_videos)
    visited_urls.add(pivot_url)
  
  return {
    "video_urls": video_urls,
  }