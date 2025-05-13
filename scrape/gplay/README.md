We ingest open-source metadata from [AndroZoo](https://androzoo.uni.lu/) to determine top apps from
the Google Play Store ecosystem. With a newline-separated of application package names, we then run
[apkeep](https://github.com/EFForg/apkeep) in order to download the applications directly from the
Google Play Store. We refer to the [Google
Play](https://github.com/EFForg/apkeep/blob/master/USAGE-google-play.md) usage guide for setup and
filling out the appropriate fields in `apkeep.ini`.
