#!/usr/bin/env python
# encoding: utf-8
'''
RaaamtukoguKlient -- shortdesc

Raamatukogu kasutaja liides raamatute otsimiseks, t�htaegade vaatamiseks jne.

It defines classes_and_methods

@author:     Holger Kruusla
'''
import sys # functions used: 
import requests
import urllib.request
import logging
import argparse
from cmd import Cmd
from enum import Enum
import json

url='http://localhost:8080' # url definitsioon, peaks kasutama seadete 
FORMAT = "[%(asctime)-15s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log = logging.getLogger("RaamtukoguKlient") # handle andmebaasi logile
logging.basicConfig(filename="raamatukogu.log", level=logging.INFO, format=FORMAT) # kasutuse logi
    
class getResources(Enum):
    raamatud = '/api/v1/raamatud'
    raamat = '/api/v1/raamat/'
    otsi = '/api/v1/otsi'

class query(Enum):
    raamatud = 0
    raamat = 1
    otsi = 2
    
class Raamatukoguklient():
    def do_POST(self, qry, params, DATA):
        api= ""
        try:
            req = requests.post("{0}{1}".format(url,getResources[qry.name].value), params=params)
            print(req.status_code)
        except Exception as ex:
            log.error("PUT: {0} ebaõnnestus".format(DATA))
        
    def do_GET(self, qry, params=""):
        try:
            if qry.name not in query.__members__:
                raise ValueError
            req = requests.get("{0}{1}".format(url,getResources[qry.name].value), params=params)            
            print(req.status_code)
            #print(req.text)
            for item in req.json():
                print(item)
        except Exception as ex:
            log.error("GET: {0} ebaõnnestus {1}".format(getResources[qry.name].value, ex))

class MyPrompt(Cmd):
    def do_hello(self, args):
        """Tervitus. Ja muu info vajalik funktsiooni kasutamiseks"""
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print("Hello, %s" % name)
        
    def do_quit(self, args):
        """Sulgeb ui"""
        print("Sulgen.")
        raise SystemExit  
    
    def do_lisa(self, *args):
        """Lisab raamatu raamatukokku
        Args:
            nimi (str): Raamatu pealkiri (NOT NULL)
            autor (str): Raamatu autor (NOT NULL)
            aasta (int): Raamatu väljalaskeaasta (NOT NULL)
            tagastada (dd.mm.YYYY):Raamatu tagastamise tähtaeg
            isbn (str): Raamatu ISBN kood
            staatus (int): Raamatu staatus [0-arhiveeritud, 1-kohal, 2-laenutatud, 3-hooldus, 4-kohalkasutus]
        """
        log.info("Lisan raamatu")
        
    def do_otsi(self, *args):
        """Otsib raamatukogust
            *args (str): sisesta otsisõnad mida otsitakse andmebaasist. Kui tühi, siis terve raamatukogu
        """
        if len(args[0]) == 0:
            Raamatukoguklient.do_GET(None, query['raamatud']) 
        else:
            keys = {'key':args}
            print(keys)
            Raamatukoguklient.do_GET(None, query['otsi'], params=keys)
        log.info("Lisan raamatu") 
           
        
if __name__ == '__main__':
    
    prompt = MyPrompt() # CLI väärtustamine
    prompt.prompt = '> ' # rea tähistus
    prompt.intro = "Tere tulemast virutaalsesse raamatukokku v0.1"
    prompt.onecmd("help")
    prompt.cmdloop() # käivitab CLI, millega kasutaja suhtleb