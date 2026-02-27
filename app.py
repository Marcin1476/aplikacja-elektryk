import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy v3.8", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

# --- 2. STYLE CSS (OPTYMALIZACJA POD A4 I WYDRUK) ---
st.markdown("""
    <style>
    /* STYLE EKRANOWE */
    .obudowa { background-color: #333; padding: 20px; border-radius: 12px; }
    .szyna-din {
        display: flex; flex-direction: row; background-color: #b0b0b0;
        padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777;
        gap: 4px; margin-bottom: 15px; overflow-x: auto;
    }
    
    /* STYLE DRUKU */
    @media print {
        section[data-testid="stSidebar"], .stButton, header, footer, [data-testid="stDecoration"] {
            display: none !important;
        }
        .main .block-container {
            padding: 10mm !important;
            margin: 0 !important;
        }
        .print-header {
            font-size: 22px !important; /* Zmniejszona czcionka nagłówka */
            text-align: center;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .copyright-footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: right;
            font-size: 10px;
            color: #555;
            border-top: 1px solid #ccc;
            padding-top: 5px;
        }
        .obudowa { background-color: white !important; border: 1px solid #000 !important; }
        .szyna-din { background-color: #f0f0f0 !important; border: 1px solid #000 !important; page-break-inside: avoid; }
        .aparat { border: 1px solid black !important; print-color-adjust: exact; }
    }
    
    .copyright-screen {
        text-align: right;
        font-size: 12px;
        color: #888;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PARAMETRY I LOGIKA ---
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        else: return "6.0 mm²+"
    except: return "wg dok."

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)
        try: self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except: self.val_a = 0.0

# --- 4. SIDEBAR ---
st.sidebar.title("🛠️ Kreator Projektu")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

# Biblioteka (uproszczona dla stabilności fundamentu)
BIBL = [
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1},
    {"n": "Różnicówka 4P", "c": "Typ A", "p": "40", "m": 4},
    {"n": "Ochronnik T1+T2", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Rozłącznik 3P", "c": "FR", "p": "100", "m": 3}
]

idx = st.sidebar.selectbox("Aparat:", range(len(BIBL)), format_func=lambda x: f"{BIBL[x]['n']} {BIBL[x]['c']}{BIBL[x]['p']}")
etyk = st.sidebar.text_input("Opis obwodu:", "Gniazda")

if st.sidebar.button("Dodaj ➡️", use_container_width=True):
    b = BIBL[idx]
    f = "L123" if b['m'] >= 3 else ["L1", "L2", "L3"][st.session_state['next_faza_idx']]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], f, etyk))
    if b['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Resetuj projekt 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- 5. WIDOK GŁÓWNY (DOKUMENTACJA) ---
st.markdown('<div class="print-header">Dokumentacja Techniczna Rozdzielnicy</div>', unsafe_allow_html=True)
st.write(f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Podział na rzędy
rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly



st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"**SZYNIA DIN NR {r_i+1}**")
        html = '<div class="szyna-din">'
        for u in rzad:
            f_c = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza)
            html += f"""
            <div style="width:{u.moduly*45}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; min-height:260px; display:flex; flex-direction:column; border-top:8px solid {brand_color};">
                <div style="font-size:9px; font-weight:bold; color:{f_c};">{u.faza}</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:18px; font-weight:900;">{u.charakterystyka}{u.prad}</div>
                    <div style="font-size:8px;">{u.przekroj}</div>
                </div>
                <div style="border-top:1px solid #ddd; padding:3px; height:50px; font-size:9px; font-weight:bold; display:flex; align-items:center; justify-content:center; background:#f9f9f9;">{u.opis}</div>
                <div style="font-size:8px; padding:2px; background:#eee;">{u.moduly}M</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Tabele
if st.session_state['szyna']:
    st.subheader("1. Specyfikacja techniczna")
    df = pd.DataFrame([{"Nr": i+1, "Aparat": f"{u.charakterystyka}{u.prad}", "Faza": u.faza, "Przewód": u.przekroj, "Opis": u.opis} for i, u in enumerate(st.session_state['szyna'])])
    st.table(df)

    st.subheader("2. Zestawienie materiałowe")
    bom = pd.Series([f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]).value_counts().reset_index()
    bom.columns = ['Element', 'Sztuk']
    st.table(bom)

# --- STOPKA AUTORSKA ---
footer_html = f"""
    <div class="copyright-screen no-print">© {datetime.now().year} Marcin Szymański. Wszystkie prawa zastrzeżone.</div>
    <div class="copyright-footer">Projekt i opracowanie: Marcin Szymański</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
