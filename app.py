import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka Fundament v2.5.2", layout="wide")

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- PARAMETRY ---
RZAD_MAX_MOD = 12 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}
U_N = 230  

# --- CSS ---
st.markdown("""
    <style>
    .obudowa { background-color: #444; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 35px 15px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 18px solid #777; border-bottom: 18px solid #777;
        min-height: 400px; gap: 5px; margin-bottom: 30px;
    }
    .aparat {
        border: 2px solid #111; border-radius: 3px; text-align: center;
        box-shadow: 4px 4px 6px rgba(0,0,0,0.4); display: flex;
        flex-direction: column; min-height: 360px; flex-shrink: 0; background-color: white;
    }
    .aparat-brand { font-size: 9px; font-weight: bold; color: #fff; padding: 2px 0; text-transform: uppercase; }
    .amp-text { font-size: 28px; font-weight: 900; color: #e67e22; display: block; line-height: 1.1; }
    .aparat-label { border: 1px solid #ccc; background: #fdfdfd; font-size: 10px; min-height: 50px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 4px; font-weight: bold; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 8px 2px; margin-top: auto; font-size: 11px; }
    .short-circuit { font-size: 10px; color: #c0392b; font-weight: bold; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis="", zs=0.0, rcd_group="Brak"):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis
        self.zs = zs  
        self.rcd_group = rcd_group

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    {"n": "Rozłącznik Główny 3P", "c": "FR", "p": "100", "m": 3},
    {"n": "Ochronnik T1+T2", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Różnicówka 4P 30mA", "c": "RCCB", "p": "40", "m": 4},
    {"n": "Różnicówka 2P 30mA", "c": "RCCB", "p": "25", "m": 2},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 3P", "c": "B", "p": "16", "m": 3},
]

# --- SIDEBAR ---
st.sidebar.title("🛠️ Projektant v2.5.2")
wybrany_producent = st.sidebar.selectbox("Producent osprzętu:", list(PRODUCENCI.keys()))
kolor_brandu = PRODUCENCI[wybrany_producent]

st.sidebar.divider()
opcje_tekst = [f"{u['c']}{u['p']} | {u['n']}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Dodaj aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])

with st.sidebar.expander("Parametry dodatkowe", expanded=True):
    etyk = st.sidebar.text_input("Nazwa obwodu:", "Gniazda")
    faz = st.sidebar.radio("Zasilanie:", ["L1", "L2", "L3"]) if BIBLIOTEKA[idx]['m'] < 3 else "L123"
    zs_val = st.sidebar.number_input("Impedancja Zs [Ω]:", min_value=0.0, max_value=10.0, value=0.0, step=0.01)
    
    # Szukanie dostępnych RCD w sesji
    lista_rcd = ["Brak"] + [f"RCD {i+1}" for i, u in enumerate(st.session_state['szyna']) if "RCCB" in getattr(u, 'charakterystyka', '')]
    grupa_rcd = st.sidebar.selectbox("Przypisz do RCD:", lista_rcd)

if st.sidebar.button("Dodaj ➡️"):
    b = BIBLIOTEKA[idx]
    nowe = Urzadzenie(b['n'], b['c'], b['p'], b['m'], faz, etyk, zs_val, grupa_rcd)
    st.session_state['szyna'].append(nowe)
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']:
        st.session_state['szyna'].pop()
        st.rerun()

if st.sidebar.button("Resetuj projekt 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# --- LOGIKA PODZIAŁU NA RZĘDY ---
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    u_mod = getattr(u, 'moduly', 1)
    if akt_mod + u_mod > RZAD_MAX_MOD:
        rzedy.append([u])
        akt_mod = u_mod
    else:
        rzedy[-1].append(u)
        akt_mod += u_mod

# --- WIZUALIZACJA ---
st.title("⚡ Projekt Rozdzielnicy")


st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if not rzad and len(st.session_state['szyna']) == 0:
        st.info("Szafa jest pusta. Dodaj aparaty z panelu bocznego.")
        break
    
    if rzad:
        st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
        html_szyny = '<div class="szyna-din">'
        
        for i, u in enumerate(rzad):
            # Bezpieczne dane
            u_faza = getattr(u, 'faza', 'L1')
            u_zs = getattr(u, 'zs', 0.0)
            u_rcd = getattr(u, 'rcd_group', 'Brak')
            
            ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u_faza, "➖")
            ik_val = round(U_N / u_zs, 2) if u_zs > 0 else 0
            ik_html = f'<div class="short-circuit">Ik: {ik_val} A</div>' if u_zs > 0 else ""
            rcd_html = f'<div style="font-size:8px; color:#27ae60; font-weight:bold;">Grp: {u_rcd}</div>' if u_rcd != "Brak" else ""
            
            # Składanie HTML dla pojedynczego aparatu
            html_szyny += f"""
            <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {kolor_brandu};">
                <div class="aparat-brand" style="background-color:{kolor_brandu};">{wybrany_producent}</div>
                <div class="aparat-faza">{ico} {u_faza}</div>
                <div class="aparat-body">
                    <div style="font-size:9px; font-weight:bold;">{u.nazwa}</div>
                    <div style="margin:5px 0;"><span style="font-size:12px; font-weight:bold;">{u.charakterystyka}</span><span class="amp-text">{u.prad}A</span></div>
                    {ik_html} {rcd_html}
                    <div class="aparat-label">{u.opis}</div>
                </div>
                <div class="aparat-footer">{"■"*u.moduly}<br>{u.moduly} MOD</div>
            </div>"""
        
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- TABELA ANALIZY ---
st.divider()
if st.session_state['szyna']:
    st.subheader("📋 Zestawienie Techniczne")
    df_data = []
    for i, u in enumerate(st.session_state['szyna']):
        u_zs = getattr(u, 'zs', 0.0)
        df_data.append({
            "Aparat": f"F{i+1}",
            "Typ": f"{u.charakterystyka}{u.prad}A",
            "Zs [Ω]": u_zs,
            "Ik [A]": round(U_N / u_zs, 2) if u_zs > 0 else 0,
            "Grupa RCD": getattr(u, 'rcd_group', 'Brak'),
            "Opis": u.opis
        })
    st.table(pd.DataFrame(df_data))
