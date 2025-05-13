# WireWatch

This repository contains the associated code for
"[WireWatch](https://www.computer.org/csdl/proceedings-article/sp/2025/223600d916/26hiVQjbZqE): Measuring the security of proprietary
network encryption in the global Android ecosystem", published at IEEE S&P 2025. The project is currently under active
development as the team works to streamline running WireWatch for additional longitudinal
measurements.

If you have any questions about this work, or would like access to related historical datasets, feel free to reach out to `monaw@princeton.edu`.

Below is a bibtex citation of this work:

```
@inproceedings{wirewatch2025,
  author = { Wang, Mona and Knockel, Jeffrey and Reichert, Zoë and Mittal, Prateek and Mayer, Jonathan},
  booktitle = { 2025 IEEE Symposium on Security and Privacy (S & P) },
  title = {{ WireWatch: Measuring the security of proprietary network encryption in the global Android ecosystem }},
  year = {2025},
  volume = {},
  ISSN = {2375-1207},
  pages = {4248-4266},
  keywords = {},
  doi = {10.1109/SP61157.2025.00224},
  url = {https://doi.ieeecomputersociety.org/10.1109/SP61157.2025.00224},
  publisher = {IEEE Computer Society},
  address = {Los Alamitos, CA, USA},
  month = May}
```

## Downloading apps
See `scrape/` directory for more instructions on downloading applications. We utilize
[`apkeep`](https://github.com/EFForg/apkeep) for Google Play, F-Droid, and
Huawei AppGallery. However, their Huawei support only works for International applications.

We have custom scrapers for Xiaomi and Baidu App Stores.

To download a sample apk:
```
apkeep -a com.taobao.taobao -d huawei-app-gallery apps/huawei
```

## Prereqs
We use [`uiautomator2`](https://github.com/openatx/uiautomator2/) and built-in `adb`
functionalities.
```
python3 -m venv venv
source venv/bin/activate
pip -r requirements.txt
```

You also have to install the [Android SDK platform tools](https://developer.android.com/tools/adb).

Finally, our clustering is run via [Jupyter Notebook](https://docs.jupyter.org/en/latest/install/notebook-classic.html).

## Run pipeline on app
Make sure your emulator or USB-connected device shows up on `adb devices`.

To run the pipeline for a single app you can run:
```
python pipeline.py com.taobao.taobao.apk --n_actions 20
```

## Capture network traffic
In order to capture network traffic, you have to provide the command-line option `--sniff` with the
name of the network interface you want to capture on.
```
python pipeline.py com.taobao.taobao.apk --sniff ap1
```

You must configure your setup such that the device's network traffic is capturable on a
particular interface. If you are running an emulator, run `adb root` and you should be
able to capture the data from an interface like `android-tcpdump-any-emulator-5554`.

Alternatively, you can find a way to MitM the device. For instance, you could broadcast a WiFi
network/hotspot from the host device (e.g. the device you're running this pipeline on), then connect
the device to that WiFi network. On Mac, this is referred to as "Internet Sharing". Usually, the
traffic from that network will come onto a specific network interface which you can then specify in
`pipeline.py`.

### Instrumenting HTTP MITM with mitmproxy

You can also capture HTTP flows with mitmproxy instead of using TCPDump.
In this case, the `sniff` interface you provide will actually be the interface for the network that
your device is on. For instance, if your device is connected to the same Wi-Fi or ethernet network, you'll
provide the interface for that network. If your device network is bridged (via Android Studio or via
Internet Sharing settings) you'll have to find the appropriate bridge interface that provides the
correct IP address for your host.
```
python pipeline.py com.taobao.taobao.apk --sniff bridge0 --mitmproxy
```

This will write a `*.mitmdump` file instead of a `*.pcap` to your trace directory.


## Running the pipeline on a lot of apps

The following will run the pipeline on many (already installed) applications:

```
python run_on_apps.py <CSV_FILE> --column <COLUMN_ID> --apkdir <DIRECTORY OF APKS>
```

This expects a CSV file, where one of the columns is the package name, and that the APK for the
package is found at `<apkdir>/<package_name>.apk`.

This will run `pipeline.py` for each of those applications, sniff and save the network
traces. It also has a 5-minute timeout for each application, in case it hangs for an unexpected
reason, it will log the occurrence and move onto the next app.

## Running entropy & proprietary encryption detection on the apps

The final app analysis can be run via `python analyze_package.py <PACKAGE NAME>`, which expects
associated traces in the `traces/` subdirectory. To run all analyses, run

```
python analyze_all_packages.py --json <ANALYSIS METADATA JSON FILE>
```

Which will append candidates for proprietary encryption, as well as formatting/encoding data, into the above JSON file.

## Clustering

The clustering portion of the pipeline is run via Jupyter notebook: `cluster.ipynb`. Running this
will export `clusters.csv`, which labels all requests from `analysis.jsonl` according to a
particular numerical cluster.

### Other code files
 * `adb.py` provides wrappers for various ADB functionality.

 * `sniffer.py` provides interfaces for starting various types of network captures.

 This is adapted from tooling and interfaces developed by [Jean-Pierre Smith](https://github.com/jpcsmith/wf-tools/tree/master) which I've found are nice abstractions around both scapy and TCPDump for network captures.

 * `agent.py` provides interfaces and logic for our "automated agents" which simulate user behavior.

This includes logic for a BFS search agent (which tries to systematically explore the app's state
space) and a chaos agent (which randomly clicks buttons on the screen). Both accept confirmation
dialogs automatically, back out of login/registration pages, and fall back to clicking randomly on the screen and other inputs if there are no XML buttons.

In the time since I worked on this project, a lot of progress has been made on using LLMs to
drive automated mobile testing. A future project might include leveraging such technology to drive
these agents.

 * `entropy.py` provides logic for detecting high-entropy requests.

