import os
import argparse
import concurrent.futures
import csv
import logging

import pipeline
logger = logging.getLogger(__name__)

TIMEOUT_PER_RUN = 5 * 60 # 5 minutes

def run_pipeline(apk_dir, package, sniff, mitmproxy):
  return pipeline.run(package,
                      f"{os.path.join(apk_dir, package)}.apk",
                      n_actions=10,
                      sniff=sniff,
                      mitmproxy=mitmproxy)

def run(csvfile, apkdir, column=0, sniff=None, mitmproxy=False):
  packages = []
  with open(csvfile, "r") as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
      packages.append(row[column])

  for package in packages:
    try:
      with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_pipeline, apkdir, package, sniff, mitmproxy)
        future.result(timeout=TIMEOUT_PER_RUN)
        logger.info(f">>>{package} DONE")
    except concurrent.futures.TimeoutError:
      logger.warning(f">>>{package} TIMEOUT")

    except Exception as e:
      logger.warning(f">>>{package} ERROR {type(e).__name__} {str(e)}")

def main():
  parser = argparse.ArgumentParser(description="Run pipeline on a bunch of apps.")
  parser.add_argument("csvfile", type=str)
  parser.add_argument("--column", type=int, default=0)
  parser.add_argument("--apkdir", type=str)
  parser.add_argument("--mitmproxy", action="store_true")
  parser.add_argument("--sniff", type=str)

  args = parser.parse_args()
  run(args.csvfile, args.apkdir, args.column, args.sniff, args.mitmproxy)

if __name__ == '__main__':
  main()
