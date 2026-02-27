import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.9 - System Fazowy", layout="wide")

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

FAZY_KOLORY = {
    "L1": "🔴",
    "L2": "⚫",
    "L3": "⚪",
    "L123": "🌈",
    "Brak": "➖"
}

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
    .aparat-faza { font-size: 16px; margin: 2px 0; }
    .aparat-id { font-size: 11px; font-weight: bold; background: #222; color: #fff; padding: 4px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 10px; font-weight: bold; color: #444; text-transform: uppercase; height: 40px; }
    .amp-text { font-size: 34px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 13px; min-height: 70px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; 
                   padding: 6px; font-family: monospace; font-weight: bold; color: #000; }
    .aparat-footer { background: #2c3e50; color: #f1c40f; padding: 10px 2px; }
    .mod-text { font-size: 12px; font-weight: 800; color: white; display: block; margin-top: 4px; }
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
st.sidebar.title("⚡ Parametry Projektu")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

st.sidebar.divider()
st.sidebar.subheader("➕ Dodaj Aparat")

opcje_szuk = [f"{u.charakterystyka}{u.prad if u.prad.isdigit() else ''} | {u.nazwa}" for u in BIBLIOTEKA]
wybor_idx = st.sidebar.selectbox("Szukaj:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_szuk[x], index=None)

# Dynamiczny wybór fazy tylko dla urządzeń 1-fazowych i 2-fazowych
wybrana_faza = "L123"
if wybor_idx is not None:
    moduly_wybranego = BIBLIOTEKA[wybor_idx].moduly
    if moduly_wybranego < 3:
        wybrana_faza = st.sidebar.radio("Wybierz fazę zasilającą:", ["L1", "L2", "L3"])

etykieta = st.sidebar.text_input("Etykieta (opis):", "")

if st.sidebar.button("Montuj na szynie ➡️"):
    if wybor_idx is not None:
        w = BIBLIOTEKA[wybor_idx]
        st.session_state['szyna'].append(Urzadzenie(w.nazwa, w.charakterystyka, w.prad, w.moduly, wybrana_faza
