import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.8", layout="wide")

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

# --- POPRAWIONY CSS DLA CZYTELNOŚCI STOPKI ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 60px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #888;
        border-bottom: 25px solid #888; min-height: 500px; gap: 4px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 6px 6px 12px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 400px; flex-shrink: 0;
        background-color: white; overflow: hidden;
    }
    .aparat-id { font-size: 11px; font-weight: bold; background: #222; color: #fff; padding: 4px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 10px; font-weight: bold; color: #444; text-transform: uppercase; height: 40px; line-height: 1.2; }
    
    .aparat-specs { margin: 10px 0; padding: 5px; border-radius: 5px; background: #f0f0f0; }
    .char-text { font-size: 16px; font-weight: bold; color: #444; display: block; }
    .amp-text { font-size: 34px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 13px; min-height: 70px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; 
                   padding: 6px; font-family: 'Courier New', monospace; font-weight: bold; color: #000; border-radius: 3px;}
    
    /* NOWA, BARDZIEJ CZYTELNA STOPKA MODUŁÓW */
    .aparat-footer { 
        background: #2c3e50; color: #f1c40f; padding: 10px 2px;
        border-top: 2px solid #1a252f; margin-top: auto;
    }
    .mod-text { font-size: 12px; font-weight: 800; color: white; display: block; margin-top: 4px; letter-spacing: 1px; }
    .mod-icons { font-size: 16px; letter-spacing: 3px; line-height: 1; }
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
    Urzadzenie("Różnicówka 4P 30mA", "RCCB", "40", 4),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "10", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "16", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "20", 1),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", "20", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "32", 3),
]

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Konfiguracja")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

opcje_wyszukiwania = [f"{u.charakterystyka}{u.prad if u.prad.isdigit() else ''} | {u.nazwa}" for u in BIBLIOTEKA_URZADZEN]
wybor_idx = st.sidebar.selectbox("Szukaj urządzenia:", range(len(BIBLIOTEKA_URZADZEN)), format_func=lambda x: opcje_wyszukiwania[x], index=None, placeholder="Wpisz np. B16...")
etykieta = st.sidebar.text_input("Nazwa obwodu (Etykieta):", "")

if st.sidebar.button("Montuj na szynie ➡️"):
    if wybor_idx is not None:
        w = BIBLIOTEKA_URZADZEN[wybor_idx]
        st.session_state['szyna'].append(Urzadzenie(w.nazwa, w.charakterystyka, w.prad, w.moduly, etykieta))
        st.rerun()

st.sidebar.divider()
if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()
if st.sidebar.button("Wyczyść szynę 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title("⚡ Wirtualna Rozdzielnica")

html_szyna = ""
for i, u in enumerate(st.session_state.get('szyna', [])):
    szer = u.moduly * 65 # Szerokość bazy na moduł
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; border-left: 1px solid #ddd; border-right: 1px solid #ddd;'
    
    # Tworzenie żółtych kwadratów modułów
    mod_icons = "■" * u.moduly
    
    # Budowa HTML
    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-header">{u.nazwa}</div>'
    html_szyna += f'<div class="aparat-specs">'
    html_szyna += f'<span class="char-text">{u.charakterystyka}</span>'
    html_szyna += f'<span class="amp-text">{u.prad}{"A" if u.prad.isdigit() else ""}</span>'
    html_szyna += f'</div>'
    html_szyna += f'<div class="aparat-label">{u.opis if u.opis else "---"}</div>'
    html_szyna += f'</div>'
    # STOPKA Z MODUŁAMI
    html_szyna += f'<div class="aparat-footer">'
    html_szyna += f'<div class="mod-icons">{mod_icons}</div>'
    html_szyna += f'<div class="mod-text">{u.moduly} MODUŁ{"Y" if u.moduly > 1 else "" if u.moduly==1 else "ÓW"}</div>'
    html_szyna += f'</div>'
    html_szyna += f'</div>'

st.markdown(f'<div class="szyna-din">{html_szyna}</div>', unsafe_allow_html=True)

# PODSUMOWANIE
st.divider()
total_m = sum(u.moduly for u in st.session_state.get('szyna', []))
st.subheader(f"Zajęte miejsce na szynie: {total_m} modułów")
