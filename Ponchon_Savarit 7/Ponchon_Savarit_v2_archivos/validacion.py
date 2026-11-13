"""Ruta independiente: balances algebraicos + raíces por bisección, sin puntos Delta.
Comparte únicamente la tabla y propiedades constitutivas con el simulador.
"""
import json,csv
from pathlib import Path
from modelo import solve,DEFAULT,X,Y,T

def lin(v,xx,yy):
    for a,b,c,d in zip(xx,xx[1:],yy,yy[1:]):
        if a<=v<=b: return c+(v-a)*(d-c)/(b-a)
    raise ValueError('Fuera de tabla')
def hl(x): return (136*x+159*(1-x))*lin(x,X,T)
def hv(y): return y*(136*80.1+30720)+(1-y)*(159*110.6+33180)
def bisect(f,a,b):
    fa=f(a)
    if fa*f(b)>0: raise ValueError('Raíz sin encerrar')
    for _ in range(80):
        m=(a+b)/2; fm=f(m)
        if fa*fm<=0: b=m
        else: a=m; fa=fm
    return (a+b)/2

def independent(p):
    F,z,xd,xb,R=[p[k] for k in ('F','zF','xD','xB','R')]
    # Se calcula primero B, de manera independiente de la fórmula del simulador.
    B=F*(xd-z)/(xd-xb); D=F-B; reflux=R*D
    qc=(D+reflux)*hv(xd)-(D+reflux)*hl(xd)
    qr=qc+D*hl(xd)+B*hl(xb)-F*hl(z)
    rows=[]; y=xd; prev=xd; feed=None
    for n in range(1,1001):
        x=bisect(lambda v:lin(v,X,Y)-y,0,1)
        if feed is None and x<=z: feed=n
        rows.append(dict(n=n,x=x,y=y))
        if x<=xb: break
        if feed is None:
            def residual(v):
                V=D*(xd-x)/(v-x); L=V-D
                return V*hv(v)-L*hl(x)-D*hl(xd)-qc
        else:
            def residual(v):
                V=B*(x-xb)/(v-x); L=V+B
                return L*hl(x)+qr-V*hv(v)-B*hl(xb)
        prev=x; y=bisect(residual,x+1e-10,lin(x,X,Y))
    else: raise ValueError('No convergió')
    return dict(D=D,B=B,L0=reflux,QC=qc,QR=qr,N_grafico=n-1+(prev-xb)/(prev-x),etapa_alimentacion=feed,etapas=rows)

def run():
    main=solve(); other=independent(DEFAULT)
    delta={k:abs(main[k]-other[k]) for k in ('D','B','L0','QC','QR','N_grafico','etapa_alimentacion')}
    dx=max(abs(a['x']-b['x']) for a,b in zip(main['etapas'],other['etapas']))
    assert len(main['etapas'])==len(other['etapas'])==12
    assert dx<1e-10 and max(delta.values())<1e-6
    assert main['etapa_alimentacion']==6
    assert abs(main['res_energia'])<1e-6
    # Conservación local en cada plato completo, incluida la alimentación.
    rows=main['etapas']; residuals=[]
    for i,row in enumerate(rows[:-1]):
        prev=rows[i-1] if i else None
        Lin=prev['L'] if prev else main['L0']
        Vin= row['V']; Lout=row['L']
        Vout=prev['V'] if prev else main['V1']
        xin=prev['x'] if prev else DEFAULT['xD']
        feed=DEFAULT['F'] if row['n']==main['etapa_alimentacion'] else 0
        mass=Lin+Vin+feed-Lout-Vout
        comp=Lin*xin+Vin*row['y_siguiente']+feed*DEFAULT['zF']-Lout*row['x']-Vout*row['y']
        energy=Lin*hl(xin)+Vin*hv(row['y_siguiente'])+feed*main['hF']-Lout*hl(row['x'])-Vout*hv(row['y'])
        assert abs(mass)<1e-8 and abs(comp)<1e-8 and abs(energy)<1e-6
        residuals.append(dict(etapa=row['n'],materia=mass,benceno=comp,energia=energy))
    changes=[]
    for R in [2,2.5,3,4]:
        r=solve(dict(R=R)); o=independent(dict(DEFAULT,R=R))
        assert abs(r['N_grafico']-o['N_grafico'])<1e-9
        changes.append(dict(R=R,N=r['N_grafico'],N_entero=r['N_entero'],alimentacion=r['etapa_alimentacion'],QC_kW=r['QC']/3600,QR_kW=r['QR']/3600))
    assert all(a['N']>b['N'] and a['QC_kW']<b['QC_kW'] for a,b in zip(changes,changes[1:]))
    scaled=solve(dict(F=200))
    assert abs(scaled['QC']-2*main['QC'])<1e-6 and scaled['N_grafico']==main['N_grafico']
    rejected=0
    for p in [dict(F=0),dict(F=-1),dict(R=1),dict(R=-2),dict(zF=.99),dict(xB=.96),dict(xD=1),dict(F=float('nan'))]:
        try: solve(p)
        except ValueError: rejected+=1
        else: raise AssertionError(f'No se rechazó {p}')
    out=dict(comparacion={k:dict(simulador=main[k],independiente=other[k],diferencia=delta[k]) for k in delta},max_error_x=dx,balances_platos=residuals,sensibilidad=changes,pruebas_invalidas=rejected)
    dest=Path(__file__).parent/'resultados';dest.mkdir(exist_ok=True)
    (dest/'validacion.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    with (dest/'etapas.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['n','x','y','T','h','H','seccion']);w.writeheader()
        w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
