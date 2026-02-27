import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.4", layout="wide")

# --- INICJALIZACJA SESJI ---
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

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 50px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #888;
        border-bottom: 25px solid #888; min-height: 420px; gap: 4px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 320px; flex-shrink: 0;
    }
    .aparat-id { font-size: 10px; font-weight: bold; background: #222; color: #fff; padding: 2px; }
    .aparat-body { padding: 10px 4px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .aparat-header { font-size: 9px; font-weight: bold; color: #555; text-transform: uppercase; height: 30px; }
    
    /* STYL DLA WARTOŚCI PRĄDU */
    .aparat-specs { margin: 15px 0; }
    .char-text { font-size: 14px; font-weight: bold; color: #444; }
    .amp-text { font-size: 28px; font-weight: 900; color: #d35400; display: block; }
    
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 11px; min-height: 50px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 2px; }
    .aparat-footer { font-size: 10px; background: #ddd; padding: 4px; border-top: 1px solid #888; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka # np. B, C
        self.prad = prad                       # np. 16
        self.moduly = moduly
        self.opis = opis

# --- PANEL BOCZNY ---
st.sidebar.title("🛠️ Parametry Aparatu")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", "10", 1),
    Urzadzenie("Wyłącznik 1P", "B", "16", 1),
    Urzadzenie("Wyłącznik 1P", "C", "20", 1),
    Urzadzenie("Wyłącznik 3P", "B", "25", 3),
    Urzadzenie("Wyłącznik 3P", "C", "32", 3),
    Urzadzenie("Różnicówka 4P", "RCCB", "40", 4),
    Urzadzenie("Ochronnik T1+T2", "SPD", "T1+T2", 4),
]

opcje = [f"{u.nazwa} {u.charakterystyka}{u.prad}A" for u in biblioteka]
wybor = st.sidebar.selectbox("Wybierz z biblioteki:", opcje)
opis_uzytkownika = st.sidebar.text_input("Opis (etykieta):", "Obwód")

if st.sidebar.button("Montuj na szynie ⚡"):
    u_base = biblioteka[opcje.index(wybor)]
    nowy = Urzadzenie(u_base.nazwa, u_base.charakterystyka, u_base.prad, u_base.moduly, opis_uzytkownika)
    st.session_state['szyna'].append(nowy)
    st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# --- WIZUALIZACJA ---
st.title("⚡ Wirtualna Rozdzielnica")

lista_aparatow = st.session_state.get('szyna', [])
html_szyna = ""

for i, u in enumerate(lista_aparatow):
    szer = u.moduly * 55
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; background-color: {brand["bg"]};'
    
    # Budujemy HTML modułu z wyraźnym rozdzieleniem charakterystyki i Amperów
    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-header">{u.nazwa}</div>'
    
    # Sekcja parametrów technicznych
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
total_m = sum(u.moduly for u in lista_aparatow)
st.subheader(f"📊 Statystyki: {total_m} modułów | {total_m * 17.5} mm szerokości")
