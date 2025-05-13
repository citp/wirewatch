import os
import sys
import time
import datetime
import random
import subprocess
import argparse

import uiautomator2 as u2
import logging

import adb
import sniffer
import agent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

CAPTURE_DIRECTORY = "traces"
STANDARD_WAIT = 0.2

def capture_name(appname: str, ext: str) -> str:
  current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  return f"{appname}_{current_time}.{ext}"

def random_click_session(device, package_name, n_actions):
  logger.info(f"Starting {package_name} session...")
  n_clicks = 0
  try:
    with device.session(package_name) as s:
      agt = agent.ChaosAgent(s, package_name)
      for i in range(0, n_actions):
        try:
          agt.click_something()
          n_clicks += 1
        except agent.AppClosedException:
          break
  except u2.exceptions.SessionBrokenError:
    logger.warning("Unexpectedly closed app")
  logger.info(f"... Clicked {n_clicks} time(s)!")
  return n_clicks


def set_mitmproxy(proxy):
  return adb.shell(['settings', 'put', 'global', 'http_proxy', proxy])

def run(package_name, apk_path, n_actions=10, sniff=None, mitmproxy=False):
  # START TRAFFIC SNIFFER
  if sniff is not None:
    if mitmproxy:
      s = sniffer.MitmproxyPacketSniffer(sniff, set_mitmproxy)
      ext = "mitmproxy"
    else:
      # Construct packet sniffer.
      # TODO: fork this to use `adb` and perform sniffing on the android device
      s = sniffer.TCPDumpPacketSniffer(
                iface=sniff,
                command_name="tshark")
      ext = "pcap"
    s.start()

  device = u2.connect()
  device.settings["wait_timeout"] = 5
  device.settings["operation_delay"] = (0.1, 0.1)

  try:
    # INSTALL APP
    if not device.app_list(package_name):
      logger.info(f"Installing {apk_path}...")
      adb.install(apk_path)
    time.sleep(STANDARD_WAIT)
    device.app_stop_all()
    device.app_auto_grant_permissions(package_name)

    # CLICK RANDOMLY
    random_click_session(device, package_name, n_actions)
    random_click_session(device, package_name, n_actions)
  finally:
    # UNINSTALL APP NO MATTER WHAT
    logger.info(f"Uninstalling {package_name}...")
    device.app_uninstall(package_name)
    if sniff is not None:
      logger.info(f"Stopping packet capture...")
      s.stop()
      pcap_file = os.path.join(CAPTURE_DIRECTORY, capture_name(package_name, ext))
      logger.info(f"Saving network trace to {pcap_file}...")
      with open(pcap_file, "wb") as f:
        f.write(s.pcap())
      return pcap_file
  return None

def main():
  parser = argparse.ArgumentParser(description="Install and open the specified application.")
  parser.add_argument("app_path")
  parser.add_argument("--sniff", default=None, type=str)
  parser.add_argument("--mitmproxy", action="store_true", default=False)
  parser.add_argument("-v", action="store_true", default=False)
  parser.add_argument("--n_actions", default=10, type=int)

  args = parser.parse_args()
  package_name = os.path.splitext(os.path.basename(args.app_path))[0]
  run(package_name, args.app_path, args.n_actions, args.sniff, args.mitmproxy)

if __name__ == '__main__':
  main()

