import sys
import os
from datetime import datetime
import argparse
import glob
import json
import csv
import analyze_package

def main():
  parser = argparse.ArgumentParser(description="Analyze traces for specified package.")
  parser.add_argument("csv_file", type=str)
  parser.add_argument("--dir", default="traces/", type=str)
  parser.add_argument("--json", default="analysis.jsonl", type=str)
  args = parser.parse_args()
  traces = {}
#  print(args.json)
#  print(args.csv_file)

#  processed = set()
#  with open(args.json, "r") as jsonf:
#    for line in jsonf:
#      data = json.loads(line)
#      processed.add(list(data.keys())[0])

  for filename in glob.glob(f"{args.dir}*.pcap*"):
    package_name, date, time = os.path.basename(filename).rsplit("_", 2)
    time = time.rstrip(".pcapng")
    epoch = int(datetime.strptime(f"{date}_{time}", "%Y-%m-%d_%H-%M-%S").timestamp())
    if package_name not in traces:
      traces[package_name] = []
    traces[package_name].append(filename)

  writer = csv.writer(sys.stdout)

  with open(args.csv_file, "r") as f:
    reader = csv.reader(f)
    headers = next(reader)
    headers.append("Candidates for proprietary crypto")
    writer.writerow(headers)

    with open(args.json, "w") as f_out:
      for row in reader:
        package_name = row[0]
        traces = glob.glob(f"{os.path.join(args.dir, package_name)}*.pcap*")
        if len(traces) == 0:
          writer.writerow(row + ["N/A"])
          continue
        #if traces[0] in processed:
        #  continue
        try:
          results = analyze_package.analyze_all_files(traces)
        except Exception as e:
          writer.writerow(row + ["ERROR"])
          continue

        total = (sum([len(x) for x in results.values()]))
        json.dump(results, f_out)
        f_out.write("\n")
        writer.writerow(row + [str(total)])
        f_out.flush()
        sys.stdout.flush()




if __name__ == "__main__":
  main()

