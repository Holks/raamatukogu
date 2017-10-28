#!/usr/bin/env python
# encoding: utf-8
'''
RaaamtukoguKlient -- shortdesc

Raamatukogu kasutaja liides raamatute otsimiseks, t�htaegade vaatamiseks jne.

It defines classes_and_methods

@author:     Holger Kruusla
'''
import requests
import logging
from cmd import Cmd
from enum import Enum
import json
import RaamatuteAndmebaas as rmtk # raamatu staatuse enum

url='http://localhost:8080' # url definitsioon, peaks kasutama seadete 
FORMAT = "[%(asctime)-15s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log = logging.getLogger("RaamtukoguKlient") # handle andmebaasi logile
logging.basicConfig(filename="raamatukogu.log", level=logging.INFO, format=FORMAT) # kasutuse logi
raamatukirje = "id\tpealkiri\tautor\tisbn\tväljalaskeaasta\tkohaviit\tstaatus\ttagastustähtaeg" # CLI kuva päis

class getResources(Enum):
    raamatud = '/api/v1/raamatud'
    raamat = '/api/v1/raamat'
    otsi = '/api/v1/otsi'
    lisa = '/api/v1/lisa'
    uuenda = '/api/v1/uuenda'
    eemalda = '/api/v1/eemalda'

class query(Enum):
    raamatud = 0
    raamat = 1
    otsi = 2
    lisa = 3
    uuenda = 4
    eemalda = 5
    
class Raamatukoguklient():
    def do_POST(self, qry, DATA, params=""):
        try:
            req = requests.post("{0}{1}".format(url,getResources[qry.name].value), data=DATA, params=params)
            log.info("POST: {0} õnnestus".format(getResources[qry.name].value))
            if req.status_code == 200:
                print("Andmebaasi lisatud")
                log.info("POST: lisatud data='{0}', params='{1}'".format(DATA, params))
            else:
                log.error("POST: ebaõnnestus data='{0}', params='{1}' -  response {2}".format(DATA, params, req.status_code))            
        except Exception as ex:
            log.error("POST: {0} ebaõnnestus veateatega {1}".format(DATA, ex))
        
    def do_GET(self, qry, params=""):
        try:
            if qry.name not in query.__members__:
                raise ValueError
            req = requests.get("{0}{1}".format(url,getResources[qry.name].value), params=params)               
            #print(req.json())
            if req.status_code == 200:
                log.info("GET: {0} õnnestus".format(getResources[qry.name].value)) 
                return req.json()
        except Exception as ex:
            log.error("GET: {0} ebaõnnestus {1}".format(getResources[qry.name].value, ex))
        return True
    
    def do_DELETE(self, qry, raamatID):
        try:
            req = requests.delete("{0}{1}/{2}".format(url,getResources[qry.name].value,raamatID))       
            if req.status_code == 200:                
                print("Raamat kustutatud")
            else:
                print("Midagi läks valesti")
                log.error("DELETE: {0} ebaõnnestus {1}".format(getResources[qry.name].value, raamatID))
        except Exception as ex:
            log.error("DELETE: {0} ebaõnnestus {1}".format(getResources[qry.name].value, ex))
            
    def do_PUT(self, qry, raamatID, params=""):
        try:
            req = requests.put("{0}{1}/{2}".format(url,getResources[qry.name].value,raamatID), data=params)
            if req.status_code == 200:                
                print("Raamatu saatus uuendatud")
                return False
            else:
                print("Ei õnnestunud")
                return True
        except Exception as ex:
            log.error("PUT: {0} ebaõnnestus {1}".format(getResources[qry.name].value, ex))
            return True
        
class MyPrompt(Cmd):
    def do_hello(self, args):
        """Tervitus. Ja muu info vajalik funktsiooni kasutamiseks"""
        if len(args) == 0:
            nimi = 'Kasutaja'
        else:
            nimi = args
        print("Tere, %s" % nimi)
        
    def do_quit(self, args):
        """Sulgeb ui"""
        print("Sulgen.")
        raise SystemExit  
    
    def do_lisa(self, fail):
        """Lisab raamatu/raamatud raamatukokku
        ======================================================
        --Lisab raamatukokku ükshaaval või failist mitu korraga
        --NB! puudub eriline sisestuse kt e raamatu kirje korrektsus jääb kasutaja teha
        Args:
            file(str): faili (csv) aadress, kus raamatud veergudega
                -pealkiri,ilmumisaasta,isbn,autor,staatus,kohaviit,tähtaeg
            nimi (str): Raamatu pealkiri (NOT NULL)
            autor (str): Raamatu autor (NOT NULL)
            aasta (int): Raamatu väljalaskeaasta (NOT NULL)
            tagastada (dd.mm.YYYY): Raamatu tagastamise tähtaeg
            isbn (str): Raamatu ISBN kood
            staatus (int): Raamatu staatus [0-arhiveeritud, 1-kohal, 2-laenutatud, 3-hooldus, 4-kohalkasutus]
        """
        if len(fail) == 0:
            print("Sisestame uue raamatukirje andmebaasi")
            print("""nimi (str): Raamatu pealkiri (ei tohi olla tühi, puudumisel '-')
            autor (str): Raamatu autor (ei tohi olla tühi, puudumisel '-')
            aasta (int): Raamatu väljalaskeaasta (ei tohi olla tühi, puudumisel '-')
            tagastada (dd.mm.YYYY): Raamatu tagastamise tähtaeg
            isbn (str): Raamatu ISBN kood
            staatus (int): Raamatu staatus [0-arhiveeritud, 1-kohal, 2-laenutatud, 3-hooldus, 4-kohalkasutus]
            kohaviit (str): Raamatu füüsiline kohaviit raamatukogus, NB peab olema unikaalne kirje
            """)
            autor = input("Sisesta raamatu autor ")
            if autor == "":
                print("Sisestusviga, katkestan\nAbi saamiseks: help lisa")
                return
            aasta = input("Sisesta raamatu väljalaskeaasta ")
            if aasta == "":
                print("Sisestusviga, katkestan\nAbi saamiseks: help lisa")
                return
            pealkiri = input("Sisesta raamatu pealkiri ")
            if pealkiri == "":
                print("Sisestusviga, katkestan\nAbi saamiseks: help lisa")
                return
            isbn = input("Sisesta raamatu isbn ")
            staatus = input("Sisesta raamatu staatus ")
            kohaviit = input("Sisesta raamatu kohaviit raamatukogus ")
            if kohaviit == "":
                print("Sisestusviga, katkestan\nAbi saamiseks: help lisa")
                return
            daatum = input("Sisesta raamatu laenutustähtaeg ")
            raamat = {
                'pealkiri':pealkiri,
                'autor':autor,
                'aasta':aasta,
                'isbn':isbn,
                'staatus':staatus,
                'kohaviit':kohaviit,
                'daatum':daatum}
            kinnitus = input("Sisestan raamatu {0} andmebaasi [y/n]".format(raamat)).lower()
            if kinnitus == "y":
                Raamatukoguklient.do_POST(None, query['lisa'], json.dumps(raamat))
                print("Raamatu sisestus edukas") 
            else:
                print("Katkestan sisestuse")
        else:
            raamatud = []
            with open(fail.strip('"')) as fail:
                for i,rida in enumerate(fail): # käin läbi terve faili rea kaupa
                    try:
                        rida = rida.split(',') # NB! probleemiks komaga andmeväljad, nt pealkirja vms  
                        pealkiri = rida[0]
                        aasta = rida[1]
                        isbn = rida[2]
                        autor = rida[3] 
                        staatus = rmtk.RaamatuStaatusKontroll(rida[4])
                        
                        kohaviit = rida[5] # siia võiks sisestada ka kohaviida kontrolli
                        try:
                            daatum = rida[6].strip().split('.')
                            daatum = '{0}-{1}-{2}'.format(daatum[2],daatum[1],daatum[0]) 
                        except:
                            daatum = ""
                            if len(rida[6]) > 1 : # kui sisendis on midagi, kui parses ei saanud hakkama, siis veateade
                                log.error("Tähtaja kirje vigane failis {0} rida {1}\n".format(fail,i))
                        log.info("Leidsin raamatu {0}, {1}, {2}, {3}, {4}, {5}, {6}\n".format(pealkiri, autor, isbn, aasta, kohaviit, staatus,  daatum))
                        raamat = {
                            'pealkiri':pealkiri,
                            'autor':autor,
                            'aasta':aasta,
                            'isbn':isbn,
                            'staatus':staatus,
                            'kohaviit':kohaviit,
                            'daatum':daatum}
                        raamatud.append(raamat) # lisa raamat dict loetellu
                    except Exception as ex:
                        print("Sisestusviga {0}, katkestan\nAbi saamiseks: help lisa".format(ex))
                        log.error("Vigane kirje failis {0} rida {1}\n".format(fail,i))
                Raamatukoguklient.do_POST(None, query['lisa'], json.dumps(raamatud))
        log.info("Lisan raamatu")
        
    def do_laenuta(self, raamatID):
        """Laenuta raamat
        ======================================================
        raamatId (int): raamatu id (andmebaasi võtme veerg)
        daatum (dd.mm.YYYY): Raamatu tagastamise tähtaeg
        return: laenutatud raamatu andmebaasi rida v sellist raamatut ei leitud
        """
        if raamatID == "":
            raamatID = input("Sisesta laenutatava raamatu id (triipkood)")
        raamat = Raamatukoguklient.do_GET(None, query['raamat'], raamatID)
        try:
            rmt =  """{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}""".format(
                    raamat['id'],
                    raamat['pealkiri'],
                    raamat['autor'],
                    raamat['isbn'],
                    raamat['aasta'],
                    raamat['kohaviit'],
                    raamat['staatus'],
                    raamat['daatum'])
            if int(raamat['staatus']) == 1:
                daatum = input("Sisesta tagastuskuupäev ")
                keys = {'daatum':daatum}
                if not Raamatukoguklient.do_PUT(None, query['uuenda'], raamatID, keys):
                    raamat = Raamatukoguklient.do_GET(None, query['raamat'], raamatID)
                    print("Laenutatud {0}".format(rmt))
                else:
                    print("Hetkel raamat pole saadaval")
                log.info("Uuendan andmebaasi kirjet: LAENUTUS {0} -> tähtaeg {1}".format(raamatID,daatum))
            elif int(raamat['staatus']) == 2:
                print("Raamat\n-{0}\non juba väljalaenutatud".format(rmt))
            else:                
                print("Raamat\n\t{0}\non staatusega:{1}".format(rmt, rmtk.RaamatuStaatus[int(raamat['staatus'])].name))
        except Exception as ex:
            log.error("Laenutamine: {0} ebaõnnestus {1}".format(raamatID, ex))
        
        
    def do_tagasta(self, raamatID):
        """Tagasta raamat
        ======================================================
        raamatId (int): raamatu id (andmebaasi võtme veerg)
        return: laenutatud raamatu andmebaasi rida v sellist raamatut ei leitud
        """
        if raamatID == "":
            raamatID = input("Sisesta tagastatava raamatu id (triipkood)")
            
        keys = {'daatum':""}
        try:
            if not Raamatukoguklient.do_PUT(None, query['uuenda'], raamatID, keys):
                raamat = Raamatukoguklient.do_GET(None, query['raamat'], raamatID)
                rmt =  """{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}""".format(
                        raamat['id'],
                        raamat['pealkiri'],
                        raamat['autor'],
                        raamat['isbn'],
                        raamat['aasta'],
                        raamat['kohaviit'],
                        raamat['staatus'],
                        raamat['daatum'])
                print("Raamat\n\t{0}\ntagastatud".format(rmt))
            else:
                print("Tagastamine ei õnnestunud, proovi uuesti või ...")
            log.info("Uuendan andmebaasi kirjet: TAGASTUS {0}".format(raamatID)) 
        except Exception as ex:
            log.error("Tagastamine: {0} ebaõnnestus {1}".format(raamatID, ex))
    def do_kustuta(self, raamatID):
        """Otsib raamatukogust
        ======================================================
            raamatID (int): sisestades raamatu id kustutatakse vastav kirje andmebaasist.
        """
        if raamatID == "":
            raamatID = input("Sisesta kustutava raamatu id (triipkood)")
        try:
            raamat = Raamatukoguklient.do_GET(None, query['raamat'], raamatID)
            rmt =  """{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}""".format(
                    raamat['id'],
                    raamat['pealkiri'],
                    raamat['autor'],
                    raamat['isbn'],
                    raamat['aasta'],
                    raamat['kohaviit'],
                    raamat['staatus'],
                    raamat['daatum'])
            print(rmt)
            kinnitus = input("Kustutan raamatu {0} [y/n]".format(raamatID)).lower()
            if kinnitus == 'y':
                Raamatukoguklient.do_DELETE(None, query['eemalda'], raamatID)
                print("Eemaldasin raamatu {0}".format(raamatID))
        except Exception as ex:
            print("Eemaldamine ebaõnnestus veaga {0}\nProovi otsi ja kontrolli ID-d".format(ex))
            log.error("Eemaldamine ebaõnnestus veaga {0}\n".format(ex))
        
    def do_otsi(self, *args):
        """Otsib raamatukogust
        ======================================================
            *args (str): sisesta otsisõnad mida otsitakse andmebaasist. Kui tühi, siis kuvatakse terve raamatukogu
        """
        log.info("Otsin raamatut {0}".format(*args))
        if len(args[0]) == 0:
            res = Raamatukoguklient.do_GET(None, query['raamatud'])
        else:
            keys = {'key':args}
            res  = Raamatukoguklient.do_GET(None, query['otsi'], params=keys)
        try:
            print(raamatukirje)
            for item in res:
                print("""{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}""".format(
                    item['id'],
                    item['pealkiri'],
                    item['autor'],
                    item['isbn'],
                    item['aasta'],
                    item['kohaviit'],
                    item['staatus'],
                    item['daatum']))
            #print(json.dumps(res, indent=2))
        except:
            pass
if __name__ == '__main__':
    
    prompt = MyPrompt() # CLI väärtustamine
    prompt.prompt = '> ' # rea tähistus
    prompt.intro = "Tere tulemast virutaalsesse raamatukokku v0.1"
    prompt.onecmd("help")
    prompt.cmdloop() # käivitab CLI, millega kasutaja suhtleb