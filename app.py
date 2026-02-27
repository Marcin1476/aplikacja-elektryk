import streamlit as st
import pandas as pd

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Dokumentacja Rozdzielnicy v3.7", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'nazwy_rzedow' not in st.session_state:
    st.session_state['nazwy_rzedow'] = {}

# --- 2. PARAMETRY ---
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- 3. CSS DLA WYDRUKU (KLUCZOWY ELEMENT) ---
st.markdown("""
    <style>
    /* STYLE DLA EKRANU */
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-din { 
        display: flex; flex-direction: row; background-color: #b0b0b0; 
        padding: 35px 5px; border-top: 15px solid #777; border-bottom: 15px solid #777; 
        gap: 4px; margin-bottom: 30px; 
    }
    
    /* STYLE DLA DRUKARKI (Ctrl+P) */
    @media print {
        /* Ukrywamy sidebar, przyciski, stopki i dekoracje Streamlit */
        section[data-testid="stSidebar"], 
        .stButton, 
        header, 
        footer, 
        .no-print,
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        /* Resetujemy marginesy i tła */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        body, .main {
            background-color: white !important;
            color: black !important;
        }
        
        .obudowa {
            background-color: white !important;
            border: 2px solid black !important;
            padding: 10px !important;
            box-shadow: none !important;
        }
        
        .szyna-din {
            background-color: #f9f9f9 !important;
            border: 1px solid #000 !important;
            padding: 20px 0 !important;
            page-break-inside: avoid;
        }
        
        .aparat {
            border: 1px solid black !important;
            box-shadow: none !important;
            background: white !important;
            print-color-adjust: exact;
        }
        
        h1, h2, h3 {
            color: black !important;
            margin-top: 10px !important;
        }

        /* Wymuszamy, aby tabele nie dzieliły się w połowie wiersza */
        table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. KLASA I FUNKCJE ---
def wylicz_przekroj(prad):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        else: return "4.0 mm²+"
    except: return "-"

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)

# --- 5. PANEL BOCZNY (Widoczny tylko na ekranie) ---
st.sidebar.title("🛠️ Panel Inżynierski")
prod = st.sidebar.selectbox("Marka:", list(PRODUCENCI.keys()))
b_color = PRODUCENCI[prod]

# Prosta biblioteka do testów
ap_typ = st.sidebar.selectbox("Aparat:", ["Wyłącznik B16", "Wyłącznik B10", "RCD 4P 40A", "SPD T1+T2"])
etyk = st.sidebar.text_input("Opis obwodu:", "Gniazda")

if st.sidebar.button("Dodaj do projektu"):
    # Logika uproszczona dla demonstracji wydruku
    m = 4 if "SPD" in ap_typ or "RCD" in ap_typ else 1
    char = "B" if "B" in ap_typ else "SPD"
    prad = "16" if "16" in ap_typ else "10" if "10" in ap_typ else "40"
    st.session_state['szyna'].append(Urzadzenie(ap_typ, char, prad, m, "L1", etyk))
    st.rerun()

if st.sidebar.button("Wyczyść projekt"):
    st.session_state['szyna'] = []; st.rerun()

# --- 6. GENEROWANIE DOKUMENTACJI (Widok główny) ---
st.title("PROJEKT TECHNICZNY ROZDZIELNICY")
st.caption("Dokument wygenerowany automatycznie. Zawiera schemat montażowy, specyfikację i listę materiałową.")

# Wizualizacja rzędów
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
            html += f"""
            <div class="aparat" style="width:{u.moduly*48}px; border-top: 10px solid {b_color}; border: 1px solid #000; background: #fff; flex-shrink:0; text-align:center; min-height:280px; display:flex; flex-direction:column;">
                <div style="font-size:10px; font-weight:bold; padding:5px; border-bottom:1px solid #eee;">{u.faza}</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:24px; font-weight:900;">{u.charakterystyka}{u.prad}</div>
                    <div style="font-size:9px;">{u.przekroj}</div>
                </div>
                <div style="font-size:10px; padding:5px; background:#f9f9f9; min-height:60px; font-weight:bold;">{u.opis}</div>
                <div style="font-size:9px; padding:3px; background:#ddd;">{u.moduly} MOD</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sekcje tekstowe
st.header("1. Specyfikacja techniczna obwodów")
if st.session_state['szyna']:
    df_tech = pd.DataFrame([{
        "Poz.": i+1, "Aparat": f"{u.charakterystyka}{u.prad}", 
        "Opis obwodu": u.opis, "Przewód Cu": u.przekroj, "Faza": u.faza
    } for i, u in enumerate(st.session_state['szyna'])])
    st.table(df_tech)

st.header("2. Zbiorcze zestawienie materiałowe")
if st.session_state['szyna']:
    bom = pd.Series([f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]).value_counts().reset_index()
    bom.columns = ['Nazwa elementu', 'Ilość [szt.]']
    st.table(bom)
