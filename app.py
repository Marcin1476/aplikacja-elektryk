import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy v3.3 - Analiza Mocy", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

FAZY_LISTA = ["L1", "L2", "L3"]
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- BIBLIOTEKA (skrócona dla czytelności kodu, ale z pełną logiką) ---
DB_APARATY = {
    "Zabezpieczenia": [{"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "16", "20", "25"], "m": 1},
                       {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32"], "m": 3}],
    "Różnicówki": [{"n": "Różnicówka 2P", "c": "A", "p": ["25", "40"], "m": 2},
                   {"n": "Różnicówka 4P", "c": "AC", "p": ["25", "40"], "m": 4}]
}

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        try:
            self.val_a = float(''.join(filter(str.isdigit, prad)))
        except:
            self.val_a = 0.0

# --- SIDEBAR ---
st.sidebar.title("🛠️ Analiza Obciążenia v3.3")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

st.sidebar.divider()
st.sidebar.subheader("⚙️ Parametry Zasilania")
limit_a = st.sidebar.number_input("Zabezpieczenie przedlicznikowe [A]:", value=25)
wsp_jedn = st.sidebar.slider("Współczynnik jednoczesności:", 0.1, 1.0, 0.6)

st.sidebar.divider()
kat = st.sidebar.selectbox("Kategoria:", list(DB_APARATY.keys()))
ap_data = st.sidebar.selectbox("Typ:", DB_APARATY[kat], format_func=lambda x: f"{x['n']} {x['c']}")
prad_sel = st.sidebar.selectbox("Prąd [A]:", ap_data['p'])
etyk = st.sidebar.text_input("Opis:", "Obwód")
f_auto = "L123" if ap_data['m'] >= 3 else st.sidebar.selectbox("Faza:", FAZY_LISTA, index=st.session_state['next_faza_idx'])

if st.sidebar.button("Dodaj ➡️"):
    st.session_state['szyna'].append(Urzadzenie(ap_data['n'], ap_data['c'], prad_sel, ap_data['m'], f_auto, etyk))
    if ap_data['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Wyczyść 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- OBLICZENIA OBCIĄŻALNOŚCI ---
obciazenie = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    # Nie liczymy Rozłączników i SPD jako odbiorników
    if u.charakterystyka not in ["FR", "SPD"]:
        if u.faza == "L123":
            for f in FAZY_LISTA: obciazenie[f] += u.val_a * wsp_jedn
        else:
            obciazenie[u.faza] += u.val_a * wsp_jedn

# --- WIZUALIZACJA ---
st.title("⚡ Monitoring Obciążenia Fazowego")



cols = st.columns(3)
for i, f in enumerate(FAZY_LISTA):
    moc_kw = (obciazenie[f] * 230) / 1000
    proc = min(obciazenie[f] / limit_a, 1.2)
    
    with cols[i]:
        st.metric(f"Faza {f}", f"{obciazenie[f]:.1f} A", f"{moc_kw:.2f} kW")
        color = "green" if proc < 0.8 else "orange" if proc < 1.0 else "red"
        st.markdown(f"""
            <div style="background:#eee; border-radius:10px; height:20px; width:100%;">
                <div style="background:{color}; height:20px; width:{proc*100}%; border-radius:10px;"></div>
            </div>
            """, unsafe_allow_html=True)
        if proc >= 1.0: st.warning(f"Przeciążenie {f}!")

# Wizualizacja szyny
rzedy = [[]]; akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_mod = u.moduly
    else: rzedy[-1].append(u); akt_mod += u.moduly

st.markdown('<div style="background:#333; padding:20px; border-radius:10px;">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        html = '<div style="display:flex; background:#b0b0b0; padding:30px 5px; border-top:15px solid #777; border-bottom:15px solid #777; gap:3px; margin-bottom:15px;">'
        for u in rzad:
            f_c = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza)
            html += f"""
            <div style="width:{u.moduly*45}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; min-height:300px; border-top:10px solid {brand_color};">
                <div style="font-size:10px; font-weight:bold; color:{f_c};">{u.faza}</div>
                <div style="font-size:18px; font-weight:900;">{u.charakterystyka}{u.prad}</div>
                <div style="font-size:9px; margin-top:10px; padding:2px; height:40px; overflow:hidden;">{u.opis}</div>
                <div style="background:#1a252f; color:#f1c40f; font-size:9px; margin-top:auto; padding:3px;">{u.moduly}M</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
