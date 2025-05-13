This folder contains scripts and pipelines for scraping popular applications from both the Google
Play Store (in `gplay/`) and the Xiaomi Mi Store (in `xiaomi/`).

The Google Play Store portion depends on access to [AndroZoo](https://androzoo.uni.lu/gp-metadata)
metadata, which we use to order application download count and popularity.

The Xiaomi Mi Store application scraping relies only on Xiaomi's own publicly available ranking data.

Downloading the top ~1K apps from both stores can be quite costly in terms of time, space, and network
usage. We suggest reserving about 5TB of space on your disk drives before attempting to download
the full APK archives; ours ended up around 1TB total, but this figure may increase in the future
depending on which applications end up in the top 1k. Depending on your network speed, these
downloads may take several dozen hours to complete.
