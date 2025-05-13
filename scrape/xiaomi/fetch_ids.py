import csv
import sys
import time
import argparse
import requests

import logging
logger = logging.getLogger(__name__)

# https://app.market.xiaomi.com/apm/app?appId=431355&packageName=com.ss.android.ugc.aweme&os=1.1.1&sdk=19
def get_json_from_package_name(name):
    url = f"https://app.market.xiaomi.com/apm/app?packageName={name}&os=1.1.1&sdk=19"
    app = requests.get(url).json()
    return app["app"]

def process_row(writer, row):
    data = get_json_from_package_name(row[1])
    try:
        row.append(data["appId"])
        row.append(data["versionName"])
        row.append(data["versionCode"])
        row.append(data["downloadCount"])
        row.append(data["updateTime"])
        row.append(data["level1CategoryNameV2"])
        row.append(data["level2CategoryNameV2"])
    except:
        row.append("ERROR")
    writer.writerow(row)
    sys.stdout.flush()

def main():
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

    reader = csv.reader(args.input)
    writer = csv.writer(args.output)
    
    # Process headers
    headers = next(reader)
    headers.append("APPID")
    headers.append("VERSION")
    headers.append("VERSION NUM")
    headers.append("DOWNLOADS")
    headers.append("LAST UPDATE")
    headers.append("CATEGORY")
    headers.append("SUBCATEGORY")
    writer.writerow(headers)

    # Process each row
    for row in reader:
        process_row(writer, row)
        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
