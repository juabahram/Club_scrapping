#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
import requests
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
import re


# to avoid ssl error
import os, ssl
from _datetime import datetime
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# the URL of the login page
login_url = "https://yoururl.es/login"
session= requests.Session()

response = session.get(login_url)

soup = BeautifulSoup(response.text, "html.parser")
csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
# the payload with your login credentials
payload = {
    "_username": "username1",
    "_password": "password1",
    "_csrf_token": csrf_token,
}

heads = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": login_url, 
    "Origin": "https://yoururl.es",
}

response = session.post(login_url, data=payload, headers=heads)

p=response.url
his=response.history
if response.ok and "member" in p:
    print("login successful")

else:
    print("login failed")
    # send the POST request to login


def extraer_elementos():
    lista_codigos=[]
    
    for t in range(1,171):
        url = "https://yoururl/member/page/" + str(t)
        response = session.get(url)
        if response.status_code ==200:
            s = BeautifulSoup(response.text, "lxml")
            q= s.find_all("tr")
    
            for i in q:
                cod= i.get("id")
                if cod != None:
                    lista_codigos.append(cod)

    return lista_codigos

def almacenar_socios():
    conn = sqlite3.connect('supreme.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS SOCIOS")
    conn.execute('''CREATE TABLE SOCIOS
        (NOMBRE            TEXT NOT NULL,
        CODE           TEXT,
        CHIP            INT,
        DNI        TEXT,
        FECHADNI    DATE,
        ALTA      DATE,
        NACIMIENTO    DATE,
        TLF    TEXT,
        CREDIT    FLOAT);''')
    
    lista_socios = extraer_elementos()
    
    i=0
    for e in lista_socios:
        response = session.get("https://yoururl.es/member/" + str(e))
        s = BeautifulSoup(response.text, "lxml")
        nombre = s.find("h4", class_="m-t-sm")
        if nombre == None:
            print("what")
            nombre="noname"
        else:
            nombre = nombre.get_text(strip=True)
        cod= s.find("p", class_="m-b-sm").get_text(strip=True)
        chip= s.find("i", class_="fa fa-id-card-o").find_parent("li").find("div", class_="value").get_text(strip=True)
        dni=s.find("h4", class_="m0").find_parent("div").find_next_sibling("div").find_next_sibling("div").find("h4", class_="m0").get_text(strip=True)
        response = session.get("https://yoururl.es/member/" + str(e) + "/edit")
        d = BeautifulSoup(response.text, "lxml")
        fechadni= d.find("input", id="member_dniExpiration")
        fechadni1= fechadni["value"].replace("-", ' ')
        fechadni2= datetime.strptime(fechadni1, "%d %m %Y")
        alta= d.find("input", id="member_created")
        alta1= alta["value"].replace("-", ' ')
        alta2= datetime.strptime(alta1, "%d %m %Y")
        nacimiento= d.find("input", id="member_birth")
        nacimiento1= nacimiento["value"].replace("-", ' ')
        nacimiento2= datetime.strptime(nacimiento1, "%d %m %Y")
        tlf1= d.find("input", id="member_phone")
        input_phone = d.find("input", id="member_phone")
        if input_phone and "value" in input_phone.attrs:
            tlf=tlf1["value"]
        else:
            tlf=0
        credit = s.find("span", id="membercredit").get_text(strip=True)
        
        conn.execute("""INSERT INTO SOCIOS (NOMBRE, CODE, CHIP, DNI, FECHADNI, ALTA, NACIMIENTO, TLF, CREDIT) VALUES (?,?,?,?,?,?,?,?,?)""",
                     (nombre, cod, chip,dni, fechadni2, alta2, nacimiento2, tlf, float(credit)))
        print(i)
        i=i+1
    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM SOCIOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " socios")
    conn.close()

def almacenar_carta():
    conn = sqlite3.connect('dispensario.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS CARTA")
    conn.execute('''CREATE TABLE CARTA
        (NOMBRE            TEXT NOT NULL,
        PRECIO_UNIDAD           TEXT,
        CATEGORÍA            TEXT);''')
    
    response = session.get("https://yoururl.es/category/")
    s = BeautifulSoup(response.text, "lxml")
    catego= s.find("h5")
    i=0
    while(i<15):
        catego1=catego.get_text(strip=True).split("(")[0]
        nombres_precio=catego.find_parent("div", class_="row").find_next_sibling("div", class_="row").find("tbody").find_all("tr")
        for elem in nombres_precio:
            nombre=elem.find("td", class_="d-none d-sm-table-cell")
            nom=nombre.get_text(strip=True)
            precio=nombre.find_next_sibling("td", class_="d-none d-sm-table-cell").get_text(strip=True)
            conn.execute("""INSERT INTO CARTA (NOMBRE, PRECIO_UNIDAD, CATEGORÍA) VALUES (?,?,?)""",
                    (nom, precio, catego1))
            
        catego= catego.find_parent("div", class_="row").find_next_sibling("div", class_="row").find_next_sibling("div", class_="row").find("h5")
        
        if catego ==None:
            catego=s.find("h5", text=lambda x: x and "Bebidas" in x)
            
        i=i+1
        print(i)

    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM CARTA")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " items")
    conn.close()

if __name__ == "__main__":
    #almacenar_socios()
    almacenar_carta()