import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy 18-mod", layout="wide")

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0
if 'nazwy_rzedow' not in st.session_state:
    st.session_state['nazwy_rzedow'] = {}

FAZY_LISTA = ["L1", "L2", "L3"]
U_N = 230  
# --- KLUCZOWA ZMIANA: 18 MODUŁÓW ---
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- POMOCNICZE ---
def dobierz_przewod(prad_str):
    try:
        p = int(''.join(filter(str.isdigit, prad_str)))
        if p <= 13: return "1.5 mm²"
        elif p <= 19: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 35: return "6.0 mm²"
        else: return "10.0 mm²+"
    except: return "wg projektu"

# --- CSS (Dostosowany do 18 modułów) ---
st.markdown("""
    <style>
    .obudowa { background-color: #3d3d3d; padding: 25px; border-radius: 12px; border: 6px solid #222; width: 100%; }
    .szyna-header { color: #f1c40f; font-size: 18px; font-weight: bold; margin-bottom: 5px; border-left: 5px solid #f1c40f; padding-left: 10px; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 40px 10px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 20px solid #777; border-bottom: 20px solid #777;
        min-height: 400px; gap: 4px; margin-bottom: 40px; width: 100%;
    }
    .aparat {
        border: 2px solid #111; border-radius: 4px; text-align: center;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.5); display: flex;
        flex-direction: column; min-height: 350px; flex-shrink: 0; background-color: white;
    }
    .aparat-brand { font-size: 9px; font-weight: bold; color: #fff; padding: 2px 0; text-transform: uppercase; }
    .amp-text { font-size: 26px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    .aparat-label { border: 1px solid #ccc; background: #fdfdfd; font-size: 10px; min-height: 55px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 3px; font-weight: bold; }
    .faza-badge { font-size: 9px; padding: 2px 4px; border-radius: 2px; color: white; margin-bottom: 3px; display: inline-block; }
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
st.sidebar.title("🛠️ Projektant 18-mod")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

# Podział na rzędy
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD:
        rzedy.append([u]); akt_mod = u.moduly
    else:
        rzedy[-1].append(u); akt_mod += u.moduly

st.sidebar.divider()
st.sidebar.subheader("🏷️ Nazwy Szyn")
for r_idx in range(len(rzedy)):
    klucz = f"rzad_{r_idx}"
    st.session_state['nazwy_rzedow'][klucz] = st.sidebar.text_input(f"Przeznaczenie szyny #{r_idx+1}:", 
                                                                  value=st.session_state['nazwy_rzedow'].get(klucz, f"Szyna {r_idx+1}"))

st.sidebar.divider()
idx = st.sidebar.selectbox("Dodaj aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: f"{BIBLIOTEKA[x]['c']}{BIBLIOTEKA[x]['p']} | {BIBLIOTEKA[x]['n']}")
etyk = st.sidebar.text_input("Opis:", "Obwód")
faza_auto = "L123" if BIBLIOTEKA[idx]['m'] >= 3 else st.sidebar.selectbox("Faza:", FAZY_LISTA, index=st.session_state['next_faza_idx'])

if st.sidebar.button("Dodaj ➡️", use_container_width=True):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b['n'], b['c'], b['p'], b['m'], faza_auto, etyk))
    if b['m'] < 3:
        st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

# --- WIZUALIZACJA ---
st.title(f"⚡ Rozdzielnica {RZAD_MAX_MOD} modułowa")

# Obliczenia mocy
m_faz = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    if u.faza == "L123":
        for f in FAZY_LISTA: m_faz[f] += round(u.moc_kw / 3, 2)
    else: m_faz[u.faza] += u.moc_kw

c1, c2, c3 = st.columns(3)
c1.metric("Moc L1", f"{m_faz['L1']:.2f} kW", delta_color="inverse")
c2.metric("Moc L2", f"{m_faz['L2']:.2f} kW", delta_color="inverse")
c3.metric("Moc L3", f"{m_faz['L3']:.2f} kW", delta_color="inverse")



st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        nazwa = st.session_state['nazwy_rzedow'].get(f"rzad_{r_i}", f"SZYNIA #{r_i+1}")
        st.markdown(f'<div class="szyna-header">{nazwa.upper()}</div>', unsafe_allow_html=True)
        html_szyny = '<div class="szyna-din">'
        for i, u in enumerate(rzad):
            f_col = {"L1":"red","L2":"black","L3":"gray","L123":"blue"}.get(u.faza, "black")
            # Skalowanie szerokości: dla 18 modułów 50px na moduł to ok. 900px szerokości szyny
            html_szyny += f"""
            <div class="aparat" style="width:{u.moduly*50}px; border-top: 15px solid {brand_color};">
                <div class="aparat-brand" style="background-color:{brand_color};">{prod_name}</div>
                <div style="font-size:9px; background:#eee; padding:2px;">R{r_i+1}-A{i+1}</div>
                <div style="padding:4px;">
                    <span class="faza-badge" style="background:{f_col};">{u.faza}</span>
                    <div style="font-size:8px; color:#666;">~{u.moc_kw}kW</div>
                </div>
                <div class="aparat-body">
                    <div style="font-size:11px; font-weight:bold;">{u.charakterystyka}{u.prad}</div>
                    <div class="aparat-label">{u.opis}</div>
                </div>
                <div class="aparat-footer">{u.moduly} MOD</div>
            </div>"""
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKUPY I TABELA ---
tab1, tab2 = st.tabs(["🛒 Zakupy", "📋 Specyfikacja"])
with tab1:
    if st.session_state['szyna']:
        produkty = [f"{u.nazwa} {u.charakterystyka}{u.prad}A" for u in st.session_state['szyna']]
        st.table(pd.Series(produkty).value_counts().reset_index().rename(columns={"index":"Aparat", 0:"Sztuk"}))

with tab2:
    if st.session_state['szyna']:
        for r_idx, rzad in enumerate(rzedy):
            if rzad:
                st.write(f"**{st.session_state['nazwy_rzedow'].get(f'rzad_{r_idx}', 'Szyna')}**")
                st.table(pd.DataFrame([{
                    "Nr": f"A{i+1}", "Faza": u.faza, "Zab.": f"{u.charakterystyka}{u.prad}A",
                    "Przewód": u.przewod, "Opis": u.opis
                } for i, u in enumerate(rzad)]))
