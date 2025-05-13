import csv
import sys
import time
import requests
import json
import argparse

import logging
logger = logging.getLogger(__name__)

#OUT_FILE = "xiaomi-app-metadata-1-2025.json"

def get_json_metadata(appid):
    url = f"https://app.market.xiaomi.com/apm/download/{appid}?marketVersion=1914002&os=V6.2.1.0.KXDCNBK&sdk=19"
    response = requests.get(url)
    json_response = response.json()
    return json_response

def process_row(outfile, row, retries=0):
    appid = row[3]
    if appid == "ERROR" or retries > 5:
        return
    try:
        json_data = get_json_metadata(appid)
        if "apkSize" not in json_data:
            logger.info("Hit rate limit. Waiting 1 min...")
            time.sleep(60)
            return process_row(outfile, row, retries=retries+1)
        if "apk" not in json_data:
          logger.info("No APK link in response.")
          return
        json.dump(json_data, outfile)
        outfile.write("\n")
        outfile.flush()
    except:
        return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Input file. If not specified, retrieves from stdin.')
    parser.add_argument('--output',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Output file. If not specified, outputs to stdout.')
    args = parser.parse_args()


    processed_apps = set()
    #with open(OUT_FILE, "r") as f:
    #    for line in f.readlines():
    #        app = json.loads(line)
    #        processed_apps.add(app["packageName"])
    reader = csv.reader(args.input)
    
    # Process headers
    headers = next(reader)
    headers.append("APPID")

    # Process each row
#with open(OUT_FILE, "a") as f:
    for row in reader:
        logger.info(f"Processing {row[1]}")
        if row[1] in processed_apps:
            continue
        process_row(args.output, row)
        time.sleep(10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
