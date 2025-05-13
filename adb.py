# ADB helper functions.
import tempfile
import subprocess
import os
import sys
import glob

errors = [
"INSTALL_FAILED_MISSING_SHARED_LIBRARY",
"INSTALL_FAILED_NO_MATCHING_ABIS",
"INSTALL_FAILED_MISSING_SPLIT",
]

def adb(command: list[str]) -> bytes:
  command = ['adb'] + command
  process = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                    timeout = 60)
  return process

def dump() -> bytes:
  shell(["uiautomator", "dump"])
  with tempfile.TemporaryDirectory() as tmp:
    dumpfile = os.path.join(tmp, "dump.xml")
    adb(["pull", "/sdcard/window_dump.xml", dumpfile])
    with open(dumpfile, "rb") as f:
      return f.read()
    

def start(package: str) -> bytes:
  return shell(["monkey", "-p", package, "1"])

def shell(command: list[str]) -> bytes:
  return adb(["shell"] + command)

def install(package: str) -> bytes:
  base, ext = os.path.splitext(package)
  if os.path.isdir(base):
    print("Installing XAPK...")
    packages = glob.glob(f"{base}/*")
    return adb(["install-multiple"] + packages)
    
  if not os.path.isfile(package):
    raise Exception(f"Could not find app package at {package}.")
  return adb(["install", package])

def uninstall(package: str) -> bytes:
  return adb(["uninstall", package])


