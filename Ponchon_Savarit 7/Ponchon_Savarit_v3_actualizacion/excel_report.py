from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

def make_workbook(r, components=None):
    components=components or {}
    wb=Workbook()
    ws=wb.active; ws.title="Entradas"
    ws.append(["SIMULADOR PONCHON–SAVARIT | HOJA DE ENTRADAS"])
    ws.append(["Parámetro","Valor","Unidad / descripción"])
    for k,v,u in [
        ("F",r["entradas"]["F"],"kmol/h"),("zF",r["entradas"]["zF"],"fracción molar del componente más volátil"),
        ("xD",r["entradas"]["xD"],"fracción molar en destilado"),("xB",r["entradas"]["xB"],"fracción molar en fondos"),
        ("R",r["entradas"]["R"],"L0/D"),("D",r["D"],"kmol/h calculado"),("B",r["B"],"kmol/h calculado"),
        ("Etapas gráficas",r["N_grafico"],"incluye rehervidor parcial"),("Etapas enteras",r["N_entero"],"estimación"),
        ("Etapa de alimentación",r["etapa_alimentacion"],"desde arriba")]:
        ws.append([k,v,u])
    ws.append([])
    ws.append(["Componentes para comparación de volatilidad"])
    ws.append(["Componente 1",components.get("name1","Benceno")])
    ws.append(["Componente 2",components.get("name2","Tolueno")])
    ws.append(["Temperatura de comparación (°C)",components.get("T",80)])
    ws.append(["Presión de comparación (kPa)",components.get("P",101.325)])
    for k in ("A1","B1","C1","A2","B2","C2"):
        if k in components: ws.append([k,components[k]])
    bal=wb.create_sheet("Procedimiento")
    bal.append(["PROCEDIMIENTO Y BALANCES"])
    bal.append(["Paso","Ecuación / operación","Resultado","Unidad"])
    rows=[
        ("1","D = F(zF − xB)/(xD − xB)",r["D"],"kmol/h"),
        ("2","B = F − D",r["B"],"kmol/h"),
        ("3","L0 = R·D",r["L0"],"kmol/h"),
        ("4","V1 = (R + 1)·D",r["V1"],"kmol/h"),
        ("5","hF = h(zF)",r["hF"],"kJ/kmol"),
        ("6","hD = h(xD)",r["hD"],"kJ/kmol"),
        ("7","hB = h(xB)",r["hB"],"kJ/kmol"),
        ("8","QC = (R+1)D[H(xD) − hD]",r["QC"],"kJ/h"),
        ("9","QR = D·hD + B·hB + QC − F·hF",r["QR"],"kJ/h"),
        ("10","ΔD = hD + QC/D",r["deltaD"],"kJ/kmol"),
        ("11","ΔB = hB − QR/B",r["deltaB"],"kJ/kmol"),
        ("12","Residuo global de energía",r["res_energia"],"kJ/h"),
    ]
    for x in rows: bal.append(list(x))
    st=wb.create_sheet("Etapas")
    st.append(["ETAPAS DE EQUILIBRIO Y CONSTRUCCIÓN"])
    headers=["Etapa","x líquido","y vapor","T (°C)","h líquido (kJ/kmol)","H vapor (kJ/kmol)","L (kmol/h)","V (kmol/h)","Sección","Residuo energía","Residuo benceno"]
    st.append(headers)
    for a in r["etapas"]:
        st.append([a.get(k) for k in ["n","x","y","T","h","H","L","V","seccion","res_energia","res_benceno"]])
    vol=wb.create_sheet("Volatilidad")
    vol.append(["COMPARACIÓN DE VOLATILIDAD RELATIVA"])
    vol.append(["La volatilidad relativa ideal se estima como α12 = Psat,1 / Psat,2 usando Antoine."])
    vol.append(["Componente 1",components.get("name1","Benceno")])
    vol.append(["Componente 2",components.get("name2","Tolueno")])
    vol.append(["T (°C)",components.get("T",80)])
    vol.append(["P (kPa)",components.get("P",101.325)])
    if all(k in components for k in ("A1","B1","C1","A2","B2","C2")):
        T=float(components.get("T",80))
        p1=10**(float(components["A1"])-float(components["B1"])/(T+float(components["C1"])))
        p2=10**(float(components["A2"])-float(components["B2"])/(T+float(components["C2"])))
        vol.append(["Psat 1 (mmHg)",p1]); vol.append(["Psat 2 (mmHg)",p2]); vol.append(["α12",p1/p2])
        vol.append(["Más volátil",components.get("name1") if p1>p2 else components.get("name2") if p2>p1 else "Similar"])
    else:
        vol.append(["Resultado","Introduce constantes Antoine A, B, C para ambos componentes en la app."])
    for sh in wb.worksheets:
        sh.freeze_panes="A3"; sh.sheet_view.showGridLines=False
        sh.column_dimensions["A"].width=30
        for col in range(2,sh.max_column+1): sh.column_dimensions[get_column_letter(col)].width=25
        for cell in sh[1]:
            cell.font=Font(bold=True,color="FFFFFF",size=14); cell.fill=PatternFill("solid",fgColor="123A3C")
        for cell in sh[2]:
            cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="14756A")
        for row in sh.iter_rows(min_row=3):
            for c in row:
                c.alignment=Alignment(vertical="center")
                if c.column==2 and isinstance(c.value,(int,float)): c.number_format="0.000000"
    out=BytesIO(); wb.save(out); return out.getvalue()
