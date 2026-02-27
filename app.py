import streamlit as st
import pandas as pd

# --- KONFIGURACJA ---
st.set_page_config(page_title="Projektant Rozdzielnicy v3.2 - Full Library", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0
if 'nazwy_rzedow' not in st.session_state:
    st.session_state['nazwy_rzedow'] = {}

FAZY_LISTA = ["L1", "L2", "L3"]
RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

# --- ROZBUDOWANA BIBLIOTEKA DANYCH ---
DB_APARATY = {
    "Zabezpieczenia Nadprądowe (MCB)": [
        {"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "13", "16", "20", "25", "32", "40", "50", "63"], "m": 1},
        {"n": "Wyłącznik 1P", "c": "C", "p": ["6", "10", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32", "40", "63"], "m": 3},
        {"n": "Wyłącznik 3P", "c": "C", "p": ["16", "20", "25", "32", "40", "63"], "m": 3},
        {"n": "Wyłącznik 3P", "c": "D", "p": ["16", "20", "25", "32"], "m": 3},
    ],
    "Różnicowoprądowe (RCD)": [
        {"n": "Różnicówka 2P 30mA", "c": "Typ AC", "p": ["25", "40", "63"], "m": 2},
        {"n": "Różnicówka 2P 30mA", "c": "Typ A", "p": ["25", "40"], "m": 2},
        {"n": "Różnicówka 4P 30mA", "c": "Typ AC", "p": ["25", "40", "63"], "m": 4},
        {"n": "Różnicówka 4P 30mA", "c": "Typ A", "p": ["40", "63"], "m": 4},
        {"n": "Różnicówka 4P 100mA", "c": "Typ AC", "p": ["40", "63"], "m": 4},
    ],
    "Ochrona i Rozłączanie": [
        {"n": "Rozłącznik Główny 3P", "c": "FR", "p": ["40", "63", "80", "100", "125"], "m": 3},
        {"n": "Ochronnik Przepięć T1+T2", "c": "SPD", "p": ["B+C"], "m": 4},
        {"n": "Rozłącznik Bezpiecznikowy 3P", "c": "RBK", "p": ["25", "32", "50"], "m": 3},
        {"n": "Ogranicznik Mocy", "c": "Etimat", "p": ["16", "20", "25"], "m": 3},
    ],
    "Automatyka i Kontrola": [
        {"n": "Lampka Kontrolna 3F", "c": "L-3", "p": ["230V"], "m": 1},
        {"n": "Licznik Energii 3F", "c": "MID", "p": ["80"], "m": 4},
        {"n": "Stycznik Modułowy 2P", "c": "ST", "p": ["25"], "m": 1},
        {"n": "Stycznik Modułowy 4P", "c": "ST", "p": ["25", "40", "63"], "m": 3},
        {"n": "Zegar Astronomiczny", "c": "TIME", "p": ["230V"], "m": 2},
        {"n": "Automatyczny Przełącznik Faz", "c": "APF", "p": ["16"], "m": 3},
        {"n": "Zasilacz Szynowy", "c": "DC", "p": ["12V", "24V"], "m": 2},
    ]
}

# --- POMOCNICZE ---
def dobierz_przewod(prad_str):
    try:
        p = int(''.join(filter(str.isdigit, prad_str)))
        if p <= 13: return "1.5 mm²"
        elif p <= 19: return "2.5 mm²"
        elif p <= 25: return "4.0 mm²"
        elif p <= 40: return "6.0 mm²"
        else: return "10.0 mm²+"
    except: return "wg dok."

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przewod = dobierz_przewod(prad)
        try: self.moc_kw = round((230 * int(''.join(filter(str.isdigit, prad))) * 0.6) / 1000, 2)
        except: self.moc_kw = 0.0

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Kreator Pro v3.2")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

st.sidebar.divider()
kat = st.sidebar.selectbox("Kategoria urządzenia:", list(DB_APARATY.keys()))
urzadzenia_w_kat = DB_APARATY[kat]
wybrane_u = st.sidebar.selectbox("Typ urządzenia:", range(len(urzadzenia_w_kat)), format_func=lambda x: f"{urzadzenia_w_kat[x]['n']} ({urzadzenia_w_kat[x]['c']})")
aparat_data = urzadzenia_w_kat[wybrane_u]
wybrany_prad = st.sidebar.selectbox("Prąd znamionowy / Parametr:", aparat_data['p'])

faza_auto = "L123" if aparat_data['m'] >= 3 else st.sidebar.selectbox("Faza:", FAZY_LISTA, index=st.session_state['next_faza_idx'])
etyk = st.sidebar.text_input("Przeznaczenie obwodu:", "Gniazda Salon")

if st.sidebar.button("Dodaj na szynę ➡️", use_container_width=True):
    st.session_state['szyna'].append(Urzadzenie(aparat_data['n'], aparat_data['c'], wybrany_prad, aparat_data['m'], faza_auto, etyk))
    if aparat_data['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

# --- WIZUALIZACJA ---
st.title(f"⚡ Rozdzielnica {prod_name} - Standard {RZAD_MAX_MOD} MOD")

# Podział na rzędy
rzedy = [[]]; akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_mod = u.moduly
    else: rzedy[-1].append(u); akt_mod += u.moduly



st.markdown('<div style="background-color:#333; padding:20px; border-radius:10px;">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.markdown(f'<div style="color:#f1c40f; font-weight:bold; margin-bottom:5px;">SZYNIA #{r_i+1}</div>', unsafe_allow_html=True)
        html = '<div style="display:flex; overflow-x:auto; background:#b0b0b0; padding:30px 10px; border-top:15px solid #777; border-bottom:15px solid #777; gap:5px; margin-bottom:20px;">'
        for i, u in enumerate(rzad):
            f_col = {"L1":"red","L2":"black","L3":"gray","L123":"blue"}.get(u.faza, "black")
            html += f"""
            <div style="width:{u.moduly*48}px; border:2px solid #000; background:#fff; flex-shrink:0; text-align:center; display:flex; flex-direction:column; min-height:340px; border-top:10px solid {brand_color};">
                <div style="font-size:8px; background:{brand_color}; color:#fff;">{prod_name}</div>
                <div style="font-size:12px; font-weight:bold; margin:5px 0;"><span style="color:{f_col};">●</span> {u.faza}</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:10px; font-weight:bold;">{u.nazwa}</div>
                    <div style="font-size:22px; font-weight:900; color:#d35400;">{u.charakterystyka}{u.prad}</div>
                </div>
                <div style="border:1px solid #ddd; margin:5px; font-size:9px; height:50px; display:flex; align-items:center; justify-content:center; font-weight:bold;">{u.opis}</div>
                <div style="background:#1a252f; color:#f1c40f; font-size:10px; padding:5px;">{u.moduly} MOD</div>
            </div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- RAPORTY ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 Specyfikacja techniczna")
    if st.session_state['szyna']:
        st.table(pd.DataFrame([{
            "Nr": f"F{i+1}", "Faza": u.faza, "Typ": f"{u.charakterystyka}{u.prad}", "Aparat": u.nazwa, "Przewód": u.przewod, "Opis": u.opis
        } for i, u in enumerate(st.session_state['szyna'])]))

with c2:
    st.subheader("🛒 Lista zakupowa")
    if st.session_state['szyna']:
        bom = pd.Series([f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]).value_counts().reset_index()
        bom.columns = ['Urządzenie', 'Ilość']
        st.table(bom)
