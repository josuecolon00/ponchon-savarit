"""Ejecutar: python3 app.py. Servidor exclusivamente local, sin dependencias."""
import argparse,json,threading,webbrowser,os,base64,io
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from modelo import solve
from diagramas import diagram
from openpyxl import Workbook, load_workbook
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
        if self.path not in ('/api','/api/export-xlsx','/api/import-xlsx'):return self.send(404,'{}','application/json')
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<10_000_000:raise ValueError('Solicitud inválida')
            data=json.loads(self.rfile.read(n))
            if self.path=='/api/import-xlsx':
                raw=base64.b64decode(data.get('file',''),validate=True); wb=load_workbook(io.BytesIO(raw),data_only=True,read_only=True); ws=wb['Entradas']; vals={str(row[0].value):row[1].value for row in ws.iter_rows(min_row=2) if row[0].value}; wb.close(); self.send(200,json.dumps({'params':{k:float(vals[k]) for k in ('F','zF','xD','xB','R') if k in vals},'components':{k:vals.get(k) for k in ('componente_1','componente_2','Tb1_C','Tb2_C')}}),'application/json'); return
            p=data.get('params',{})
            if not isinstance(p,dict) or set(p)-{'F','zF','xD','xB','R'}:raise ValueError('Variables desconocidas')
            r=solve(p); p=r['entradas']
            if self.path=='/api/export-xlsx':
                wb=Workbook(); ws=wb.active; ws.title='Entradas'; ws.append(['Variable','Valor','Unidad / descripción'])
                comp=data.get('components',{})
                for row in [('componente_1',comp.get('name1','Benceno'),'Nombre'),('componente_2',comp.get('name2','Tolueno'),'Nombre'),('Tb1_C',comp.get('tb1',80.1),'°C'),('Tb2_C',comp.get('tb2',110.6),'°C'),('F',p['F'],'kmol/h'),('zF',p['zF'],'fracción molar del componente 1'),('xD',p['xD'],'fracción molar del componente 1'),('xB',p['xB'],'fracción molar del componente 1'),('R',p['R'],'L0/D')]: ws.append(list(row))
                ws2=wb.create_sheet('Balances'); ws2.append(['Magnitud','Valor','Unidad'])
                for row in [('D',r['D'],'kmol/h'),('B',r['B'],'kmol/h'),('L0',r['L0'],'kmol/h'),('V1',r['V1'],'kmol/h'),('hF',r['hF'],'kJ/kmol'),('hD',r['hD'],'kJ/kmol'),('hB',r['hB'],'kJ/kmol'),('QC',r['QC'],'kJ/h'),('QR',r['QR'],'kJ/h'),('DeltaD',r['deltaD'],'kJ/kmol'),('DeltaB',r['deltaB'],'kJ/kmol'),('Residuo energia',r['res_energia'],'kJ/h')]: ws2.append(list(row))
                ws3=wb.create_sheet('Etapas'); ws3.append(['Etapa','x líquido','y vapor','T °C','L kmol/h','V kmol/h','Sección'])
                for a in r['etapas']: ws3.append([a['n'],a['x'],a['y'],a['T'],a.get('L'),a.get('V'),a['seccion']])
                ws4=wb.create_sheet('Procedimiento'); ws4.append(['Paso','Descripción']);
                for row in [(1,'Balance global: F = D + B'),(2,'Balance de componente 1: F zF = D xD + B xB'),(3,'Cálculo de entalpías de alimentación, destilado y fondos'),(4,'Cálculo de cargas térmicas QC y QR'),(5,'Construcción gráfica Ponchon–Savarit y conteo de etapas'),(6,'Revisar cierre de balances y supuestos del modelo')]: ws4.append(list(row))
                for sh in wb.worksheets:
                    sh.freeze_panes='A2'; sh.column_dimensions['A'].width=28; sh.column_dimensions['B'].width=24; sh.column_dimensions['C'].width=34
                bio=io.BytesIO(); wb.save(bio); self.send(200,base64.b64encode(bio.getvalue()).decode(),'text/plain; charset=utf-8'); return
            limit=int(data.get('limit',r['N_entero']))
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
