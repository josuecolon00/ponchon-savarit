from modelo import X,Y,h,H

def diagram(r,full=False,limit=None,rays=True):
    p=r['entradas']; rows=r['etapas'][:limit]
    low,high=(min(r['deltaB'],-5000)-10000,max(r['deltaD'],60000)+10000) if full else (7000,55000)
    w,ht=1000,550; left,right,top,bottom=85,965,35,485
    sx=lambda x:left+x*(right-left)
    sy=lambda y:bottom-(y-low)/(high-low)*(bottom-top)
    a=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {ht}" role="img" aria-label="Diagrama entalpía composición Ponchon Savarit"><rect width="100%" height="100%" fill="white"/><defs><clipPath id="plot"><rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"/></clipPath></defs>']
    def line(x1,y1,x2,y2,color,width=1,dash='',extra=''):
        a.append(f'<line x1="{sx(x1):.3f}" y1="{sy(y1):.3f}" x2="{sx(x2):.3f}" y2="{sy(y2):.3f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" {extra}/>')
    def label(x,y,s,col='#344054',anchor='middle',size=12):
        a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{col}" font-family="Arial,sans-serif" font-size="{size}">{s}</text>')
    for i in range(11):
        x=i/10;line(x,low,x,high,'#e6eaf0');label(sx(x),bottom+23,f'{x:.1f}')
    for i in range(7):
        y=low+(high-low)*i/6;line(0,y,1,y,'#e6eaf0');label(left-10,sy(y)+4,f'{y/1000:.1f}',anchor='end')
    label(520,535,'Fracción molar de benceno · x (líquido), y (vapor)',size=14)
    a.append('<text x="20" y="290" transform="rotate(-90 20 290)" text-anchor="middle" font-family="Arial" font-size="14" fill="#344054">Entalpía · 10³ kJ/kmol</text>')
    a.append('<g clip-path="url(#plot)">')
    for x,y in zip(X,Y):line(x,h(x),y,H(y),'#d6dde7',1,'4 4')
    if rays:
        line(p['xB'],r['deltaB'],p['xD'],r['deltaD'],'#8c70bd',1.5,'7 5')
    for func,col in [(h,'#0288a6'),(H,'#dc7542')]:
        pts=' '.join(f'{sx(i/400):.2f},{sy(func(i/400)):.2f}' for i in range(401))
        a.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
    for row in rows:
        n,x,y=row['n'],row['x'],row['y'];col='#156f63' if n<r['etapa_alimentacion'] else '#3865b8'
        if n==r['etapa_alimentacion']:col='#a3458b'
        line(y,H(y),x,h(x),col,2.4)
        a.append(f'<circle cx="{sx(x):.2f}" cy="{sy(h(x)):.2f}" r="4" fill="{col}"><title>Etapa {n}: x={x:.6f}, y={y:.6f}</title></circle>')
        label(sx(x),sy(h(x))+18,str(n),col,size=11)
        if 'y_siguiente' in row:
            yn=row['y_siguiente']
            if rays:
                dx,dh=(p['xD'],r['deltaD']) if n<r['etapa_alimentacion'] else (p['xB'],r['deltaB'])
                line(dx,dh,x,h(x),col,.8,'3 5')
            line(x,h(x),yn,H(yn),col,1.5,'6 4')
    line(p['xB'],low,p['xB'],high,'#af4163',1,'3 5')
    a.append('</g>')
    points=[(p['zF'],r['hF'],'F','#a3458b'),(p['xD'],r['hD'],'D','#156f63'),(p['xB'],r['hB'],'B','#3865b8')]
    if full: points +=[(p['xD'],r['deltaD'],'ΔD','#156f63'),(p['xB'],r['deltaB'],'ΔB','#3865b8')]
    for x,y,s,c in points:
        a.append(f'<circle cx="{sx(x)}" cy="{sy(y)}" r="5" fill="{c}"/>');label(sx(x)+8,sy(y)-10,s,c,anchor='start',size=15)
    a.append('</svg>');return ''.join(a)
