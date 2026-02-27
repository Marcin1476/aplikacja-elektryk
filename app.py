import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.7", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- DEFINICJA PRODUCENTÓW ---
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f8f9fa"},
    "Legrand": {"primary": "#E20613", "bg": "#fffafa"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f2fff5"},
    "Hager": {"primary": "#00305d", "bg": "#f0f4f7"},
    "Standard": {"primary": "#333", "bg": "#ffffff"}
}

# --- CSS (Wizualizacja z poprawioną czytelnością modułów) ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 60px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #888;
        border-bottom: 25px solid #888; min-height: 480px; gap: 4px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 6px 6px 12px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 380px; flex-shrink: 0;
        background-color: white;
    }
    .aparat-id { font-size: 11px; font-weight: bold; background: #222; color: #fff; padding: 3px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 9px; font-weight: bold; color: #444; text-transform: uppercase; height: 35px; border-bottom: 1px solid #eee; }
    
    .aparat-specs { margin: 15px 0; background: rgba(0,0,0,0.03); padding: 5px; border-radius: 5px; }
    .char-text { font-size: 16px; font-weight: bold; color: #444; }
    .amp-text { font-size: 32px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 12px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; 
                   padding: 4px; font-family: monospace; font-weight: bold; color: #000; }
    
    /* POPRAWIONA CZYTELNOŚĆ MODUŁÓW */
    .aparat-footer { 
        font-size: 11px; background: #444; color: white; padding: 6px; 
        border-top: 2px solid #222; font-weight: bold;
    }
    .moduly-icon { color: #f1c40f; letter-spacing: 2px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.opis = opis

# --- BIBLIOTEKA ---
BIBLIOTEKA_URZADZEN = [
    Urzadzenie("Rozłącznik Izolacyjny 3P", "FR", "100", 3),
    Urzadzenie("Ochronnik Przepięć T1+T2", "SPD", "B+C", 4),
    Urzadzenie("Różnicówka 2P 30mA", "RCCB", "25", 2),
    Urzadzenie("Różnicówka 2P 30mA", "RCCB", "40", 2),
    Urzadzenie("Różnicówka 4P 30mA", "RCCB", "40", 4),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "10", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "16", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "20", 1),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", "20", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "25", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "32", 3),
    Urzadzenie("Lampka kontrolna 3F", "L-L", "230V", 1),
]

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Konfiguracja")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

opcje_wyszukiwania = [f"{u.charakterystyka}{u.prad if u.prad.isdigit() else ''} | {u.nazwa}" for u in BIBLIOTEKA_URZADZEN]
wybor_idx = st.sidebar.selectbox("Szukaj urządzenia:", range(len(BIBLIOTEKA_URZADZEN)), format_func=lambda x: opcje_wyszukiwania[x], index=None, placeholder="Wpisz np. B16...")
etykieta = st.sidebar.text_input("Nazwa obwodu:", "")

if st.sidebar.button("Dodaj na szynę ➡️"):
    if wybor_idx is not None:
        w = BIBLIOTEKA_URZADZEN[wybor_idx]
        st.session_state['szyna'].append(Urzadzenie(w.nazwa, w.charakterystyka, w.prad, w.moduly, etykieta))
        st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- WIZUALIZACJA ---
st.title("⚡ Wirtualna Rozdzielnica")

html_szyna = ""
for i, u in enumerate(st.session_state.get('szyna', [])):
    szer = u.moduly * 60 # Zwiększona szerokość dla czytelności
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; background-color: {brand["bg"]};'
