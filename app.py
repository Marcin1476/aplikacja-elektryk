import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.5", layout="wide")

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

# --- CSS (Wizualizacja) ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 50px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #888;
        border-bottom: 25px solid #888; min-height: 450px; gap: 4px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 350px; flex-shrink: 0;
    }
    .aparat-id { font-size: 10px; font-weight: bold; background: #222; color: #fff; padding: 2px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 9px; font-weight: bold; color: #555; text-transform: uppercase; height: 35px; overflow: hidden; }
    .aparat-specs { margin: 15px 0; }
    .char-text { font-size: 14px; font-weight: bold; color: #444; }
    .amp-text { font-size: 26px; font-weight: 900; color: #d35400; display: block; }
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 11px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 2px; overflow: hidden; }
    .aparat-footer { font-size: 10px; background: #ddd; padding: 4px; border-top: 1px solid #888; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.opis = opis

# --- ROZBUDOWANA BIBLIOTEKA ---
BIBLIOTEKA_URZADZEN = [
    # ZABEZPIECZENIA GŁÓWNE
    Urzadzenie("Rozłącznik Izolacyjny 3P (Główny)", "FR", "100", 3),
    Urzadzenie("Ochronnik Przepięć T1+T2", "SPD", "B+C", 4),
    
    # RÓŻNICÓWKI (RCD)
    Urzadzenie("Różnicówka 2P (RCD)", "AC", "25A/30mA", 2),
    Urzadzenie("Różnicówka 2P (RCD)", "AC", "40A/30mA", 2),
    Urzadzenie("Różnicówka 4P (RCD)", "AC", "25A/30mA", 4),
    Urzadzenie("Różnicówka 4P (RCD)", "AC", "40A/30mA", 4),

    # WYŁĄCZNIKI NADPRĄDOWE 1P (Charakterystyka B)
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "6", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "10", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "16", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "20", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "25", 1),

    # WYŁĄCZNIKI NADPRĄDOWE 1P (Charakterystyka C)
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "10", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "16", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "20", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "25", 1),

    # WYŁĄCZNIKI NADPRĄDOWE 3P
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", "16", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", "25", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "20", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "25", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "32", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "40", 3),

    # APARATURA MODUŁOWA INNA
    Urzadzenie("Lampka kontrolna 3-fazowa", "L-L", "230V", 1),
    Urzadzenie("Stycznik modułowy 1P", "ST", "25", 1),
    Urzadzenie("Stycznik modułowy 3P", "ST", "40", 3),
    Urzadzenie("Zegar sterujący", "TIME", "24h", 2),
]

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Biblioteka Aparatury")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

opcje = [f"{u.nazwa} {u.charakterystyka} {u.prad}A" for u in BIBLIOTEKA_URZADZEN]
wybor_idx = st.sidebar.selectbox("Wybierz urządzenie:", range(len(BIBLIOTEKA_URZADZEN)), format_func=lambda x: opcje[x])
wybor = BIBLIOTEKA_URZADZEN[wybor_idx]

etykieta = st.sidebar.text_input("Etykieta obwodu:", "Obwód")

if st.sidebar.button("Montuj na szynie ➡️"):
    nowy = Urzadzenie(wybor.nazwa, wybor.charakterystyka, wybor.prad, wybor.moduly, etykieta)
    st.session_state['szyna'].append(nowy)
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']:
        st.session_state['szyna'].pop()
        st.rerun()

if st.sidebar.button("Wyczyść rozdzielnicę 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# --- WIZUALIZACJA ---
st.title("⚡ Wirtualna Rozdzielnica")



html_szyna = ""
for i, u in enumerate(st.session_state.get('szyna', [])):
    szer = u.moduly * 55
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; background-color: {brand["bg"]};'
    
    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-header">{u.nazwa}</div>'
    html_szyna += f'<div class="aparat-specs">'
    html_szyna += f'<span class="char-text">{u.charakterystyka}</span>'
    html_szyna += f'<span class="amp-text">{u.prad}{"A" if u.prad.isdigit() else ""}</span>'
    html_szyna += f'</div>'
    html_szyna += f'<div class="aparat-label">{u.opis}</div>'
    html_szyna += f'</div>'
    html_szyna += f'<div class="aparat-footer">{u.moduly} MOD</div>'
    html_szyna += f'</div>'

st.markdown(f'<div class="szyna-din">{html_szyna}</div>', unsafe_allow_html=True)

# PODSUMOWANIE
st.divider()
total_m = sum(u.moduly for u in st.session_state.get('szyna', []))
c1, c2 = st.columns(2)
c1.metric("Suma modułów", f"{total_m} DIN")
c2.metric("Szerokość w obudowie", f"{total_m * 17.5} mm")
