import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURACJA FUNDAMENTALNA ---
st.set_page_config(page_title="Projektant Rozdzielnicy - Marcin Szymański", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

# --- 2. STYLE CSS (OPTYMALIZACJA WYDRUKU WIELOSTRONICOWEGO) ---
st.markdown("""
    <style>
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; }
    .szyna-din { 
        display: flex; flex-direction: row; background-color: #b0b0b0; 
        padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777; 
        gap: 4px; margin-bottom: 15px; overflow-x: auto; 
    }
    .header-box { border: 3px solid #1f1f1f; padding: 0; margin-bottom: 25px; background-color: #ffffff; }
    .header-top { background-color: #1f1f1f; color: white; text-align: center; padding: 15px; font-size: 24px; font-weight: bold; text-transform: uppercase; }
    .schemat-box { font-family: 'Courier New', Courier, monospace; border: 2px solid #000; padding: 20px; background-color: #ffffff; white-space: pre; line-height: 1.2; }

    @media print {
        /* Resetowanie blokad Streamlit */
        .stApp { display: block !important; }
        .main .block-container { max-width: 100% !important; padding: 10mm !important; margin: 0 !important; }
        section[data-testid="stSidebar"], .stButton, header, footer, [data-testid="stDecoration"], .no-print { display: none !important; }
        
        /* Wymuszenie podziału stron przed sekcjami */
        .print-break { 
            display: block !important; 
            page-break-before: always !important; 
            break-before: page !important; 
            height: 0px;
        }
        
        .obudowa { background-color: white !important; border: 2px solid black !important; }
        .szyna-din { background-color: #f9f9f9 !important; border: 1px solid #000 !important; page-break-inside: avoid; display: flex !important; }
        .header-box { border: 2px solid black !important; }
        .header-top { background-color: #f2f2f2 !important; color: black !important; border-bottom: 2px solid black; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PARAMETRY ---
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 40: return "6.0 mm²"
        else: return "10.0 mm²"
    except: return "2.5 mm²"

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)
        try: self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except: self.val_a = 0.0

# --- 4. SIDEBAR ---
st.sidebar.title("Kreator Projektu")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]
klient = st.sidebar.text_input("Inwestor:", "Jan Kowalski")
miejsce = st.sidebar.text_input("Lokalizacja:", "Rozdzielnica R1")

if st.sidebar.button("DODAJ APARAT PRZYKŁADOWY (B16)"):
    st.session_state['szyna'].append(Urzadzenie("Wyłącznik", "B", "16", 1, ["L1", "L2", "L3"][st.session_state['next_faza_idx']], "Gniazda"))
    st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("WYCZYŚĆ WSZYSTKO"):
    st.session_state['szyna'] = []; st.rerun()

# --- 5. NAGŁÓWEK ---
st.markdown(f'<div class="header-box"><div class="header-top">Dokumentacja Techniczna Rozdzielnicy</div></div>', unsafe_allow_html=True)

# --- 6. WIZUALIZACJA ---
st.subheader("1. Widok montażowy")
rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"SZYNIA DIN {r_i+1}")
        html = '<div class="szyna-din">'
        for u in rzad:
            html += f'<div style="width:{u.moduly*45}px; border:1px solid #000; background:#fff; text-align:center; min-height:200px; border-top:8px solid {brand_color};">' \
                    f'<div style="font-size:10px;">{u.faza}</div>' \
                    f'<div style="font-size:18px; font-weight:bold;">{u.charakterystyka}{u.prad}</div>' \
                    f'<div style="font-size:9px;">{u.opis}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['szyna']:
    # --- 7. SPECYFIKACJA (STRONA 2) ---
    st.markdown('<div class="print-break"></div>', unsafe_allow_html=True)
    st.subheader("2. Specyfikacja techniczna")
    df = pd.DataFrame([{"Aparat": f"{u.charakterystyka}{u.prad}", "Faza": u.faza, "Przewód": u.przekroj, "Opis": u.opis} for u in st.session_state['szyna']])
    st.table(df)

    # --- 8. SCHEMAT (STRONA 3) ---
    st.markdown('<div class="print-break"></div>', unsafe_allow_html=True)
    st.subheader("3. Schemat jednokreskowy")
    sch = "ZASILANIE: Sieć TN-S 3x230/400V 50Hz\n┃\n"
    for u in st.session_state['szyna']:
        sch += f"┣━({u.faza})━[ {u.charakterystyka}{u.prad} ]─── {u.przekroj} ───> {u.opis}\n"
    st.markdown(f'<div class="schemat-box">{sch}</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; font-size:10px; margin-top:50px;">© {datetime.now().year} Marcin Szymański</div>', unsafe_allow_html=True)
