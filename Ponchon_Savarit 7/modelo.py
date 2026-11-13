"""Ponchon-Savarit: benceno/tolueno a 101.325 kPa. Solo biblioteca estándar."""
import math
from bisect import bisect_right
X = [0,.05,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,1]
Y = [0,.115,.209,.376,.511,.623,.714,.790,.854,.910,.958,.980,1]
T = [110.6,108.8,106.9,103.3,99.9,96.8,93.9,91.2,88.6,86.1,83.5,82.1,80.1]
DEFAULT = dict(F=100.,zF=.4,xD=.95,xB=.05,R=2.5)
A=159*110.6+33180
C=136*80.1+30720-A

def interp(v, absc, vals):
    if not math.isfinite(v) or v < -1e-12 or v > 1+1e-12:
        raise ValueError('Composición fuera de [0,1]; no se extrapola.')
    v=min(1,max(0,v)); i=min(len(absc)-2,max(0,bisect_right(absc,v)-1))
    return vals[i]+(v-absc[i])*(vals[i+1]-vals[i])/(absc[i+1]-absc[i])

def temp(x): return interp(x,X,T)
def eq(x): return interp(x,X,Y)
def inv(y): return interp(y,Y,X)
def h(x): return (159-23*x)*temp(x)
def H(y): return A+C*y

def ray(x,dx,dh):
    """Intersección exacta de la recta (x,h(x))-Delta con H(y)=A+C*y."""
    hx=h(x); den=(dh-hx)-C*(dx-x)
    if abs(den)<1e-9: raise ValueError('Recta operativa paralela a la curva de vapor.')
    return (x*(dh-hx)+(A-hx)*(dx-x))/den

def solve(params=None):
    p=DEFAULT.copy()
    if params: p.update(params)
    F,z,xd,xb,R=[float(p[k]) for k in ('F','zF','xD','xB','R')]
    p=dict(F=F,zF=z,xD=xd,xB=xb,R=R)
    if not all(math.isfinite(v) for v in p.values()): raise ValueError('Todos los datos deben ser finitos.')
    if F<=0 or R<0: raise ValueError('Se requiere F > 0 y R >= 0.')
    if not 0<xb<z<xd<1: raise ValueError('Se requiere 0 < xB < zF < xD < 1; pureza absoluta requiere un tratamiento límite.')
    D=F*(z-xb)/(xd-xb); B=F-D; L0=R*D
    hf,hd,hb=h(z),h(xd),h(xb)
    QC=(R+1)*D*(H(xd)-hd)
    QR=D*hd+B*hb+QC-F*hf
    dd=hd+QC/D; db=hb-QR/B
    # Pinch de alimentación: indicador local, no garantía general de viabilidad.
    dmin=hf+(H(eq(z))-hf)*(xd-z)/(eq(z)-z)
    rpinch=(dmin-H(xd))/(H(xd)-hd)
    if R <= rpinch+1e-10:
        raise ValueError(f'Reflujo insuficiente: R debe superar {rpinch:.5f} (pinch de alimentación).')
    if QR<=0: raise ValueError('La operación requiere un rehervidor con carga positiva.')
    rows=[]; y=xd; previous_x=xd; feed=None
    for n in range(1,1001):
        x=inv(y)
        if x >= previous_x-1e-11:
            raise ValueError('Pinch o falta de avance: no se alcanza la separación con este reflujo.')
        if feed is None and x <= z+1e-12: feed=n
        section='Agotamiento' if feed is not None else 'Rectificación'
        row=dict(n=n,x=x,y=y,T=temp(x),h=h(x),H=H(y),seccion=section)
        rows.append(row)
        if x <= xb:
            fraction=(previous_x-xb)/(previous_x-x)
            count=n-1+fraction
            break
        dx,dh=(xd,dd) if feed is None else (xb,db)
        ynext=ray(x,dx,dh)
        if not x < ynext < y-1e-12:
            raise ValueError('Condición no viable: flujo negativo, pinch o composición sin avance.')
        if feed is None:
            liquid=D*(xd-ynext)/(ynext-x); vapor=liquid+D
            er=vapor*H(ynext)-liquid*h(x)-D*hd-QC
            mr=vapor*ynext-liquid*x-D*xd
        else:
            vapor=B*(x-xb)/(ynext-x); liquid=vapor+B
            er=liquid*h(x)+QR-vapor*H(ynext)-B*hb
            mr=liquid*x-vapor*ynext-B*xb
        if min(liquid,vapor)<=0: raise ValueError('Flujos internos no positivos.')
        row.update(y_siguiente=ynext,L=liquid,V=vapor,res_energia=er,res_benceno=mr)
        previous_x=x; y=ynext
    else: raise ValueError('Se superaron 1000 etapas: operación demasiado cercana a un pinch.')
    return dict(entradas=p,D=D,B=B,L0=L0,V1=(R+1)*D,hF=hf,hD=hd,hB=hb,
                QC=QC,QR=QR,deltaD=dd,deltaB=db,R_pinch=rpinch,
                etapas=rows,N_grafico=count,N_entero=len(rows),etapa_alimentacion=feed,
                res_materia=F-D-B,res_benceno=F*z-D*xd-B*xb,
                res_energia=F*hf+QR-D*hd-B*hb-QC)

if __name__=='__main__':
    import json
    print(json.dumps(solve(),indent=2,ensure_ascii=False))
