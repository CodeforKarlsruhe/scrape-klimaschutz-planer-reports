""" Extract data from klimaschutz-planer """
import pandas as pd
import pandasgui as gui
import sys
import os
from bs4 import BeautifulSoup
import re

# API
#pdf: https://www.klimaschutz-planer.de/ajax.php?action=page&pageID=bilanz_bericht_ausgabe&commune=150020000000&year=2015
#html https://www.klimaschutz-planer.de/ajax.php?action=newWindow&pageID=bilanz_bericht_ausgabe&eparam=commune%3D150020000000%26year%3D2015
# Note the eparam on html !!!

# assume we have cities.json already by :
# curl 'https://www.klimaschutz-planer.de/ajax.php?action=thgMap&onlyShowCached=1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0' -H 'Accept: */*' -H 'Accept-Language: de,en-US;q=0.7,en;q=0.3' -H 'Accept-Encoding: gzip, deflate, br' -H 'X-Requested-With: XMLHttpRequest' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Referer: https://www.klimaschutz-planer.de/'  -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'TE: trailers' 


def mkUrl(city,year):
    return f'"https://www.klimaschutz-planer.de/ajax.php?action=newWindow&pageID=bilanz_bericht_ausgabe&eparam=commune%3D{city}%26year%3D{year}"'
    #return f"https://www.klimaschutz-planer.de/ajax.php?action=newWindow&pageID=bilanz_bericht_ausgabe&eparam=commune={city}&year={year}"

def extract(root,file):
    with open(os.sep.join([root,file])) as html:
        soup = BeautifulSoup(html)
        tables = soup.find_all("table", attrs={"id":"table-bericht"})

        base = file.split(".html")[0]
        captions = pd.DataFrame()
        for t in tables:
            title = re.sub(' +', ' ',t.find_next_siblings("p")[0].get_text(strip=True).replace("\n",""))
            tabnum = title.split(":")[0]
            title = title.split(":")[1]
            print(tabnum," - ",title)
            # The first tr contains the field names.
            headings = [th.get_text(strip=True) for th in t.find("tr").find_all("th")]

            df = pd.DataFrame()
            for row in t.find_all("tr")[1:]:
                item = dict(zip(headings, (td.get_text(strip=True) for td in row.find_all("td"))))
                print(item)
                df = df.append(item,ignore_index=True)  

            tblname = base + "-" + tabnum + ".csv"
            captions = captions.append({"table":tabnum,"caption":title,"file":tblname},ignore_index=True)
            #print(captions)
            df.to_csv(os.sep.join([root,tblname]))
            
        captname = base + "-Tables.csv"
        captions.to_csv(os.sep.join([root,captname]))
        return os.sep.join([root,captname])


cities = pd.read_json("cities.json")

"""
"communeKey": "065310007007",
"communeName": "Heuchelheim",
"year": 2019,
"einwohner": 7819,
"haushalte": 3391,
"thgVK": 8159.044105527407,
"thgST": 92500.94715902071,
"thgHH": 20548.766095910196,

thgVK : Verkehr?
thgST : unklar
(thgVK + thgST)/einwohner = Gesamttreibhausgasemissionen* der Kommune [t/einwohner]
thgHH / einwohner = Treibhausgasemissionen* im Sektor Private Haushalte [t/einwohner]


Heuchelheim (065310007007)
Bilanz	2019
Gesamttreibhausgasemissionen* der Kommune	12,87 t/Ew.
Treibhausgasemissionen* im Sektor Private Haushalte	2,63 t/Ew.
EinwohnerInnen (Ew.)	7819
Festgelegte Ziele:
* Treibhausgasemissionen umfassen Kohlenstoffdioxid (CO2) sowie Methan und Distickstoffmonoxid (CH4 und N2O als CO2-Äquivalente)

"""

cities = cities.T
cities.drop(index=cities[cities.year.isna()].index,inplace = True)
cities.drop(index=cities[cities.einwohner < 1].index,inplace = True)


df = pd.DataFrame()

root = "out_htm"
try:
    os.listdir(root)
except FileNotFoundError:
    os.mkdir(root)
except:
    print("Out dir error")
    sys.exit()

for _, c in cities.iterrows():
    #print(c["communeName"])
    if (c["einwohner"] < 1) or (c["hasReport"] != True):
        continue
    item = {
        "id":c["communeKey"],
        "name":c["communeName"],
        "year":c["year"],
        "size":c["einwohner"],
        "vk":c["thgVK"],
        "st":c["thgST"],
        "hh":c["thgHH"],
        "coords":c["pinLocations"]
        }
    city = c["communeKey"]
    year = c["year"]
    name = c["communeName"].replace(","," ")
    file = ("_".join([city,name,str(year)]) + ".html").replace(" ","").replace("/","-")
    url = mkUrl(city,year)
    print(url,os.sep.join([root,file]))
    try:
        os.system("/usr/bin/chromium-browser --headless --disable-gpu --run-all-compositor-stages-before-draw  --virtual-time-budget=10000 --dump-dom " + url + " > " + os.sep.join([root,file]))
        tables = extract(root,file)
        print("Tables:",tables)
        item["tables"] = tables
        df = df.append(item,ignore_index=True)
    except:
        print("failed on",file)


df.to_json(os.sep.join([root,"results.json"]),orient="records")

print("Distribution\n",df.year.value_counts().sort_index())

