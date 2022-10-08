# scrape-klimaschutz-planer-reports
Scrape reports from https://www.klimaschutz-planer.de/. Inspired by https://github.com/derhuerst/scrape-klimaschutz-planer-reports

**Very initial draft, however capable to extract data**

**Uses Klimaschutz-Planer *API* to retrieve files.** API documentation is unknown.

## Approach
Read city description from website. The important stuff is loaded with the map data. 
Experience shows we can get the JSON data like so:

> curl 'https://www.klimaschutz-planer.de/ajax.php?action=thgMap&onlyShowCached=1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0' -H 'Accept: */*' -H 'Accept-Language: de,en-US;q=0.7,en;q=0.3' -H 'Accept-Encoding: gzip, deflate, br' -H 'X-Requested-With: XMLHttpRequest' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Referer: https://www.klimaschutz-planer.de/'  -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'TE: trailers'  > cities.json

This might change in the future ... 

We store the data in *cities.json* for further processing.

For all entries in *cities.json*:
  * check if valid on year, report and einwohner
  * Extract basic infos
  * Setup URL to *API* for city key (communeKey) => HTML
  * Call headless Chromium to render and save HTMT
  * Search for tables with beautiful soup
  * Extract tables => file
  * Write summary file *results.json*





