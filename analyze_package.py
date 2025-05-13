import pyshark
import argparse
import glob
from datetime import datetime
import os
import sys
from hexdump import hexdump
import logging
from urllib.parse import urlparse, parse_qs, unquote

import pyshark
import entropy

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def analyze_datatype_entropy(http_layer):
  response_code = ""
  request_method = ""
  request_uri = ""
  request_query = ""
  query_type = ""
  body_type = ""
  request_body = b""
  request_in = None
  try:
    #print("\n" + "="*50 + "\n")

    if hasattr(http_layer, "request_method"): # HTTP REQUEST
      # Extract the HTTP request method, URI, and headers
      request_method = http_layer.get_field('request_method')
      host = http_layer.get_field('host')
      uri = http_layer.get_field('request_uri')
      request_uri = f"{host}{uri}"

      query_has_entropy = False
      # Print the request line
      parsed = urlparse(uri)
      if parsed.query:
        request_query = parsed.query
        query_type = entropy.decode_query_params(parsed.query.encode("utf-8"))

      # Extract the HTTP request body if it exists
      if hasattr(http_layer, 'file_data'):
          request_body = http_layer.file_data.binary_value
          body_type = entropy.check_entropic(request_body)

    elif hasattr(http_layer, 'response_code'):
      response_code = http_layer.response_code
      if hasattr(http_layer, 'request_in'):
        request_in = http_layer.request_in
      # Extract the HTTP request body if it exists
      if hasattr(http_layer, 'file_data') and http_layer.file_data.raw_value is not None:
          request_body = http_layer.file_data.binary_value
          body_type = entropy.check_entropic(request_body)
  except KeyError as e:
      # Handle cases where the expected fields are not found
      logger.warning(f"Error processing packet: {e}")
  return {
    "request_method": request_method,
    "response_code": response_code,
    "request_uri": request_uri,
    "body_datatype": body_type,
    "request_query": { "data": request_query, "type": query_type },
    "request_in": request_in
  }

def get_candidates_for_custom_crypto(filename):
  pcap_data = pyshark.FileCapture(filename, display_filter="http and ip.addr != 127.0.0.1")

  logger.info(f"Analyzing {filename}...")
  packets = {}

  candidates = {}

  for packet in pcap_data:
    logger.info(f"Analyzing packet # {packet.number}...")
    http_layer = packet['http']
    metadata = analyze_datatype_entropy(http_layer)
    metadata["packet_number"] = packet.number
    packets[packet.number] = metadata

    request_ref = metadata["request_in"]
    if request_ref in candidates:
      candidates[request_ref]["response"] = metadata

    if "high entropy" in metadata["body_datatype"]:
      logger.info(metadata)
      if request_ref: # RESPONSE
        candidates[request_ref] = {
          "request": packets[request_ref],
          "response": metadata
        }
      else: # REQUEST
        candidates[packet.number] = {
          "request": metadata,
        }

  return candidates

def analyze_all_files(traces):
  results = {}
  for trace in traces:
    result = get_candidates_for_custom_crypto(trace)
    results[trace] = result
  return results

def main():
  parser = argparse.ArgumentParser(description="Analyze traces for specified package.")
  parser.add_argument("package_name")
  parser.add_argument("--dir", default="traces/", type=str)

  args = parser.parse_args()

  #traces = {}
  #for filename in glob.glob(f"{args.dir}*.pcap*"):
  #  package_name, date, time = os.path.basename(filename).rsplit("_", 2)
  #  time = time.rstrip(".pcapng")
  #  epoch = int(datetime.strptime(f"{date}_{time}", "%Y-%m-%d_%H-%M-%S").timestamp())
  #  if package_name not in traces:
  #    traces[package_name] = []
  #  traces[package_name].append(filename)
  traces = glob.glob(f"{os.path.join(args.dir, args.package_name)}_*.pcap*")
  logger.info(traces)
  results = analyze_all_files(traces)
  logger.info(sum([len(x) for x in results.values()]))


if __name__ == "__main__":
  main()

