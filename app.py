import streamlit as st
import pandas as pd
from datetime import datetime

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
        font-family: monospace; border: 2px solid #000; padding: 20px; background-color: #fdfdfd; overflow-x: auto;
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
        .copyright-footer {
            position: fixed;
            bottom: 5mm;
            right: 5mm;
            font-size: 10px;
            color: #333;
            display: block !important;
        }
        .page-break { page-break-before: always !important; }
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
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
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

    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    st.header("3. Schemat jednokreskowy ideowy")
    

[Image of electrical switchboard single line diagram]

    sch = "ZASILANIE: Sieć TN-S 3x230/400V 50Hz\\n┃\\n"
    glowny = [u for u in st.session_state['szyna'] if u.charakterystyka in ["FR", "SPD"]]
    obwody = [u for u in st.session_state['szyna'] if u.charakterystyka not in ["FR", "SPD"]]
    for u in glowny:
        pref = "Q" if u.charakterystyka == "FR" else "F"
        sch += f"┣━[ {pref}: {u.charakterystyka} {u.prad} ] ——— Rozdzielacz główny\\n┃\\n"
    sch += "┣━━━━┳━━━━┳━━━━ SZYNIA L1, L2, L3\\n"
    for u in obwody:
        sym = "—[—" if u.moduly == 1 else "—[≡—"
        sch += f"┃    ┣━({u.faza})━{sym} {u.charakterystyka}{u.prad} ]——— {u.przekroj} ———> {u.opis}\\n"
    sch += "┃    ▼\\n⚡ REZERWA"
    st.markdown(f'<div class="schemat-box"><pre style="font-size:14px; line-height:1.2;">{sch}</pre></div>', unsafe_allow_html=True)

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
