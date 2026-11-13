"""Ejecutar: python3 app.py. Servidor exclusivamente local, sin dependencias."""
import argparse,json,threading,webbrowser,os
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from modelo import solve
from diagramas import diagram
ROOT=Path(__file__).resolve().parent
class Handler(BaseHTTPRequestHandler):
    def send(self,status,data,mime):
        data=data.encode('utf-8') if isinstance(data,str) else data
        self.send_response(status);self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store')
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path in ('/','/index.html'):self.send(200,(ROOT/'interfaz.html').read_bytes(),'text/html; charset=utf-8')
        elif self.path=='/health':self.send(200,'ok','text/plain')
        else:self.send(404,'No encontrado','text/plain')
    def do_POST(self):
        if self.path!='/api':return self.send(404,'{}','application/json')
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<10000:raise ValueError('Solicitud inválida')
            data=json.loads(self.rfile.read(n));p=data.get('params',{})
            if not isinstance(p,dict) or set(p)-{'F','zF','xD','xB','R'}:raise ValueError('Variables desconocidas')
            r=solve(p); limit=int(data.get('limit',r['N_entero']))
            limit=max(0,min(limit,r['N_entero']))
            r['svg']=diagram(r,bool(data.get('full',False)),limit,bool(data.get('rays',True)))
            self.send(200,json.dumps(r,allow_nan=False),'application/json')
        except (ValueError,TypeError,KeyError,OverflowError) as e:
            self.send(400,json.dumps({'error':str(e)}),'application/json')
    def log_message(self,*args):pass
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8501);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    port=int(os.environ.get('PORT',args.port))
    server=ThreadingHTTPServer(('0.0.0.0',port),Handler)
    url=f'http://0.0.0.0:{port}';print(f'Simulador: {url}\nDetener: Ctrl+C',flush=True)
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
