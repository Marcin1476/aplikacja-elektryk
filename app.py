import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy - Automat Fazowy", layout="wide")

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0  # 0:L1, 1:L2, 2:L3

FAZY_LISTA = ["L1", "L2", "L3"]

# --- PARAMETRY ---
RZAD_MAX_MOD = 12 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

def dobierz_przewod(prad_str):
    try:
        p = int(''.join(filter(str.isdigit, prad_str)))
        if p <= 13: return "1.5 mm²"
        elif p <= 19: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 35: return "6.0 mm²"
        else: return "10.0 mm²+"
    except: return "wg projektu"

# --- CSS ---
st.markdown("""
    <style>
    .obudowa { background-color: #3d3d3d; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 40px 15px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 20px solid #777; border-bottom: 20px solid #777;
        min-height: 400px; gap: 8px; margin-bottom: 30px;
    }
    .aparat {
        border: 2px solid #111; border-radius: 4px; text-align: center;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.5); display: flex;
        flex-direction: column; min-height: 360px; flex-shrink: 0; background-color: white;
    }
    .aparat-brand { font-size: 10px; font-weight: bold; color: #fff; padding: 3px 0; text-transform: uppercase; }
    .amp-text { font-size: 30px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    .aparat-label { border: 1px solid #ccc; background: #fdfdfd; font-size: 11px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 8px; padding: 4px; font-weight: bold; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 10px 2px; margin-top: auto; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis
        self.przewod = dobierz_przewod(prad)

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    {"n": "Rozłącznik Główny 3P", "c": "FR", "p": "100", "m": 3},
    {"n": "Ochronnik T1+T2", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Różnicówka 4P 30mA", "c": "RCCB", "p": "40", "m": 4},
    {"n": "Różnicówka 2P 30mA", "c": "RCCB", "p": "25", "m": 2},
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1},
    {"n": "Wyłącznik 3P", "c": "B", "p": "16", "m": 3},
]

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Projektant v2.8")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

st.sidebar.divider()
opcje_tekst = [f"{u['c']}{u['p']} | {u['n']}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Wybierz aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])

# AUTOMATYKA FAZOWA
b_mod = BIBLIOTEKA[idx]['m']
if b_mod >= 3:
    faza_auto = "L123"
    st.sidebar.info("Aparat wielofazowy: Automatycznie L1+L2+L3")
else:
    domyslna_faza = FAZY_LISTA[st.session_state['next_faza_idx']]
    faza_auto = st.sidebar.selectbox("Faza (Sugestia automatu):", FAZY_LISTA, index=st.session_state['next_faza_idx'])

etyk = st.sidebar.text_input("Przeznaczenie:", "Gniazda")

if st.sidebar.button("Dodaj do szafy ➡️", use_container_width=True):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], faza_auto, etyk))
    
    # Przesunięcie automatu tylko dla aparatów 1P/2P
    if b['m'] < 3:
        st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Cofnij ostatni ⬅️"):
    if st.session_state['szyna']:
        # Przy cofaniu warto byłoby też cofnąć fazę, ale dla uproszczenia resetujemy do wyboru użytkownika
        st.session_state['szyna'].pop()
        st.rerun()

if st.sidebar.button("Wyczyść i Resetuj Fazy 🗑️"):
    st.session_state['szyna'] = []
    st.session_state['next_faza_idx'] = 0
    st.rerun()

# --- LOGIKA RZĘDÓW I WIZUALIZACJA ---
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD:
        rzedy.append([u]); akt_mod = u.moduly
    else:
        rzedy[-1].append(u); akt_mod += u.moduly



st.title("⚡ Projekt Rozdzielnicy - Automat Fazowy")
st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
        html_szyny = '<div class="szyna-din">'
        for i, u in enumerate(rzad):
            ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u.faza, "➖")
            html_szyny += f"""
            <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {brand_color};">
                <div class="aparat-brand" style="background-color:{brand_color};">{prod_name}</div>
                <div style="font-size:10px; font-weight:bold; background:#222; color:#fff; padding:2px;">R{r_i+1}-A{i+1}</div>
                <div style="font-size:14px; margin:5px 0;">{ico} {u.faza}</div>
                <div class="aparat-body">
                    <div style="font-size:9px; font-weight:bold; color:#444;">{u.nazwa}</div>
                    <div style="margin:8px 0;"><span style="font-size:14px; font-weight:bold;">{u.charakterystyka}</span><span class="amp-text">{u.prad}A</span></div>
                    <div class="aparat-label">{u.opis}</div>
                </div>
                <div class="aparat-footer">{"■"*u.moduly}<br>{u.moduly} MOD</div>
            </div>"""
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SPECYFIKACJA ---
if st.session_state['szyna']:
    st.divider()
    st.subheader("📋 Specyfikacja techniczna")
    for r_idx, rzad in enumerate(rzedy):
        if rzad:
            st.write(f"**Szyna nr {r_idx + 1}**")
            df = pd.DataFrame([{
                "Nr": f"A{i+1}", "Aparat": u.nazwa, "Zab.": f"{u.charakterystyka}{u.prad}A",
                "Przewód": u.przewod, "Faza": u.faza, "Opis": u.opis
            } for i, u in enumerate(rzad)])
            st.table(df)
