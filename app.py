from crypt import methods
from attr import has
from flask import Flask, render_template, redirect, request
from bs4 import BeautifulSoup as bs
import requests

app = Flask(__name__)
linkIcerik = requests.get("https://www.songlyrics.com/")
site = bs(linkIcerik.content, 'html.parser')

ayarlar = {}

with open("ayarlar.txt", encoding="utf-8") as dosya:
    for i in dosya.readlines():
        i = i.replace("\n", "").split("=")
        ayarlar[i[0]] = i[1]

@app.route("/")
def index():
    return render_template("index.html", ayarlar=ayarlar)

@app.route("/ara", methods=["GET", "POST"])
def sarkiAra():
    if request.method == "GET":
        sarkiList = []
        sarkilar = site.find('div', attrs={'class': 'box listbox'})

        for sarki in sarkilar.findAll('tr', attrs={'itemprop': 'itemListElement'}):
            sarkiList.append(str(sarki.h3.text + "," +  sarki.span.text).split(","))

        return render_template("ara.html", sarkilar=sarkiList, ayarlar=ayarlar)
    
    return redirect("/ara/" + request.form.get("arandi"))

@app.route("/lyrics/<string:sarkici>/<string:sarki>")
def lyrics(sarkici, sarki):
    sorgu = requests.get("https://www.songlyrics.com/" + str(sarkici).replace(" ", "-").lower() + "/" + str(sarki).replace(" ", "-").lower() + "-lyrics")
    lirik = bs(sorgu.content, 'html.parser')
    sozler = lirik.find('div', attrs={'id': 'songLyricsDiv-outer'})

    if (sozler != None):
        return render_template("lirik.html", sarkici=sarkici, sarki=sarki, sozler=sozler.text, ayarlar=ayarlar)
    else:
        return redirect("/ara")

@app.route("/ara/<string:aranan>", methods=["GET", "POST"])
def sarkiCikti(aranan):
    sorgu = requests.get("https://www.songlyrics.com/index.php?section=search&searchW=" + aranan + "&submit=Search")
    cikti = bs(sorgu.content, 'html.parser')
    dongu = 0

    sarkilar = []
    ciktilar = cikti.find('div', attrs={'class': 'coltwo-wide-2'})

    for cikti in ciktilar.findAll('div', attrs={'class': 'serpresult'}):
        if dongu == 10:
            break

        veri = str(cikti.p.a.text + "," + cikti.h3.text).replace("Lyrics", "").split(",")
        
        if veri not in sarkilar:
            sarkilar.append(str(cikti.p.a.text + "," + cikti.h3.text).replace("Lyrics", "").split(","))
            dongu = dongu + 1

    print(sarkilar)
    return render_template("araCikti.html", aranan=aranan, sarkilar=sarkilar, ayarlar=ayarlar)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)