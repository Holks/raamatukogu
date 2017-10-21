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
from dateutil.parser import parse 

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

dbServerName    = "localhost"
dbUser          = "kitsemampsel"
dbPassword      = "e6FkVoF4d3PGiEG7"
dbName          = "raamatukogu"
charSet         = "utf8mb4"
cusrorType      = pymysql.cursors.DictCursor 

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
            sql = "CREATE TABLE IF NOT EXISTS Raamatukogu "
            sql += "(`id` int(20) NOT NULL AUTO_INCREMENT,"
            sql += "`title` varchar(255) COLLATE utf8_bin NOT NULL,"
            sql += "`author` varchar(255) COLLATE utf8_bin NOT NULL,"
            sql += "`isbn` varchar(50) COLLATE utf8_bin,"
            sql += "`published` varchar(10) COLLATE utf8_bin NOT NULL,"
            sql += "`inventory_no` varchar(255) COLLATE utf8_bin,"
            sql += "`status` int(1) NOT NULL,"
            sql += "`return_datum` varchar(255),"
            sql += "PRIMARY KEY (`id`)) AUTO_INCREMENT=1;"
            
            cursor.execute(sql)    
        conn.commit()
    except Exception as ex:
        #log.info("Lisan tabeli {0} kujul {1} ".format( "Raamatukogu", sql))
        log.error("Ei õnnestunud tabeli loomine {0} {1} ".format( type(ex), ex)) # logi veateade
        print(ex) # ja prindi ka konsooli
    finally:
        conn.close()

def LisaRaamat(raamatud):
    '''
    -- Lisab ühe raamatu andmebaasi
    '''
    pass 

def LisaAndmebaasi(raamatud):
    log.info("Üritan lisada andmebaasi {0} kirjet".format(len(raamatud)))
    conn = pymysql.connect(host=dbServerName,
                             user=dbUser,
                             password=dbPassword,
                             db=dbName)
    cur = conn.cursor()
    cur.execute("SELECT * FROM raamatukogu")
    
    print(cur.fetchall())
    try:
        with conn.cursor() as cursor:
            # Create a new record
            # (title, author, isbn, published, inventory_no, status, return_datum) 
            sql = """INSERT IGNORE INTO `raamatukogu` VALUES ('',%s, %s, %s, %s, %s, %s, %s);"""
            
            cursor.executemany(sql, raamatud) # rakenda muudatus
        conn.commit()
    except Exception as ex:
        #conn.rollback()
        log.error("Ei õnnestunud lisamine: {0}:{1}".format( type(ex), ex)) # logi veateade
        print(ex) # ja prindi ka konsooli
    finally:
        conn.close() # sule yhendus
        
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
    print('q+CR väljumiseks, jne\n')
    while True:
        cmd = input()
        log.info("Kasutaja sisestas {0}".format(cmd))
        if cmd == 'q':
            break
        elif cmd == 'n':
            print("Sisest uus raamat")
        elif cmd == 'newD':
            print("Sisest uus raamat")
            LooRaamatukogu()
        elif cmd == 'printD':
            print("Sisest uus raamat")
        elif cmd == 'n':
            print("Sisest uus raamat")    
    
    