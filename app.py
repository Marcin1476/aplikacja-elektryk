import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.9.1", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- DEFINICJA PRODUCENTÓW I FAZ ---
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f8f9fa"},
    "Legrand": {"primary": "#E20613", "bg": "#fffafa"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f2fff5"},
    "Hager": {"primary": "#00305d", "bg": "#f0f4f7"},
    "Standard": {"primary": "#333", "bg": "#ffffff"}
}

FAZY_KOLORY = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}

# --- CSS ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 60px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #888;
        border-bottom: 25px solid #888; min-height: 520px; gap: 4px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 6px 6px 12px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 420px; flex-shrink: 0;
        background-color: white; overflow: hidden;
    }
    .aparat-faza { font-size: 14px; font-weight: bold; margin: 4px 0; }
    .aparat-id { font-size: 11px; font-weight: bold; background: #222; color: #fff; padding: 4px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 10px; font-weight: bold; color: #444; text-transform: uppercase; height: 40px; }
    .amp-text { font-size: 34px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 13px; min-height: 70px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; 
                   padding: 6px; font-family: monospace; font-weight: bold; color: #000; }
    .aparat-footer { background: #2c3e50; color: #f1c40f; padding: 10px 2px; margin-top: auto; }
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

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    Urzadzenie("Rozłącznik 3P", "FR", "100", 3, "L123"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "B+C", 4, "L123"),
    Urzadzenie("Różnicówka 2P", "RCCB", "25", 2, "L1"),
    Urzadzenie("Różnicówka 4P", "RCCB", "40", 4, "L123"),
    Urzadzenie("Wyłącznik 1P", "B", "10", 1, "L1"),
    Urzadzenie("Wyłącznik 1P", "B", "16", 1, "L1"),
    Urzadzenie("Wyłącznik 1P", "C", "20", 1, "L1"),
    Urzadzenie("Wyłącznik 3P", "B", "16", 3, "L123"),
    Urzadzenie("Wyłącznik 3P", "C", "25", 3, "L123"),
]

# --- PANEL BOCZNY ---
st.sidebar.title("⚡ Panel Konfiguracji")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

st.sidebar.divider()
opcje_szuk = [f"{u.charakterystyka}{u.prad if u.prad.isdigit() else ''} | {u.nazwa}" for u in BIBLIOTEKA]
wybor_idx = st.sidebar.selectbox("Szukaj aparatu:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_szuk[x], index=None)

faza_finalna = "L123"
if wybor_idx is not None:
    if BIBLIOTEKA[wybor_idx].moduly < 3:
        faza_finalna = st.sidebar.radio("Wybierz fazę:", ["L1", "L2", "L3"])

etykieta = st.sidebar.text_input("Etykieta obwodu:", "")

if st.sidebar.button("Dodaj do projektu ➡️"):
    if wybor_idx is not None:
        base = BIBLIOTEKA[wybor_idx]
        nowe = Urzadzenie(base.nazwa, base.charakterystyka, base.prad, base.moduly, faza_finalna, etykieta)
        st.session_state['szyna'].append(nowe)
        st.rerun()

if st.sidebar.button("Cofnij ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

# --- WIZUALIZACJA ---
st.title("⚡ Wirtualna Rozdzielnica - System Fazowy")



html_szyna = ""
bilans = {"L1": 0, "L2": 0, "L3": 0}

for i, u in enumerate(st.session_state.get('szyna', [])):
    szer = u.moduly * 65
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]};'
    ico = FAZY_KOLORY.get(u.faza, "➖")
    
    if u.faza == "L123":
        for k in bilans: bilans[k] += 1
    elif u.faza in bilans:
        bilans[u.faza] += 1

    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-faza">{ico} {u.faza}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-header">{u.nazwa}</div>'
    html_szyna += f'<div style="background:#f0f0f0;padding:5px;border-radius:5px;">'
    html_szyna += f'<span style="font-size:14px;font-weight:bold;">{u.charakterystyka}</span>'
    html_szyna += f'<span class="amp-text">{u.prad}{"A" if u.prad.isdigit() else ""}</span></div>'
    html_szyna += f'<div class="aparat-label">{u.opis if u.opis else "---"}</div></div>'
    html_szyna += f'<div class="aparat-footer"><div>{"■"*u.moduly}</div>'
    html_szyna += f'<div style="font-size:11px;">{u.moduly} MOD</div></div></div>'

st.markdown(f'<div class="szyna-din">{html_szyna}</div>', unsafe_allow_html=True)

# --- BILANS ---
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Faza L1 (🔴)", f"{bilans['L1']} szt.")
c2.metric("Faza L2 (⚫)", f"{bilans['L2']} szt.")
c3.metric("Faza L3 (⚪)", f"{bilans['L3']} szt.")
total_m = sum(u.moduly for u in st.session_state.get('szyna', []))
c4.metric("Suma Modułów", f"{total_m} DIN")
