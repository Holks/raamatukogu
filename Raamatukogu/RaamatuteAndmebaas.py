#!/usr/bin/env python
# encoding: utf-8
'''
 -- shortdesc

Raamatukogu andmebaas, mis sisaldab raamatukogus saadavate raamatuid ja infot nende kohta

@author:     Holger Kruusla

@license:    MIT

@contact:    holgerkruusla@gmail.com
@deffield    updated: Updated
'''
import pymysql
import sys
import logging # vigade logimiseks ja muudeks
from enum import Enum # staatuse klass,
from cmd import Cmd
import json
from datetime import date, datetime

class RaamatuStaatus(Enum):
    arhiveeritud = 0
    kohal = 1
    laenutatud = 2
    hooldus = 3    
    kohalkasutus = 4
    
FORMAT = "[%(asctime)-15s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log = logging.getLogger("RaamatuteAndmebaas") # handle andmebaasi logile
logging.basicConfig(filename="raamatukogu.log", level=logging.INFO, format=FORMAT) # kasutuse logi

log.info("\n\tKäivitati skript ...\n")

dbServerName    = "127.0.0.1" # localhost
dbUser          = "kitsemampsel"
dbPassword      = "e6FkVoF4d3PGiEG7"
dbName          = "eclipse"
charSet         = "utf8mb4"
cusrorType      = pymysql.cursors.DictCursor 

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def LooRaamatukogu():
    '''
    -- Loob raamatukogu tabeli kujul

    '''
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName,
                             charset=charSet,                             
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            log.info("Üritan luua raamatukogu") # loon raamatukogu
            sql = "CREATE TABLE IF NOT EXISTS raamatukogu "
            sql += "(`id` int(20) NOT NULL AUTO_INCREMENT,"
            sql += "`title` varchar(255) COLLATE utf8_bin NOT NULL,"
            sql += "`author` varchar(255) COLLATE utf8_bin NOT NULL,"
            sql += "`isbn` varchar(50) COLLATE utf8_bin,"
            sql += "`published` varchar(10) COLLATE utf8_bin NOT NULL,"
            sql += "`inventory_no` varchar(255) COLLATE utf8_bin,"
            sql += "`status` int(1) NOT NULL,"
            sql += "`return_datum` varchar(255),"
            sql += "PRIMARY KEY (`id`),FULLTEXT idx (title, author, isbn)) AUTO_INCREMENT=1;"
            
            cursor.execute(sql)    
        conn.commit()
    except Exception as ex:
        #log.info("Lisan tabeli {0} kujul {1} ".format( "Raamatukogu", sql))
        log.error("Ei õnnestunud tabeli loomine {0} {1} ".format( type(ex), ex)) # logi veateade
        print(ex) # ja prindi ka konsooli
    finally:
        conn.close()

def LisaRaamat(raamat):
    '''
    -- Lisab ühe raamatu andmebaasi
    '''
    log.info("Üritan lisada andmebaasi kirjet {0}".format(raamat))
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    try:
        with conn.cursor() as cursor:
            # Create a new record
            # (title, author, isbn, published, inventory_no, status, return_datum) 
            sql = """INSERT IGNORE INTO `raamatukogu` VALUES ('',%s, %s, %s, %s, %s, %s, %s);"""
            
            cursor.execute(sql, raamat) # rakenda muudatus
        conn.commit()
    except Exception as ex:
        conn.rollback()
        log.error("Ei õnnestunud lisamine: {0}:{1}".format( type(ex), ex)) # logi veateade
        print(ex) # ja prindi ka konsooli
    finally:
        conn.close() # sule yhendus

def KustutaRaamat(raamat):
    '''
    -- Kustutab ühe raamatu andmebaasi
    '''
    try:
        conn = pymysql.connect(host=dbServerName,
                                 user=dbUser,
                                 password=dbPassword,
                                 db=dbName)
        cur = conn.cursor()
        sql = "DELETE FROM raamatukogu WHERE id = %s" % (raamat,)
        print(sql)
        cur.execute(sql)
        conn.commit()
        return False
    except Exception as ex:
        return ex    

def OtsiAndmebaasist(*args):
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    cur = conn.cursor()
    sql = """SELECT * FROM raamatukogu WHERE MATCH (title,author,isbn) AGAINST (%s IN NATURAL LANGUAGE MODE);"""    
    cur.execute(sql, (args,))
    raamatud = cur.fetchall()
    print(raamatud)
    nimekiri = []
    for raamat in raamatud:        
        nimekiri.append({
        'id':raamat[0],
        'pealkiri':raamat[1],
        'autor':raamat[2],    
        'isbn':raamat[3],
        'aasta':raamat[4],
        'kohaviit':raamat[5],
        'staatus':raamat[6],
        'daatum':raamat[7]
         })
    return nimekiri

def OtsiRaamatud():
    print("otsi raamatud")
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    cur = conn.cursor()
    cur.execute('SELECT * FROM raamatukogu')
    raamatud = cur.fetchall()
    nimekiri = []
    for raamat in raamatud:        
        nimekiri.append({
        'id':raamat[0],
        'pealkiri':raamat[1],
        'autor':raamat[2],    
        'isbn':raamat[3],
        'aasta':raamat[4],
        'kohaviit':raamat[5],
        'staatus':raamat[6],
        'daatum':raamat[7]
         })
    return nimekiri

def KuvaRaamat(raamatID):
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    try:
        with conn.cursor() as cur:    
            cur.execute("SELECT * FROM raamatukogu WHERE id=%s", (raamatID))
            raamat = cur.fetchone()
    except Exception as ex:
        log.error("Ei õnnestunud kuvamine: {0}:{1}".format( type(ex), ex)) # logi veateade
        print(ex) # ja prindi ka konsooli    
    finally:
        conn.close() # sule yhendus
        raamat = {
        'id':raamat[0],
        'pealkiri':raamat[1],
        'autor':raamat[2],    
        'isbn':raamat[3],
        'aasta':raamat[4],
        'kohaviit':raamat[5],
        'staatus':raamat[6],
        'daatum':raamat[7]
         }
        return raamat
    return ex

def UuendaRaamat(raamatID, daatum):
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    try:
        try:
            print(daatum)
            if daatum != "":
                print("laenutamine")
                kuup2ev = daatum.strip().split('.')
                kuup2ev = '{0}-{1}-{2}'.format(kuup2ev[2],kuup2ev[1],kuup2ev[0]) 
                staatus = 2
            else:
                kuup2ev = "0000-00-00" # kuupäeva None vorming andmebaasis
                print("tagastamine")
                staatus = 1
        except Exception as ex:
            log.error("Kuupäev vales vormingus: {0} - {1}:{2}".format(daatum, type(ex), ex)) # logi veateade
            return
        with conn.cursor() as cur: 
            sql = 'UPDATE raamatukogu SET return_datum = %s, status = %s WHERE id = %s'
            cur.execute(sql,(kuup2ev, staatus, raamatID))
            conn.commit()
    except Exception as ex:
        conn.rollback()
        conn.close()
        log.error("Ei õnnestunud lisamine: {0}:{1}".format( type(ex), ex)) # logi veateade
        return None
    finally:
        raamat = KuvaRaamat(raamatID) # esita tulemus kasutajale
        conn.close() # sule yhendus
        return raamat
    
def LisaAndmebaasi(raamatud):    
    log.info("Üritan lisada andmebaasi {0} kirjet".format(len(raamatud)))
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    try:
        with conn.cursor() as cursor:
            sql = """INSERT IGNORE INTO raamatukogu VALUES ('',%s, %s, %s, %s, %s, %s, %s);"""
            nres = cursor.executemany(sql, raamatud) # rakenda muudatus          
            print(nres)                       
        conn.commit()
    except pymysql.Warning as e:
        log.error("Andmebaasi sisestuse hoiatus: {0}".format( e)) # logi veateade
    except pymysql.MySQLError as e:
        log.error("Ei õnnestunud lisamine: {0}:{1}".format( type(e), e)) # logi veateade    
    except Exception as ex:
        conn.rollback()
        conn.close() 
        log.error("Ei õnnestunud lisamine: {0}:{1}".format( type(ex), ex)) # logi veateade
        return True
    finally:
        conn.close() # sule yhendus
        if nres == 0: 
            return False
        else:
            return nres
    
def try_parse_int(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val        

def RaamatuStaatusKontroll(staatus):
    
    if staatus in RaamatuStaatus.__members__:
        staatus = RaamatuStaatus[staatus].value
    else:
        staatus = RaamatuStaatus['kohal'].value
    return staatus     

class MyPrompt(Cmd):
    """
    Andmebaasiga suhtlemiseks käsurealt
    """
    def do_quit(self):
        """Sulgeb ui"""
        print("Täname\nKülastage meid jälle")
        raise SystemExit
    
    def do_otsi(self, *args):
        """Otsib raamatukogust
            *args (str): sisesta otsisõnad mida otsitakse andmebaasist. Kui tühi, siis terve raamatukogu
        """
        if len(args[0]) == 0:
            for raamat in OtsiRaamatud():
                print(json.dumps(raamat,default=json_serial))
        else:
            for raamat in OtsiAndmebaasist(args):
                print(json.dumps(raamat,default=json_serial))
            
if __name__ == '__main__':
    raamatud = []
    
    for file in sys.argv[1:]:
        print(file)
        for i,rida in enumerate(open(file)): # käin läbi terve faili rea kaupa
            try:
                rida = rida.split(',') # NB! probleemiks komaga andmeväljad, nt pealkirja vms  
                pealkiri = rida[0]
                aasta = rida[1]
                isbn = rida[2]
                autor = rida[3] 
                staatus = RaamatuStaatusKontroll(rida[4]) # kontrollime staatust, et sisestaja pole teinud viga
                koht = rida[5] # siia võiks sisestada ka kohaviida kontrolli
                try:
                    kuup2ev = rida[6].strip().split('.')
                    kuup2ev = '{0}-{1}-{2}'.format(kuup2ev[2],kuup2ev[1],kuup2ev[0]) 
                except:
                    kuup2ev = ""
                    if len(rida[6]) > 1 : # kui sisendis on midagi, kui parses ei saanud hakkama, siis veateade
                        log.error("Tähtaja kirje vigane failis {0} rida {1}\n".format(file,i))
                log.info("Leidsin raamatu {0}, {1}, {2}, {3}, {4}, {5}, {6}\n".format(pealkiri, autor, isbn, aasta, koht, staatus,  kuup2ev))
                raamat = (pealkiri,
                        autor, 
                        isbn, 
                        aasta, 
                        koht, 
                        staatus, 
                        kuup2ev)
                raamatud.append(raamat) # lisa raamat dict loetellu
            except:
                log.error("Vigane kirje failis {0} rida {1}\n".format(file,i))
    LooRaamatukogu()       
    LisaAndmebaasi(raamatud) # lisab saadud raamatud andmebaasi
    for item in OtsiRaamatud():
        print(item)
    prompt = MyPrompt() # CLI väärtustamine
    prompt.prompt = '> ' # rea tähistus
    prompt.intro = "Tere tulemast raamatukogu andmebaasi ..."
    prompt.onecmd("help")
    prompt.cmdloop() # käivitab CLI, millega kasutaja suhtleb  
    
    