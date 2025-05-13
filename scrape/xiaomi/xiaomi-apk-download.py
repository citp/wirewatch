import os
import sys
import argparse

import csv
import json
import requests
from multiprocessing import Pool

#with open("baidu-scrape.jsonl", "r") as f:
#  data = f.readlines()

#JSON_DATA = "xiaomi-app-metadata-1-2025.json"
DIRECTORY = "./apps/"

def download(name, url):
  path = os.path.join(DIRECTORY, name + ".apk")
  eprint(f"Downloading {path}...")
  if os.path.isfile(path):
    eprint("... Already downloaded.")
    return
  response = requests.get(url)
  with open(path, 'wb') as f:
    f.write(response.content)
  eprint(f"Downloaded {path}.")

def _choose_host(hostlist):
    for host in hostlist:
        if host.startswith("https"):
            return host
    return None

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--input',
                      type=argparse.FileType('r'),
                      default=sys.stdin,
                      help='Input file. If not specifed, retrieves from stdin.')
  parser.add_argument('--output',
                      type=argparse.FileType('w'),
                      default=sys.stdout,
                      help='Output file. If not specifed, outputs to stdout.')
  args = parser.parse_args()

  #reader = csv.reader(args.input)
  writer = csv.writer(args.output)

  pool = Pool(8)

  #writer = csv.writer(sys.stdout)
  alldata = {}

  to_download = []
  #with open(JSON_DATA, "r") as f:
  for datum in args.input.readlines():
    app = json.loads(datum)
    if app["packageName"] in alldata:
        continue
    if app["apk"].startswith("http"):
        url = app["apk"]
    else:
        url = os.path.join(_choose_host(app["hosts"]), app["apk"])
    app["url"] = url
    alldata[app["packageName"]] = app
    to_download.append((app["packageName"], url))
    writer.writerow([
        app["packageName"], app["id"], app["versionName"], app["versionCode"], url
        ])

    #for app in x["data"]["data"]:
    #  to_download.append((app["package"], app["downloadUrl"]))
    #  writer.writerow([app["sname"], app["package"], 
    #                  convert_wanyi(app["strDownload"]), app["catename"],
    #                  app["downloadUrl"]])

  #reader = csv.reader(sys.stdin)
  #writer = csv.writer(sys.stdout)
  #headers = next(reader)
  #headers.append("DOWNLOAD URL")
  #writer.writerow(headers)

  #for row in reader:
  #  row.append(alldata[row[1]]["url"])
  #  writer.writerow(row)


  pool.starmap(download, to_download)
