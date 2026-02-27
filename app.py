import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent Elektryka v3.0 - Nazwy Szyn", layout="wide")

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0
if 'nazwy_rzedow' not in st.session_state:
    st.session_state['nazwy_rzedow'] = {}

FAZY_LISTA = ["L1", "L2", "L3"]
U_N = 230  
RZAD_MAX_MOD = 12 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- POMOCNICZE ---
def dobierz_przewod(prad_str):
    try:
        p = int(''.join(filter(str.isdigit, prad_str)))
        if p <= 13: return "1.5 mm²"
        elif p <= 19: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        else: return "6.0 mm²+"
    except: return "wg projektu"

# --- CSS ---
st.markdown("""
    <style>
    .obudowa { background-color: #3d3d3d; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-header { color: #f1c40f; font-size: 18px; font-weight: bold; margin-bottom: 5px; border-left: 5px solid #f1c40f; padding-left: 10px; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 40px 15px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 20px solid #777; border-bottom: 20px solid #777;
        min-height: 400px; gap: 8px; margin-bottom: 40px;
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
    .faza-badge { font-size: 10px; padding: 2px 5px; border-radius: 3px; color: white; margin-bottom: 5px; display: inline-block; }
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
        try:
            self.moc_kw = round((U_N * int(''.join(filter(str.isdigit, prad))) * 0.6) / 1000, 2)
        except:
            self.moc_kw = 0.0

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

# --- SIDEBAR ---
st.sidebar.title("🛠️ Projektant v3.0")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

# LOGIKA PODZIAŁU DLA NAZW (potrzebna do sidebar)
rzedy_podglad = [[]]
akt_mod_p = 0
for u in st.session_state['szyna']:
    if akt_mod_p + u.moduly > RZAD_MAX_MOD:
        rzedy_podglad.append([u]); akt_mod_p = u.moduly
    else:
        rzedy_podglad[-1].append(u); akt_mod_p += u.moduly

st.sidebar.divider()
st.sidebar.subheader("🏷️ Nazwy Szyn DIN")
for r_idx in range(len(rzedy_podglad)):
    klucz = f"rzad_{r_idx}"
    domyslna = f"Szyna {r_idx + 1} - Przeznaczenie"
    st.session_state['nazwy_rzedow'][klucz] = st.sidebar.text_input(f"Przeznaczenie szyny #{r_idx+1}:", 
                                                                  value=st.session_state['nazwy_rzedow'].get(klucz, domyslna))

st.sidebar.divider()
st.sidebar.subheader("➕ Dodaj Aparat")
opcje_tekst = [f"{u['c']}{u['p']} | {u['n']}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Wybierz aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])

b_mod = BIBLIOTEKA[idx]['m']
faza_auto = "L123" if b_mod >= 3 else st.sidebar.selectbox("Faza (Automat):", FAZY_LISTA, index=st.session_state['next_faza_idx'])
etyk = st.sidebar.text_input("Opis obwodu:", "Gniazda")

if st.sidebar.button("Dodaj do szafy ➡️", use_container_width=True):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], faza_auto, etyk))
    if b['m'] < 3:
        st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

# --- ANALIZA MOCY ---
mocy_faz = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    if u.faza == "L123":
        for f in FAZY_LISTA: mocy_faz[f] += round(u.moc_kw / 3, 2)
    else:
        mocy_faz[u.faza] += u.moc_kw

# --- WIZUALIZACJA ---
st.title("⚡ Profesjonalny Projekt Rozdzielnicy")

# Wskaźniki mocy
c1, c2, c3 = st.columns(3)
c1.metric("Moc L1", f"{mocy_faz['L1']:.2f} kW")
c2.metric("Moc L2", f"{mocy_faz['L2']:.2f} kW")
c3.metric("Moc L3", f"{mocy_faz['L3']:.2f} kW")



st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy_podglad):
    if rzad:
        nazwa_szyny = st.session_state['nazwy_rzedow'].get(f"rzad_{r_i}", f"SZYNIA DIN #{r_i+1}")
        st.markdown(f'<div class="szyna-header">{nazwa_szyny.upper()}</div>', unsafe_allow_html=True)
        
        html_szyny = '<div class="szyna-din">'
        for i, u in enumerate(rzad):
            f_color = {"L1":"red","L2":"black","L3":"gray","L123":"blue"}.get(u.faza, "black")
            html_szyny += f"""
            <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {brand_color};">
                <div class="aparat-brand" style="background-color:{brand_color};">{prod_name}</div>
                <div style="padding:5px;">
                    <span class="faza-badge" style="background:{f_color};">{u.faza}</span>
                    <div style="font-size:9px; color:#666;">~{u.moc_kw}kW</div>
                </div>
                <div class="aparat-body">
                    <div style="font-size:12px; font-weight:bold;">{u.charakterystyka}{u.prad}</div>
                    <div class="aparat-label">{u.opis}</div>
                </div>
                <div class="aparat-footer">R{r_i+1}-A{i+1} | {u.moduly} MOD</div>
            </div>"""
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKUPY I SPECYFIKACJA ---
tab1, tab2 = st.tabs(["🛒 Lista Zakupowa", "📋 Specyfikacja Techniczna"])

with tab1:
    if st.session_state['szyna']:
        produkty = [f"{u.nazwa} {u.charakterystyka}{u.prad}A" for u in st.session_state['szyna']]
        df_zakupy = pd.Series(produkty).value_counts().reset_index()
        df_zakupy.columns = ['Aparat', 'Ilość [szt]']
        st.table(df_zakupy)

with tab2:
    if st.session_state['szyna']:
        for r_idx, rzad in enumerate(rzedy_podglad):
            if rzad:
                nazwa_s = st.session_state['nazwy_rzedow'].get(f"rzad_{r_idx}", f"Szyna {r_idx+1}")
                st.write(f"**{nazwa_s}**")
                df_t = pd.DataFrame([{
                    "Nr": f"A{i+1}", "Faza": u.faza, "Aparat": u.nazwa, 
                    "Zab.": f"{u.charakterystyka}{u.prad}A", "Przewód": u.przewod, "Opis": u.opis
                } for i, u in enumerate(rzad)])
                st.table(df_t)
