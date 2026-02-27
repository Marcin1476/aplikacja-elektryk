import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy - Stabilny Fundament", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- PARAMETRY ---
RZAD_MAX_MOD = 12 
PRODUCENCI = {
    "Eaton": "#005EB8", 
    "Legrand": "#E20613", 
    "Schneider": "#3dcd58", 
    "Hager": "#00305d"
}

# --- CSS (Sprawdzony układ graficzny) ---
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
                   display: flex; align-items: center; justify-content: center; margin: 8px; padding: 4px; font-weight: bold; color: #000; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 10px 2px; margin-top: auto; font-size: 11px; border-top: 1px solid #000; }
    </style>
    """, unsafe_allow_html=True)

# --- KLASA DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    {"n": "Rozłącznik Główny 3P", "c": "FR", "p": "100", "m": 3},
    {"n": "Ochronnik T1+T2", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Różnicówka 4P 30mA", "c": "RCCB", "p": "40", "m": 4},
    {"n": "Różnicówka 2P 30mA", "c": "RCCB", "p": "25", "m": 2},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 1P", "c": "C", "p": "20", "m": 1},
    {"n": "Wyłącznik 3P", "c": "B", "p": "16", "m": 3},
    {"n": "Wyłącznik 3P", "c": "C", "p": "25", "m": 3},
]

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Projektant v2.6")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

st.sidebar.divider()
opcje_tekst = [f"{u['c']}{u['p']} | {u['n']}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Wybierz aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])

etyk = st.sidebar.text_input("Nazwa obwodu:", "Gniazda")
faz = st.sidebar.radio("Zasilanie:", ["L1", "L2", "L3"]) if BIBLIOTEKA[idx]['m'] < 3 else "L123"

if st.sidebar.button("Dodaj na szynę ➡️", use_container_width=True):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], faz, etyk))
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']:
        st.session_state['szyna'].pop()
        st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# --- LOGIKA PODZIAŁU NA RZĘDY ---
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD:
        rzedy.append([u])
        akt_mod = u.moduly
    else:
        rzedy[-1].append(u)
        akt_mod += u.moduly

# --- WIZUALIZACJA ---
st.title("⚡ Projekt Rozdzielnicy")



st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if not rzad and len(st.session_state['szyna']) == 0:
        st.info("Dodaj aparaty z panelu bocznego, aby rozpocząć projekt.")
        break
    
    if rzad:
        st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
        html_szyny = '<div class="szyna-din">'
        for i, u in enumerate(rzad):
            ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u.faza, "➖")
            
            html_szyny += f"""
            <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {brand_color};">
                <div class="aparat-brand" style="background-color:{brand_color};">{prod_name}</div>
                <div style="font-size:11px; font-weight:bold; background:#222; color:#fff; padding:2px;">R{r_i+1}-A{i+1}</div>
                <div style="font-size:14px; margin:5px 0;">{ico} {u.faza}</div>
                <div class="aparat-body">
                    <div style="font-size:9px; font-weight:bold; color:#444;">{u.nazwa}</div>
                    <div style="margin:8px 0;">
                        <span style="font-size:14px; font-weight:bold;">{u.charakterystyka}</span>
                        <span class="amp-text">{u.prad}A</span>
                    </div>
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
    st.subheader("📋 Specyfikacja techniczna rzędowa")
    for r_idx, rzad in enumerate(rzedy):
        if rzad:
            st.write(f"**Szyna nr {r_idx + 1} ({prod_name})**")
            dane = [{
                "Nr": f"A{i+1}",
                "Aparat": u.nazwa,
                "Zabezpieczenie": f"{u.charakterystyka}{u.prad}A",
                "Faza": u.faza,
                "Przeznaczenie": u.opis
            } for i, u in enumerate(rzad)]
            st.table(pd.DataFrame(dane))
