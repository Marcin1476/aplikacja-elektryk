import streamlit as st

# 1. KONFIGURACJA STRONY (Zawsze na samym początku)
st.set_page_config(page_title="Projektant Rozdzielnicy v1.3", layout="wide")

# 2. INICJALIZACJA SESJI (Zabezpieczenie przed AttributeError)
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# 3. DEFINICJA PRODUCENTÓW
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f8f9fa"},
    "Legrand": {"primary": "#E20613", "bg": "#fffafa"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f2fff5"},
    "Hager": {"primary": "#00305d", "bg": "#f0f4f7"},
    "Standard": {"primary": "#333", "bg": "#ffffff"}
}

# 4. CUSTOM CSS
st.markdown("""
    <style>
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 50px 20px; background-color: #c0c0c0;
        border-radius: 8px; border-top: 25px solid #a0a0a0;
        border-bottom: 25px solid #a0a0a0; min-height: 400px; gap: 4px;
    }
    .aparat {
        border: 2px solid #555; border-radius: 4px; text-align: center;
        box-shadow: 5px 5px 10px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 300px; flex-shrink: 0;
    }
    .aparat-id { font-size: 11px; font-weight: bold; background: #222; color: #fff; padding: 3px; }
    .aparat-body { padding: 10px 5px; flex-grow: 1; display: flex; flex-direction: column; }
    .aparat-name { font-size: 10px; font-weight: bold; height: 35px; color: #444; }
    .aparat-value { font-size: 24px; font-weight: 900; margin: 10px 0; }
    .aparat-char { font-size: 16px; font-weight: bold; }
    .aparat-label { border: 1px solid #ccc; background: white; font-size: 11px; min-height: 50px; display: flex; align-items: center; justify-content: center; margin: 5px; }
    .aparat-footer { font-size: 10px; background: #ddd; padding: 3px; border-top: 1px solid #999; }
    </style>
    """, unsafe_allow_html=True)

# 5. MODELE DANYCH
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, extra="", opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.extra = extra
        self.opis = opis

# 6. PANEL BOCZNY
st.sidebar.title("🛠️ Konfiguracja")
producent_key = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", "10A", 1),
    Urzadzenie("Wyłącznik 1P", "B", "16A", 1),
    Urzadzenie("Wyłącznik 1P", "C", "20A", 1),
    Urzadzenie("Wyłącznik 3P", "B", "25A", 3),
    Urzadzenie("Wyłącznik 3P", "C", "32A", 3),
    Urzadzenie("Różnicówka 4P", "RCCB", "40A", 4, "30mA"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "T1+T2", 4),
]

opcje = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in biblioteka]
wybor = st.sidebar.selectbox("Wybierz aparat:", opcje)
etykieta = st.sidebar.text_input("Opis obwodu:", "Obwód")

if st.sidebar.button("Montuj ⚡"):
    u_base = biblioteka[opcje.index(wybor)]
    nowy = Urzadzenie(u_base.nazwa, u_base.charakterystyka, u_base.prad, u_base.moduly, u_base.extra, etykieta)
    st.session_state['szyna'].append(nowy)
    st.rerun()

if st.sidebar.button("Wyczyść 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# 7. WIZUALIZACJA GŁÓWNA
st.title("💡 Wirtualna Rozdzielnica")

# Bezpieczne pobranie listy z sesji
lista_aparatow = st.session_state.get('szyna', [])

html_szyna = ""
for i, u in enumerate(lista_aparatow):
    szer = u.moduly * 55
    style = f'width:{szer}px; border-top: 15px solid {brand["primary"]}; background-color: {brand["bg"]};'
    
    html_szyna += f'<div class="aparat" style="{style}">'
    html_szyna += f'<div class="aparat-id">F{i+1}</div>'
    html_szyna += f'<div class="aparat-body">'
    html_szyna += f'<div class="aparat-name">{u.nazwa}</div>'
    html_szyna += f'<div class="aparat-value"><span class="aparat-char">{u.charakterystyka}</span>{u.prad}</div>'
    html_szyna += f'<div class="aparat-label">{u.opis}</div>'
    html_szyna += f'</div>'
    html_szyna += f'<div class="aparat-footer">{u.moduly} MOD</div>'
    html_szyna += f'</div>'

st.markdown(f'<div class="szyna-din">{html_szyna}</div>', unsafe_allow_html=True)

# 8. PODSUMOWANIE
st.divider()
total_m = sum(u.moduly for u in lista_aparatow)
st.subheader(f"Zajętość: {total_m} modułów")
