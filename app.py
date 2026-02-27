import streamlit as st
import pandas as pd

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Asystent Elektryka v3.4 - Full System", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0
if 'nazwy_rzedow' not in st.session_state:
    st.session_state['nazwy_rzedow'] = {}

# --- 2. STAŁE I PARAMETRY ---
FAZY_LISTA = ["L1", "L2", "L3"]
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- 3. PEŁNA BIBLIOTEKA DANYCH ---
DB_APARATY = {
    "Zabezpieczenia Nadprądowe (MCB)": [
        {"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "13", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 1P", "c": "C", "p": ["6", "10", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32", "40"], "m": 3},
        {"n": "Wyłącznik 3P", "c": "C", "p": ["16", "20", "25", "32", "40"], "m": 3},
    ],
    "Różnicowoprądowe (RCD)": [
        {"n": "Różnicówka 2P 30mA", "c": "Typ A/AC", "p": ["25", "40"], "m": 2},
        {"n": "Różnicówka 4P 30mA", "c": "Typ A/AC", "p": ["25", "40", "63"], "m": 4},
        {"n": "Różnicówka 4P 100mA", "c": "Typ AC", "p": ["40", "63"], "m": 4},
    ],
    "Ochrona i Rozłączanie": [
        {"n": "Rozłącznik Główny 3P", "c": "FR", "p": ["40", "63", "100"], "m": 3},
        {"n": "Ochronnik Przepięć T1+T2", "c": "SPD", "p": ["B+C"], "m": 4},
        {"n": "Rozłącznik Bezpiecznikowy", "c": "RBK", "p": ["25", "32"], "m": 3},
    ],
    "Automatyka i Kontrola": [
        {"n": "Lampka Kontrolna 3F", "c": "L-3", "p": ["230V"], "m": 1},
        {"n": "Licznik Energii 3F", "c": "MID", "p": ["80A"], "m": 4},
        {"n": "Stycznik Modułowy", "c": "ST", "p": ["25A", "40A"], "m": 3},
        {"n": "Zegar Astronomiczny", "c": "TIME", "p": ["24h"], "m": 2},
    ]
}

# --- 4. KLASA URZĄDZENIA ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis
        # Wyciąganie wartości prądu do obliczeń
        try:
            self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except:
            self.val_a = 0.0

# --- 5. PANEL BOCZNY ---
st.sidebar.title("🛠️ Projektant Pro v3.4")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

st.sidebar.divider()
st.sidebar.subheader("⚡ Parametry Sieci")
limit_gora = st.sidebar.number_input("Zab. przedlicznikowe [A]:", value=25)
wsp_j = st.sidebar.slider("Współczynnik jednoczesności:", 0.1, 1.0, 0.6)

st.sidebar.divider()
st.sidebar.subheader("📦 Biblioteka Modułów")
kat = st.sidebar.selectbox("Kategoria:", list(DB_APARATY.keys()))
ap_typ = st.sidebar.selectbox("Urządzenie:", DB_APARATY[kat], format_func=lambda x: f"{x['n']} ({x['c']})")
ap_prad = st.sidebar.selectbox("Parametr/Prąd:", ap_typ['p'])

f_auto = "L123" if ap_typ['m'] >= 3 else st.sidebar.selectbox("Faza:", FAZY_LISTA, index=st.session_state['next_faza_idx'])
etykieta = st.sidebar.text_input("Opis obwodu:", "Gniazda")

if st.sidebar.button("Dodaj do szafy ➡️", use_container_width=True):
    st.session_state['szyna'].append(Urzadzenie(ap_typ['n'], ap_typ['c'], ap_prad, ap_typ['m'], f_auto, etykieta))
    if ap_typ['m'] < 3:
        st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

# --- 6. OBLICZENIA OBCIĄŻALNOŚCI ---
obc = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    if u.charakterystyka not in ["FR", "SPD", "L-3"]: # Pomijamy aparaty niepobierające mocy roboczej
        if u.faza == "L123":
            for f in FAZY_LISTA: obc[f] += u.val_a * wsp_j
        else:
            obc[u.faza] += u.val_a * wsp_j

# --- 7. WIZUALIZACJA GÓRNA ---
st.title(f"⚡ Rozdzielnica {RZAD_MAX_MOD} MOD - Monitor Obciążenia")

cols = st.columns(3)
for i, f in enumerate(FAZY_LISTA):
    moc_kw = (obc[f] * 230) / 1000
    p_proc = min(obc[f] / limit_gora, 1.1)
    with cols[i]:
        st.metric(f"Faza {f}", f"{obc[f]:.1f} A", f"{moc_kw:.2f} kW")
        bar_c = "green" if p_proc < 0.8 else "orange" if p_proc < 1.0 else "red"
        st.markdown(f'<div style="background:#eee;height:10px;width:100%;border-radius:5px;"><div style="background:{bar_c};height:10px;width:{p_proc*100}%;border-radius:5px;"></div></div>', unsafe_allow_html=True)

# --- 8. RZĘDY I WIZUALIZACJA GRAFICZNA ---
rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly



st.markdown('<div style="background:#3d3d3d; padding:20px; border-radius:12px; border:6px solid #222;">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.markdown(f'<div style="color:#f1c40f; font-weight:bold; margin-bottom:5px;">SZYNIA #{r_i+1}</div>', unsafe_allow_html=True)
        html = '<div style="display:flex; overflow-x:auto; background:#b0b0b0; padding:30px 5px; border-top:15px solid #777; border-bottom:15px solid #777; gap:4px; margin-bottom:20px;">'
        for i, u in enumerate(rzad):
            f_col = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza, "black")
            html += f"""
            <div style="width:{u.moduly*48}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; display:flex; flex-direction:column; min-height:340px; border-top:10px solid {brand_color};">
                <div style="font-size:8px; background:{brand_color}; color:#fff; font-weight:bold;">{prod_name}</div>
                <div style="font-size:11px; font-weight:bold; padding:5px;"><span style="color:{f_col};">●</span> {u.faza}</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:9px; font-weight:bold; color:#444;">{u.nazwa}</div>
                    <div style="font-size:22px; font-weight:900; color:#d35400;">{u.charakterystyka}{u.prad}</div>
                </div>
                <div style="border:1px solid #ddd; margin:5px; font-size:10px; height:50px; display:flex; align-items:center; justify-content:center; font-weight:bold; background:#f9f9f9;">{u.opis}</div>
                <div style="background:#1a252f; color:#f1c40f; font-size:10px; padding:5px;">{u.moduly} MOD</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 9. RAPORTY ---
st.divider()
t1, t2 = st.tabs(["🛒 Lista Zakupowa", "📋 Dane Techniczne"])
with t1:
    if st.session_state['szyna']:
        bom = pd.Series([f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]).value_counts().reset_index()
        bom.columns = ['Aparat', 'Ilość [szt]']
        st.table(bom)
with t2:
    if st.session_state['szyna']:
        st.table(pd.DataFrame([{
            "Nr": f"F{i+1}", "Faza": u.faza, "Urządzenie": f"{u.nazwa} {u.charakterystyka}{u.prad}", "Moc robocza": f"{u.val_a * wsp_j:.1f} A", "Opis": u.opis
        } for i, u in enumerate(st.session_state['szyna'])]))
