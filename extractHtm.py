""" https://stackoverflow.com/questions/11790535/extracting-data-from-html-table """
import sys
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

root = "out_htm"
files = os.listdir(root)
#files = ["034040000000_OsnabrückStadt_2018.html"]

def extract(root,file):
    with open(os.sep.join([root,file])) as html:
        soup = BeautifulSoup(html)
        base = file.split(".html")[0]
        hdrs4 = soup.find_all("h4")
        captions = pd.DataFrame()
        goals = []
        for h in hdrs4:
            if h.get_text(strip = True) == "Festgelegte Ziele":
                print ("goals present",h)
                glist = h.find_next("ul").find_all("li")
                for g in glist:
                    goals.append(g.get_text())
                print ("goals",goals)
                break
        if len(goals) > 0:
            gf = pd.DataFrame(goals)
            gf.to_csv(os.sep.join([root,base + "-Goals.csv"]))
            captions = captions.append({"table":"Goals","caption":"Goals","file":base + "-Goals.csv"},ignore_index=True)
            
        tables = soup.find_all("table", attrs={"id":"table-bericht"})

        for t in tables:
            title = re.sub(' +', ' ',t.find_next_siblings("p")[0].get_text(strip=True).replace("\n",""))
            tabnum = title.split(":")[0]
            title = title.split(":")[1]
            print(tabnum," - ",title)
            file = base + "-" + tabnum + ".csv"
            captions = captions.append({"table":tabnum,"caption":title,"file":file},ignore_index=True)
            print(captions)
            # The first tr contains the field names.
            headings = [th.get_text(strip=True) for th in t.find("tr").find_all("th")]

            df = pd.DataFrame()
            for row in t.find_all("tr")[1:]:
                item = dict(zip(headings, (td.get_text(strip=True) for td in row.find_all("td"))))
                print(item)
                df = df.append(item,ignore_index=True)  

            tblname = file
            df.to_csv(os.sep.join([root,tblname]))
            
        captname = base + "-Tables.csv"
        captions.to_csv(os.sep.join([root,captname]))


for i,f in enumerate(files):
    try:
        #print(f)
        extract(root,f)
    except:
        print("Failed on ",f)

