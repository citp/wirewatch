### Scraping Xiaomi's Mi Store.

This scraping pipeline is organized with via Snakemake. Simply run: `snakemake -c <num-cores` to
scrape top Xiaomi apps.

This pipeline makes many web requests, though it will back off and retry upon hitting rate
limits.

 1. Pulls top application package names from the Xiaomi Mi Store website.
 2. Pulls associated internal "IDs" from an internal Xiaomi API.
 3. Pulls URL download links, from an internal Xiaomi API. This API requires Xiaomi's internal ID and is heavily rate-limited.
 4. Finally, the pipeline downloads the apps from the links.

