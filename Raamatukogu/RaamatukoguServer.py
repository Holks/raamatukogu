#!/usr/bin/env python
# encoding: utf-8
'''
RaamatukoguServer -- shortdesc

RaamatukoguServer is a description

It defines classes_and_methods

@author:     Holger Kruusla

'''
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import argparse # kasutajasõbralikum käsurea käskude parser
import re
import logging # vigade logimiseks ja muudeks
import RaamatuteAndmebaas as rmtk# andmebaasiga suhtluse moodul
import json


FORMAT = "[%(asctime)-15s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log = logging.getLogger("RaamatukoguServer") # handle andmebaasi logile
logging.basicConfig(filename="raamatukogu.log", level=logging.INFO, format=FORMAT) # kasutuse logi

    
class LocalData(object):
    records = {}
 
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        #self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    """
    --Funktsioon raamatukogu kirje(te) lisamiseks
    
    """
    def do_POST(self):
        print(self.path)
        if re.search('/api/v1/lisa', self.path):
            try:
                self._set_headers()
                lisatavad = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode())
                print(lisatavad)
                raamatud = []
                for jsonItem in lisatavad:
                    print(jsonItem)
                    raamat = (
                        jsonItem['pealkiri'],
                        jsonItem['autor'], 
                        jsonItem['isbn'], 
                        jsonItem['aasta'], 
                        jsonItem['kohaviit'], 
                        jsonItem['staatus'], 
                        jsonItem['daatum'])
                    print(raamat)
                    raamatud.append(raamat) # lisa raamat dict loetellu
                print(raamatud)
                res = rmtk.LisaAndmebaasi(raamatud)
                if res != len(lisatavad) : # funktsioon tagastas vea?                    
                    self.send_response(403) 
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()
                    
            except:
                self.send_response(403, 'Server pole saadaval')                
        else:
            self.send_response(403)
        return
    """
    --Funktsioon raamatukogu kirje saamiseks, otsimiseks
    
    """
    def do_GET(self):
        #print(self.path)
        if re.search('/api/v1/raamatud', self.path):
            try:
                res = json.dumps(rmtk.OtsiRaamatud(), default=rmtk.json_serial, sort_keys=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(res, "utf-8"))
            except:
                self.send_response(403, 'Server pole saadaval')
                
        elif re.search('/api/v1/otsi/*', self.path):
            try:
                keywords = self.path.split('=')[-1] # ürita poolitada = juurest
                print(keywords)
                res = json.dumps(rmtk.OtsiAndmebaasist(keywords), default=rmtk.json_serial, sort_keys=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(res, "utf-8"))    
            except:
                self.send_response(403, 'Server pole saadaval')
        elif re.search('/api/v1/raamat', self.path):
            try:
                raamatID = self.path.split('?')[-1] # ürita poolitada = juurest
                res = json.dumps(rmtk.KuvaRaamat(raamatID), default=rmtk.json_serial, sort_keys=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(res, "utf-8"))    
            except:
                self.send_response(403, 'Server pole saadaval')    
        else:
            self.send_response(403)
        return
    """
    --Funktsioon raamatukogusse kirje uuendamiseks
    
    """
    def do_PUT(self):
        print(self.path)
        if re.search('/api/v1/uuenda', self.path):
            try:
                raamat = self.path.split('/')[-1]                
                res = self.rfile.read(int(self.headers['Content-Length'])).decode().split('=')[-1]
                print(res)
                response = rmtk.UuendaRaamat(raamat, res) 
                print(response)
                if response is None:
                    self.send_response(500)                
                else:
                    self.send_response(200)  
                self.send_header('Content-type', 'text/html')                
                self.end_headers()
            except:
                self.send_response(403, 'Server pole saadaval')
        else:
            self.send_response(403)
        return
    """
    --Funktsioon raamatukogust kirje kustutamiseks
    
    """
    def do_DELETE(self):
        if re.search('/api/v1/eemalda/*', self.path):
            raamat = self.path.split('/')[-1] # ürita poolitada = juurest
            if rmtk.KustutaRaamat(raamat) == False:                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
            else:
                self.send_response(403)
        else:
            self.send_response(403)
        return
    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
 
    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)
 
class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
    
    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
 
    def waitForThread(self):
        self.server_thread.join()
 
  #  def addRecord(self, recordID, jsonEncodedRecord):
    #    LocalData.records[recordID] = jsonEncodedRecord
 
    def stop(self):
        self.server.shutdown()
        self.waitForThread()
 
if __name__=='__main__':    
    
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server',nargs='?', const=1, default=8080)
    parser.add_argument('ip', help='HTTP Server IP', nargs='?', const=1, default='localhost')
    args = parser.parse_args()
    log.info("Käivitan serveri -ip {0} -port {1}\n".format(args.ip,args.port)) 
    print(args.ip, args.port, args)
    try:
        server = SimpleHttpServer(args.ip, args.port) 
        server.start()
        server.waitForThread()
    except Exception as ex:
        log.error("Ei õnnestunud serverit käima panna {0} {1} ".format( type(ex), ex))