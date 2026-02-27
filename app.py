import streamlit as st
import pandas as pd
from datetime import datetime
import base64

st.set_page_config(page_title="Projektant Rozdzielnicy - Marcin Szymański", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

st.markdown("""
    <style>
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; }
    .szyna-din {
        display: flex; flex-direction: row; background-color: #b0b0b0;
        padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777;
        gap: 4px; margin-bottom: 15px; overflow-x: auto;
    }
    .header-box {
        border: 3px solid #1f1f1f;
        padding: 0;
        margin-bottom: 25px;
        background-color: #ffffff;
    }
    .header-top {
        background-color: #1f1f1f;
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .schemat-box {
        font-family: 'Courier New', Courier, monospace;
        border: 2px solid #000;
        padding: 20px;
        background-color: #ffffff !important;
        color: #000 !important;
        white-space: pre !important;
        display: block !important;
        line-height: 1.2 !important;
        margin-top: 20px;
    }
    @media print {
        section[data-testid="stSidebar"], .stButton, header, footer, [data-testid="stDecoration"], .no-print {
            display: none !important;
        }
        .main .block-container { padding-top: 5mm !important; }
        .obudowa { background-color: white !important; border: 2px solid black !important; }
        .szyna-din { background-color: #f9f9f9 !important; border: 1px solid #000 !important; page-break-inside: avoid; }
        .header-box { border: 2px solid black !important; }
        .header-top { background-color: #f2f2f2 !important; color: black !important; border-bottom: 2px solid black; }
        
        .print-page-break {
            page-break-before: always !important;
            display: block !important;
        }
        
        .copyright-footer {
            position: fixed;
            bottom: 5mm;
            right: 5mm;
            font-size: 10px;
            color: #333;
            display: block !important;
        }
    }
    .copyright-screen {
        text-align: right; font-size: 12px; color: #888; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

DB_APARATY = {
    "Zabezpieczenia Nadprądowe (MCB)": [
        {"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "13", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32", "40"], "m": 3},
    ],
    "Różnicowoprądowe (RCD)": [
        {"n": "Różnicówka 2P 30mA", "c": "Typ A", "p": ["25", "40"], "m": 2},
        {"n": "Różnicówka 4P 30mA", "c": "Typ A", "p": ["25", "40", "63"], "m": 4},
    ],
    "Pozostałe": [
        {"n": "Rozłącznik Główny 3P", "c": "FR", "p": ["63", "100"], "m": 3},
        {"n": "Ochronnik T1+T2", "c": "SPD", "p": ["B+C"], "m": 4},
        {"n": "Lampka Kontrolna", "c": "L-3", "p": ["230V"], "m": 1},
    ]
}

def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 40: return "6.0 mm²"
        else: return "10.0 mm²+"
    except: return "wg dok."

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)
        try: self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except: self.val_a = 0.0

st.sidebar.title("🛠️ Kreator Projektu")
prod_name = st.sidebar.selectbox("Producent osprzętu:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]
st.sidebar.divider()
st.sidebar.subheader("📝 Dane Inwestycji")
klient = st.sidebar.text_input("Inwestor / Klient:", "Jan Kowalski")
miejsce = st.sidebar.text_input("Miejsce montażu:", "Dom Jednorodzinny - Rozdzielnica R1")
st.sidebar.divider()
wsp_j = st.sidebar.slider("Współczynnik jednoczesności:", 0.1, 1.0, 0.6)
limit_a = st.sidebar.number_input("Limit przedlicznikowy [A]:", value=25)
st.sidebar.divider()
kat = st.sidebar.selectbox("Kategoria:", list(DB_APARATY.keys()))
ap_typ = st.sidebar.selectbox("Urządzenie:", DB_APARATY[kat], format_func=lambda x: f"{x['n']} ({x['c']})")
ap_prad = st.sidebar.selectbox("Prąd znamionowy:", ap_typ['p'])
f_auto = "L123" if ap_typ['m'] >= 3 else st.sidebar.selectbox("Faza:", ["L1", "L2", "L3"], index=st.session_state['next_faza_idx'])
etyk = st.sidebar.text_input("Przeznaczenie obwodu:", "Gniazda Kuchnia")

if st.sidebar.button("Dodaj do szafy ➡️", use_container_width=True):
    st.session_state['szyna'].append(Urzadzenie(ap_typ['n'], ap_typ['c'], ap_prad, ap_typ['m'], f_auto, etyk))
    if ap_typ['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

if st.sidebar.button("Resetuj projekt 🗑️"):
    st.session_state['szyna'] = []; st.session_state['next_faza_idx'] = 0; st.rerun()

st.markdown(f"""
    <div class="header-box">
        <div class="header-top">Dokumentacja Techniczna Rozdzielnicy</div>
    </div>
""", unsafe_allow_html=True)

obc = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    if u.charakterystyka not in ["FR", "SPD"]:
        if u.faza == "L123":
            for f in ["L1", "L2", "L3"]: obc[f] += u.val_a * wsp_j
        else: obc[u.faza] += u.val_a * wsp_j

cols = st.columns(3)
for i, f in enumerate(["L1", "L2", "L3"]):
    p_proc = min(obc[f] / limit_a, 1.1)
    with cols[i]:
        st.metric(f"Faza {f}", f"{obc[f]:.1f} A")
        b_c = "green" if p_proc < 0.8 else "orange" if p_proc < 1.0 else "red"
        st.markdown(f'<div class="no-print" style="background:#eee;height:8px;width:100%;border-radius:4px;"><div style="background:{b_c};height:8px;width:{p_proc*100}%;border-radius:4px;"></div></div>', unsafe_allow_html=True)

rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"**SZYNIA DIN NR {r_i+1}**")
        html_szyny = '<div class="szyna-din">'
        for u in rzad:
            f_c = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza)
            html_szyny += f"""
            <div style="width:{u.moduly*45}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; min-height:270px; display:flex; flex-direction:column; border-top:8px solid {brand_color};">
                <div style="font-size:9px; font-weight:bold; color:{f_c}; padding:3px;">{u.faza}</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:19px; font-weight:900; color:#d35400;">{u.charakterystyka}{u.prad}</div>
                    <div style="font-size:9px; color:#555;">{u.przekroj}</div>
                </div>
                <div style="border-top:1px solid #ddd; padding:4px; height:50px; font-size:9px; font-weight:bold; display:flex; align-items:center; justify-content:center; background:#f9f9f9;">{u.opis}</div>
                <div style="background:#1a252f; color:#f1c40f; font-size:8px; padding:3px;">{u.moduly}M</div>
            </div>"""
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['szyna']:
    st.markdown('<div class="print-page-break"></div>', unsafe_allow_html=True)
    st.header("1. Specyfikacja techniczna obwodów")
    df = pd.DataFrame([{
        "Nr": i+1, "Aparat": f"{u.charakterystyka}{u.prad}", "Faza": u.faza,
        "Przewód": u.przekroj, "Opis": u.opis
    } for i, u in enumerate(st.session_state['szyna'])])
    st.table(df)

    st.header("2. Zbiorcze zestawienie materiałów")
    zestawienie = [f"{u.nazwa} {u.charakterystyka}{u.prad} ({prod_name})" for u in st.session_state['szyna']]
    df_bom = pd.Series(zestawienie).value_counts().reset_index()
    df_bom.columns = ['Element instalacji', 'Ilość [szt]']
    st.table(df_bom)

    st.markdown('<div class="print-page-break"></div>', unsafe_allow_html=True)
    st.header("3. Schemat jednokreskowy ideowy")
    
    sch_lines = ["ZASILANIE: Sieć TN-S 3x230/400V 50Hz", "┃"]
    glowny = [u for u in st.session_state['szyna'] if u.charakterystyka in ["FR", "SPD"]]
    obwody = [u for u in st.session_state['szyna'] if u.charakterystyka not in ["FR", "SPD"]]
    
    for u in glowny:
        pref = "Q" if u.charakterystyka == "FR" else "F"
        sch_lines.append(f"┣━[ {pref}: {u.charakterystyka} {u.prad} ] ——— Rozdzielacz główny")
        sch_lines.append("┃")
    
    sch_lines.append("┣━━━━┳━━━━┳━━━━ SZYNIA L1, L2, L3")
    for u in obwody:
        sym = "—[—" if u.moduly == 1 else "—[≡—"
        sch_lines.append(f"┃    ┣━({u.faza})━{sym} {u.charakterystyka}{u.prad} ]——— {u.przekroj} ———> {u.opis}")
    sch_lines.append("┃    ▼")
    sch_lines.append("⚡ REZERWA")
    
    sch_final = "\n".join(sch_lines)
    st.markdown(f'<div class="schemat-box">{sch_final}</div>', unsafe_allow_html=True)

    st.sidebar.divider()
    if st.sidebar.button("🖨️ DRUKUJ CAŁOŚĆ", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="copyright-screen no-print">
            © {datetime.now().year} Opracowanie: <b>Marcin Szymański</b> | Wszystkie prawa zastrzeżone
        </div>
        <div class="copyright-footer" style="display:none;">
            Projekt: Marcin Szymański | Data: {datetime.now().strftime('%d.%m.%Y')}
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Dodaj urządzenia, aby wygenerować pełną dokumentację.")

if st.session_state['szyna']:
    st.sidebar.divider()
    
    html_szyny_print = "<h2>1. Widok rozmieszczenia aparatów</h2>\n"
    for r_i, rzad in enumerate(rzedy):
        if rzad:
            html_szyny_print += f'<div style="font-weight:bold; margin-bottom: 5px; font-family: sans-serif;">SZYNA DIN NR {r_i+1}</div>'
            html_szyny_print += '<div style="display: flex; flex-direction: row; background-color: #d0d0d0; padding: 15px 5px; border-top: 6px solid #777; border-bottom: 6px solid #777; gap: 4px; margin-bottom: 25px; page-break-inside: avoid; font-family: sans-serif;">'
            for u in rzad:
                f_c = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza)
                html_szyny_print += f"""
                <div style="width:{u.moduly*38}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; min-height:180px; display:flex; flex-direction:column; border-top:6px solid {brand_color}; box-sizing: border-box;">
                    <div style="font-size:9px; font-weight:bold; color:{f_c}; padding:3px;">{u.faza}</div>
                    <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:16px; font-weight:900; color:#d35400; line-height:1;">{u.charakterystyka}{u.prad}</div>
                        <div style="font-size:9px; color:#555; margin-top:2px;">{u.przekroj}</div>
                    </div>
                    <div style="border-top:1px solid #ddd; padding:2px; height:40px; font-size:8px; font-weight:bold; display:flex; align-items:center; justify-content:center; background:#f9f9f9; overflow:hidden;">{u.opis}</div>
                    <div style="background:#1a252f; color:#f1c40f; font-size:8px; padding:3px;">{u.moduly}M</div>
                </div>"""
            html_szyny_print += '</div>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Dokumentacja - {klient}</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; color: #000; background: #fff; }}
            h1, h2 {{ text-align: center; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; font-size: 14px; }}
            .page-break {{ page-break-before: always; }}
            .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; font-weight: bold; font-size: 20px; }}
            @media print {{
                @page {{ size: A4 portrait; margin: 10mm; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            DOKUMENTACJA TECHNICZNA ROZDZIELNICY<br>
            <span style="font-size:14px; font-weight:normal;">Inwestor: {klient} | Lokalizacja: {miejsce} | Data: {datetime.now().strftime('%d.%m.%Y')}</span>
        </div>
        
        {html_szyny_print}
        
        <div class="page-break"></div>
        
        <h2>2. Specyfikacja techniczna obwodów</h2>
        <table>
            <tr><th>Nr</th><th>Aparat</th><th>Faza</th><th>Przewód</th><th>Opis</th></tr>
    """
    
    for i, u in enumerate(st.session_state['szyna']):
        html_content += f"<tr><td>{i+1}</td><td>{u.charakterystyka}{u.prad}</td><td>{u.faza}</td><td>{u.przekroj}</td><td>{u.opis}</td></tr>"
        
    html_content += """
        </table>
        
        <div class="page-break"></div>
        
        <h2>3. Schemat jednokreskowy ideowy</h2>
    """
    
    glowny = [u for u in st.session_state['szyna'] if u.charakterystyka in ["FR", "SPD"]]
    obwody = [u for u in st.session_state['szyna'] if u.charakterystyka not in ["FR", "SPD"]]
    
    svg_height = 160 + len(obwody) * 60
    
    svg = f'<div style="text-align: left; margin-top: 20px; border: 1px solid #000; padding: 20px; background-color: #fdfdfd;">'
    svg += f'<svg width="100%" height="{svg_height}" xmlns="http://www.w3.org/2000/svg" style="font-family: sans-serif;">'
    
    svg += '<line x1="80" y1="20" x2="80" y2="80" stroke="#000" stroke-width="3"/>'
    svg += '<text x="100" y="45" font-size="14" font-weight="bold">ZASILANIE: Sieć TN-S 3x230/400V 50Hz</text>'
    
    glowny_txt = " + ".join([f"{u.charakterystyka}{u.prad}" for u in glowny])
    if not glowny_txt: glowny_txt = "Rozłącznik Główny"
    svg += '<rect x="60" y="80" width="40" height="40" fill="#fff" stroke="#000" stroke-width="2"/>'
    svg += f'<text x="110" y="105" font-size="14" font-weight="bold">{glowny_txt}</text>'
    
    svg += f'<line x1="80" y1="120" x2="80" y2="{svg_height-20}" stroke="#000" stroke-width="3"/>'
    
    y = 160
    for u in obwody:
        svg += f'<circle cx="80" cy="{y}" r="4" fill="#000"/>'
        svg += f'<line x1="80" y1="{y}" x2="130" y2="{y}" stroke="#000" stroke-width="2"/>'
        svg += f'<rect x="130" y="{y-15}" width="60" height="30" fill="#fff" stroke="#000" stroke-width="2"/>'
        svg += f'<text x="160" y="{y+4}" font-size="12" font-weight="bold" text-anchor="middle">{u.charakterystyka}{u.prad}</text>'
        svg += f'<line x1="190" y1="{y}" x2="280" y2="{y}" stroke="#000" stroke-width="1.5" stroke-dasharray="4"/>'
        svg += f'<text x="290" y="{y-4}" font-size="13" font-weight="bold">{u.opis}</text>'
        svg += f'<text x="290" y="{y+12}" font-size="11" fill="#555">Faza: {u.faza} | Przewód: {u.przekroj}</text>'
        y += 60
        
    svg += '</svg></div>'
    html_content += svg
    
    html_content += f"""
        <div style="text-align: right; font-size: 10px; margin-top: 30px;">
            © {datetime.now().year} Opracowanie: Marcin Szymański | Wszystkie prawa zastrzeżone
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="Dokumentacja_{klient.replace(" ", "_")}.html" style="display: block; text-align: center; padding: 10px; background-color: #005EB8; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-bottom: 20px;">📥 POBIERZ PLIK DO DRUKU</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)
