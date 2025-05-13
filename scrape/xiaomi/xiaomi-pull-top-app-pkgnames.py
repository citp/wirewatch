import sys

import time
import argparse
import csv
import requests
from bs4 import BeautifulSoup

import logging
logger = logging.getLogger(__name__)

BASE_URL = "https://app.mi.com/catTopList/{}?page={}"
MAX_CATEGORY = 30

def extract_app_details(pagehtml):
  results = []
  soup = BeautifulSoup(pagehtml, "html.parser")

  applist = soup.find("ul", class_ = "applist")

  for element in applist.find_all("li"):
    appname = element.find("img")["alt"]
    url = element.find("a")["href"]
    package = url[url.index("=")+1:]
    category = element.find("p", class_="app-desc").find("a").get_text()
    results.append((appname, package, category))
  return results

def get_url(category, page):
  return BASE_URL.format(category, page)

def get_page(category, page):
  url = get_url(category, page)
  return requests.get(url).text

def extract_from_category(category):
  logger.info(f"Extracting apps from category {category}...")
  page = 1
  all_results = []
  results = [0] # Seed with a no-op element to not trigger while condition
  while len(results) > 0:
    results = extract_app_details(get_page(category, page))
    all_results.extend(results)
    page += 1
  logger.info(f"Extracted {len(all_results)} apps from category {category}.")
  return all_results

def extract_all_listed_apps():
  all_results = []
  for category in range(MAX_CATEGORY):
    results = extract_from_category(category)
    all_results.extend(results)
    logger.info(f"... sleep 1 sec...")
    time.sleep(1)
  return all_results

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output',
                      type=argparse.FileType('w'),
                      default=sys.stdout,
                      help='Output file. If not specifed, outputs to stdout.')
  args = parser.parse_args()
  apps = extract_all_listed_apps()
  writer = csv.writer(args.output)
  writer.writerow(["App name", "Package name", "Category"])
  for appname, package, category in apps:
    writer.writerow([appname, package, category])


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()
