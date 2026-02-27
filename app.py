import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.3", layout="wide")

# --- DEFINICJA PRODUCENTÓW ---
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f8f9fa", "accent": "#005EB8"},
    "Legrand": {"primary": "#E20613", "bg": "#fffafa", "accent": "#E20613"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f2fff5", "accent": "#27ae60"},
    "Hager": {"primary": "#00305d", "bg": "#f0f4f7", "accent": "#00305d"},
    "Standard": {"primary": "#333", "bg": "#ffffff", "accent": "#555"}
}

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        overflow-x: auto;
        padding: 50px 20px;
        background-color: #c0c0c0;
        border-radius: 8px;
        border-top: 25px solid #a0a0a0;
        border-bottom: 25px solid #a0a0a0;
        min-height: 400px;
        gap: 4px;
        box-shadow: inset 0 10px 20px rgba(0,0,0,0.2);
    }
    .aparat {
        border: 2px solid #555;
        border-radius: 4px;
        text-align: center;
        box-shadow: 5px 5px 10px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        min-height: 300px;
        flex-shrink: 0;
        position: relative;
    }
    .aparat-id {
        font-size: 11px;
        font-weight: bold;
        background: #222;
        color: #fff;
        padding: 3px;
        text-transform: uppercase;
    }
    .aparat-body {
        padding: 10px 5px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-around;
    }
    .aparat-name {
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        color: #444;
        height: 30px;
    }
    .aparat-value {
        font-size: 26px;
        font-weight: 900;
        line-height: 1;
        margin: 10px 0;
    }
    .aparat-char {
        font-size: 16px;
        font-weight: bold;
        display: block;
    }
    .aparat-extra {
        font-size: 12px;
        font-weight: bold;
        background: #eee;
        border-radius: 3px;
        padding: 2px;
    }
    .aparat-label {
        border: 1px solid #ccc;
        background: white;
        font-size: 11px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 5px;
        font-family: 'Courier New', Courier, monospace;
    }
    .aparat-footer {
        font-size: 10px;
        background: #ddd;
        padding: 3px;
        border-top: 1px solid #999;
    }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, extra="", opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.extra = extra # np. "30mA"
        self.opis = opis

if 'szyna' not in st.session_state:
    st.session_state.szyna = []

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Skonfiguruj Aparat")
producent = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent]

# Rozszerzona biblioteka
biblioteka = [
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "10A", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", "16A", 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", "20A", 1),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", "25A", 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", "32A", 3),
    Urzadzenie("Różnicówka 4P 30mA", "RCCB", "40A", 4, "IΔn 0.03A"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "T1+T2", 4, "Uc 275V"),
]

opcje = [f"{u.nazwa} {u.charakterystyka} {u.prad}" for u in biblioteka]
wybor = st.sidebar.selectbox("Wybierz typ:", opcje)
etykieta = st.sidebar.text_input("Opis obwodu:", "Obwód wolny")

if st.sidebar.button("Montuj Aparat ⚡"):
    u_base = biblioteka[opcje.index(wybor)]
    nowy = Urzadzenie(u_base.nazwa, u_base.charakterystyka, u_base.prad, u_base.moduly, u_base.extra, etykieta)
    st.session_state.szyna.append(nowy)
    st.rerun()

if st.sidebar.button("Wyczyść Szynę 🗑️"):
    st.session_state.szyna = []
    st.rerun()

# --- GŁÓWNA WIZUALIZACJA ---
st.title("💡 Wirtualny Montaż Rozdzielnicy")

html_szyna = ""
for i, u in enumerate(st.session_state.szyna):
    szer = u.moduly * 55
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; background-color: {brand["bg"]};'
    
    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-name">{u.nazwa}</div>'
    html_szyna += f'<div class="aparat-value"><span class="aparat-char">{u.charakterystyka}</span>{u.prad}</div>'
    if u.extra:
        html_szyna += f'<div class="aparat-extra">{u.extra}</div>'
    html_szyna += f'<div class="aparat-label">{u.opis}</div>'
    html_szyna += f'</div>'
    html_szyna += f'<div class="aparat-footer">{u.moduly} MOD</div>'
