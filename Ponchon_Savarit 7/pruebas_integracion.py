"""Pruebas de servidor local, exportación SVG y respuestas de error. Sin navegador."""
import json,threading,urllib.request,urllib.error,xml.etree.ElementTree as ET
from app import Handler,ThreadingHTTPServer

def run():
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url='http://127.0.0.1:'+str(server.server_port)
    def post(p,**opts):
        req=urllib.request.Request(url+'/api',data=json.dumps(dict(params=p,**opts)).encode(),headers={'Content-Type':'application/json'})
        return json.load(urllib.request.urlopen(req))
    try:
        assert urllib.request.urlopen(url+'/health').read()==b'ok'
        assert 'Ponchon'.encode() in urllib.request.urlopen(url).read()
        base=post({});assert base['N_entero']==12 and base['etapa_alimentacion']==6
        ET.fromstring(base['svg'])
        full=post({},full=True,limit=6);ET.fromstring(full['svg']);assert 'ΔD' in full['svg']
        r3=post({'R':3});assert r3['N_entero']==11 and r3['QC']>base['QC']
        for bad in [{'R':1},{'xB':.99},{'F':-1}]:
            try:post(bad)
            except urllib.error.HTTPError as e:assert e.code==400 and 'error' in json.load(e)
            else:raise AssertionError('Entrada inválida no rechazada')
        print('PASS: interfaz servida, caso base, cambio de reflujo, SVG y errores de API.')
    finally:server.shutdown();server.server_close()
if __name__=='__main__':run()
