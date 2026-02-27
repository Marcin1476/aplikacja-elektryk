import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent Elektryka v3.7 - Dokumentacja", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

# --- STYLE CSS (W TYM OBSŁUGA WYDRUKU) ---
st.markdown("""
    <style>
    /* Ukrywanie panelu bocznego i przycisków podczas drukowania */
    @media print {
        section[data-testid="stSidebar"], .stButton, header, footer, [data-testid="stDecoration"] {
            display: none !important;
        }
        .main .block-container {
            padding-top: 10px !important;
        }
        .obudowa {
            background-color: white !important;
            border: 2px solid black !important;
        }
        .szyna-din {
            background-color: #f9f9f9 !important;
            border: 1px solid #000 !important;
        }
    }
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; }
    .szyna-din {
        display: flex; flex-direction: row; background-color: #b0b0b0;
        padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777;
        gap: 4px; margin-bottom: 15px; overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PARAMETRY I BIBLIOTEKA ---
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

DB_APARATY = {
    "Zabezpieczenia Nadprądowe (MCB)": [
        {"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "13", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32", "40"], "m": 3},
    ],
    "Różnicowoprądowe (RCD)": [
        {"n": "Różnicówka 2P 30mA", "c": "Typ A", "p": ["25", "40"], "m": 2},
        {"n": "Różnicówka 4P 30mA", "c": "Typ A", "p": ["25", "40", "63"], "m": 4},
    ],
    "Pozostałe": [
        {"n": "Rozłącznik Główny 3P", "c": "FR", "p": ["63", "100"], "m": 3},
        {"n": "Ochronnik T1+T2", "c": "SPD", "p": ["B+C"], "m": 4},
        {"n": "Lampka Kontrolna", "c": "L-3", "p": ["230V"], "m": 1},
    ]
}

def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm²"
        elif p <= 20: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 40: return "6.0 mm²"
        else: return "10.0 mm²+"
    except: return "wg dok."

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)
        try: self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except: self.val_a = 0.0

# --- SIDEBAR ---
st.sidebar.title("🛠️ Projektant v3.7")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

# Dane do wydruku
st.sidebar.divider()
st.sidebar.subheader("📝 Dane inwestycji")
klient = st.sidebar.text_input("Inwestor:", "Projekt domyślny")
miejsce = st.sidebar.text_input("Lokalizacja:", "Rozdzielnica Główna")

st.sidebar.divider()
wsp_j = st.sidebar.slider("Współczynnik jednoczesności:", 0.1, 1.0, 0.6)
limit_a = st.sidebar.number_input("Limit przedlicznikowy [A]:", value=25)

st.sidebar.divider()
kat = st.sidebar.selectbox("Kategoria:", list(DB_APARATY.keys()))
ap_typ = st.sidebar.selectbox("Urządzenie:", DB_APARATY[kat], format_func=lambda x: f"{x['n']} ({x['c']})")
ap_prad = st.sidebar.selectbox("Prąd/Parametr:", ap_typ['p'])
f_auto = "L123" if ap_typ['m'] >= 3 else st.sidebar.selectbox("Faza:", ["L1", "L2", "L3"], index=st.session_state['next_faza_idx'])
etyk = st.sidebar.text_input("Opis obwodu:", "Gniazda Salon")

if st.sidebar.button("Dodaj do szafy ➡️", use_container_width=True):
    st.session_state['szyna'].append(Urzadzenie(ap_typ['n'], ap_typ['c'], ap_prad, ap_typ['m'], f_auto, etyk))
    if ap_typ['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

if st.sidebar.button("Resetuj projekt 🗑️"):
    st.session_state['szyna'] = []; st.session_state['next_faza_idx'] = 0; st.rerun()

# --- ANALIZA OBCIĄŻALNOŚCI ---
obc = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
for u in st.session_state['szyna']:
    if u.charakterystyka not in ["FR", "SPD"]:
        if u.faza == "L123":
            for f in ["L1", "L2", "L3"]: obc[f] += u.val_a * wsp_j
        else: obc[u.faza] += u.val_a * wsp_j

# --- WIZUALIZACJA ---
st.title("📄 DOKUMENTACJA TECHNICZNA ROZDZIELNICY")
st.write(f"**Inwestor:** {klient} | **Lokalizacja:** {miejsce}")

# Paski obciążenia (Tylko na ekranie)
cols = st.columns(3)
for i, f in enumerate(["L1", "L2", "L3"]):
    p_proc = min(obc[f] / limit_a, 1.1)
    with cols[i]:
        st.metric(f"Faza {f}", f"{obc[f]:.1f} A")
        b_c = "green" if p_proc < 0.8 else "orange" if p_proc < 1.0 else "red"
        st.markdown(f'<div class="no-print" style="background:#eee;height:8px;width:100%;border-radius:4px;"><div style="background:{b_c};height:8px;width:{p_proc*100}%;border-radius:4px;"></div></div>', unsafe_allow_html=True)

# Rzędy
rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.markdown(f'<div style="color:#f1c40f; font-weight:bold;">SZYNIA DIN NR {r_i+1}</div>', unsafe_allow_html=True)
        html = '<div class="szyna-din">'
        for u in rzad:
            f_c = {"L1":"red","L2":"black","L3":"#555","L123":"blue"}.get(u.faza)
            html += f"""
            <div style="width:{u.moduly*48}px; border:1px solid #000; background:#fff; flex-shrink:0; text-align:center; min-height:280px; display:flex; flex-direction:column; border-top:8px solid {brand_color};">
                <div style="font-size:9px; font-weight:bold; color:{f_c};">{u.faza}</div>
                <div style="font-size:18px; font-weight:900; color:#d35400; flex-grow:1; display:flex; align-items:center; justify-content:center; flex-direction:column;">
                    {u.charakterystyka}{u.prad}
                    <div style="font-size:9px; color:#555;">{u.przekroj}</div>
                </div>
                <div style="border-top:1px solid #ddd; padding:3px; height:50px; font-size:9px; font-weight:bold; display:flex; align-items:center; justify-content:center; background:#f9f9f9;">{u.opis}</div>
                <div style="background:#1a252f; color:#f1c40f; font-size:9px; padding:3px;">{u.moduly}M</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TABELA DANYCH TECHNICZNYCH ---
st.divider()
if st.session_state['szyna']:
    st.header("1. Specyfikacja obwodów")
    df = pd.DataFrame([{
        "Poz.": i+1, "Aparat": f"{u.charakterystyka}{u.prad}", "Faza": u.faza,
        "Przewód": u.przekroj, "Opis/Przeznaczenie": u.opis
    } for i, u in enumerate(st.session_state['szyna'])])
    st.table(df)

    # --- ZESTAWIENIE MATERIAŁOWE (BOM) ---
    st.header("2. Zbiorcze zestawienie materiałów")
    
    zestawienie = []
    for u in st.session_state['szyna']:
        zestawienie.append(f"{u.nazwa} {u.charakterystyka}{u.prad} ({prod_name})")
    
    df_bom = pd.Series(zestawienie).value_counts().reset_index()
    df_bom.columns = ['Element instalacji', 'Ilość [szt]']
    st.table(df_bom)

    st.info("💡 Aby zapisać do PDF: Użyj skrótu Ctrl+P i wybierz 'Zapisz jako PDF'.")
else:
    st.info("Dodaj aparaty, aby wygenerować dokumentację.")
