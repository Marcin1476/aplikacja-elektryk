import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURACJA FUNDAMENTALNA ---
st.set_page_config(page_title="Projektant Rozdzielnicy v4.0 - Marcin Szymański", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

# --- 2. STYLE CSS (OPTYMALIZACJA POD DRUK ZBIORCZY A4) ---
st.markdown("""
    <style>
    /* Widok ekranowy */
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; }
    .szyna-din { display: flex; flex-direction: row; background-color: #b0b0b0; padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777; gap: 4px; margin-bottom: 15px; }
    .schemat-box { font-family: 'Courier New', monospace; border: 1px solid #333; padding: 20px; background: #fdfdfd; line-height: 1.2; overflow-x: auto; }

    /* STYLE WYDRUKU */
    @media print {
        section[data-testid="stSidebar"], .stButton, header, footer, [data-testid="stDecoration"], .no-print {
            display: none !important;
        }
        .main .block-container { padding: 10mm !important; }
        .obudowa { background-color: white !important; border: 1px solid black !important; }
        .szyna-din { background-color: #f9f9f9 !important; border: 1px solid #000 !important; page-break-inside: avoid; }
        .schemat-box { border: 2px solid black !important; page-break-before: always; }
        .page-break { page-break-before: always; }
        table { width: 100% !important; page-break-inside: auto; }
        tr { page-break-inside: avoid; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA TECHNICZNA ---
def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        else: return "4.0 mm²"
    except: return "2.5 mm²"

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)

# --- 4. PANEL STEROWANIA (SIDEBAR) ---
st.sidebar.title("🛠️ Projektant v4.0")
klient = st.sidebar.text_input("Inwestor:", "Jan Kowalski")
miejsce = st.sidebar.text_input("Lokalizacja:", "Rozdzielnica Główna R1")
st.sidebar.divider()

BIBL = [
    {"n": "Rozłącznik", "c": "FR", "p": "100", "m": 3},
    {"n": "Ochronnik", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Różnicówka 4P", "c": "RCD", "p": "40", "m": 4},
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1}
]
sel = st.sidebar.selectbox("Wybierz aparat:", range(len(BIBL)), format_func=lambda x: f"{BIBL[x]['n']} {BIBL[x]['c']}")
etyk = st.sidebar.text_input("Opis obwodu:", "Gniazda Salon")

if st.sidebar.button("DODAJ APARAT ➡️", use_container_width=True):
    b = BIBL[sel]
    f = "L123" if b['m'] >= 3 else ["L1", "L2", "L3"][st.session_state['next_faza_idx']]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], f, etyk))
    if b['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("WYCZYŚĆ WSZYSTKO 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- 5. NAGŁÓWEK DOKUMENTACJI ---
st.markdown(f"""
    <div style="border: 2px solid black; padding: 15px; margin-bottom: 20px; background: #f9f9f9;">
        <h2 style="text-align: center; margin: 0; text-transform: uppercase;">Dokumentacja Techniczna Rozdzielnicy</h2>
        <hr style="border: 1px solid black;">
        <table style="width: 100%; border: none;">
            <tr><td><b>Inwestor:</b> {klient}</td><td style="text-align: right;"><b>Data:</b> {datetime.now().strftime('%d.%m.%Y')}</td></tr>
            <tr><td><b>Lokalizacja:</b> {miejsce}</td><td style="text-align: right;"><b>Projektant:</b> Marcin Szymański</td></tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# --- 6. SEKCJE (WIZUALIZACJA) ---
st.subheader("1. Widok montażowy (Rozmieszczenie aparatów)")
rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > 18: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"**SZYNIA NR {r_i+1}**")
        html = '<div class="szyna-din">'
        for u in rzad:
            html += f'<div style="width:{u.moduly*48}px; border:1px solid #000; background:#fff; text-align:center; min-height:220px; display:flex; flex-direction:column; border-top:8px solid #222;">' \
                    f'<div style="font-size:10px; font-weight:bold; border-bottom:1px solid #eee;">{u.faza}</div>' \
                    f'<div style="flex-grow:1; display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:900;">{u.charakterystyka}{u.prad}</div>' \
                    f'<div style="font-size:9px; padding:3px; background:#f9f9f9; min-height:40px;">{u.opis}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. GENERATOR SCHEMATU JEDNOKRESKOWEGO ---
st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
st.subheader("2. Schemat jednokreskowy ideowy")

if st.session_state['szyna']:
    sch = "ZASILANIE: Sieć TN-S 3x230/400V 50Hz\n"
    sch += "┃\n"
    fr = next((u for u in st.session_state['szyna'] if u.charakterystyka == "FR"), None)
    spd = next((u for u in st.session_state['szyna'] if u.charakterystyka == "SPD"), None)
    
    if fr: sch += f"┣━[ Q1: {fr.charakterystyka} {fr.prad}A ] Rozłącznik Główny\n┃\n"
    if spd: sch += f"┣━[ F1: {spd.charakterystyka} ] Ogranicznik Przepięć\n┃\n"
    
    sch += "┣━━━━┳━━━━┳━━━━ SZYNIA L1, L2, L3\n"
    for u in st.session_state['szyna']:
        if u.charakterystyka not in ["FR", "SPD"]:
            sch += f"┃    ┣━({u.faza})━[ {u.charakterystyka}{u.prad} ]─── {u.przekroj} ───> {u.opis}\n"
    
    st.markdown(f'<div class="schemat-box"><pre style="font-size:14px;">{sch}</pre></div>', unsafe_allow_html=True)

# --- 8. SPECYFIKACJA I MATERIAŁY ---
st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.subheader("3. Specyfikacja obwodów")
    if st.session_state['szyna']:
        df = pd.DataFrame([{"Faza": u.faza, "Zabezp.": f"{u.charakterystyka}{u.prad}", "Przewód": u.przekroj, "Opis": u.opis} for u in st.session_state['szyna']])
        st.table(df)

with c2:
    st.subheader("4. Zestawienie materiałowe")
    if st.session_state['szyna']:
        mat = pd.Series([f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]).value_counts().reset_index()
        mat.columns = ["Element", "Ilość"]
        st.table(mat)

# --- STOPKA AUTORSKA ---
st.markdown(f'<div style="text-align:right; font-size:12px; margin-top:50px; border-top: 1px solid #ccc; padding-top: 5px;">© {datetime.now().year} Marcin Szymański | Dokument wygenerowany systemowo</div>', unsafe_allow_html=True)
