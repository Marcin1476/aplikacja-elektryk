import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka Pro v1.1", layout="wide")

# --- DEFINICJA PRODUCENTÓW ---
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f0f4f8"},
    "Legrand": {"primary": "#E20613", "bg": "#f9f1f1"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f1f9f2"},
    "Hager": {"primary": "#00305d", "bg": "#f0f2f5"},
    "Standard": {"primary": "#34495e", "bg": "#ffffff"}
}

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        overflow-x: auto;
        padding: 40px 20px;
        background-color: #d1d1d1;
        border-radius: 8px;
        border-top: 20px solid #a0a0a0;
        border-bottom: 20px solid #a0a0a0;
        min-height: 350px;
        gap: 3px;
    }
    .aparat {
        border: 2px solid #444;
        border-radius: 4px;
        padding: 10px 2px;
        text-align: center;
        box-shadow: 3px 0px 5px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        min-height: 260px;
        flex-shrink: 0;
    }
    .aparat-naglowek {
        font-weight: bold;
        font-size: 9px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #ddd;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .aparat-char {
        font-size: 16px;
        font-weight: bold;
    }
    .aparat-prad {
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    .aparat-opis {
        font-size: 10px;
        color: #555;
        font-style: italic;
        background: rgba(255,255,255,0.5);
        margin: 5px;
        border-radius: 3px;
    }
    .aparat-footer {
        margin-top: auto;
        font-size: 9px;
        font-weight: bold;
        padding-top: 5px;
        border-top: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MODELE DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.opis = opis

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state.szyna = []

# --- PANEL BOCZNY ---
st.sidebar.header("⚙️ Konfiguracja Rozdzielnicy")

# Wybór Producenta
producent_key = st.sidebar.selectbox("Wybierz markę aparatury:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Dodaj Aparat")

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", 10, 1),
    Urzadzenie("Wyłącznik 1P", "B", 16, 1),
    Urzadzenie("Wyłącznik 1P", "C", 20, 1),
    Urzadzenie("Wyłącznik 3P", "B", 25, 3),
    Urzadzenie("Wyłącznik 3P", "C", 32, 3),
    Urzadzenie("Różnicówka 4P", "RCCB", 40, 4),
    Urzadzenie("Ochronnik T1+T2", "SPD", "ABC", 4),
]

opcje_tekstowe = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in biblioteka]
wybor_nazwa = st.sidebar.selectbox("Typ urządzenia:", opcje_tekstowe)
opis_obwodu = st.sidebar.text_input("Nazwa obwodu (np. Salon Gniazda):", "")

if st.sidebar.button("Montuj na szynie ➡️"):
    indeks = opcje_tekstowe.index(wybor_nazwa)
    szablon = biblioteka[indeks]
    # Tworzymy kopię urządzenia z własnym opisem
    nowe_urzadzenie = Urzadzenie(szablon.nazwa, szablon.charakterystyka, szablon.prad, szablon.moduly, opis_obwodu)
    st.session_state.szyna.append(nowe_urzadzenie)
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Cofnij ostatni"):
    if st.session_state.szyna:
        st.session_state.szyna.pop()
        st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state.szyna = []
    st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title(f"⚡ Projekt: Rozdzielnica ({producent_key})")

html_items = ""
for u in st.session_state.szyna:
    szerokosc = u.moduly * 45
    # Dynamiczne style oparte na producentu
    style_aparat = (
        f'width: {szerokosc}px; '
        f'border-top: 12px solid {brand["primary"]}; '
        f'background-color: {brand["bg"]};'
    )
    
    html_items += (
        f'<div class="aparat" style="{style_aparat}">'
        f'<div class="aparat-naglowek">{u.nazwa}</div>'
        f'<div class="aparat-char" style="color: {brand["primary"]};">{u.charakterystyka}</div>'
        f'<div class="aparat-prad">{u.prad}</div>'
        f'<div class="aparat-opis">{u.opis}</div>'
        f'<div class="aparat-footer">{u.moduly} MOD</div>'
        f'</div>'
    )

st.markdown(f'<div class="szyna-din">{html_items}</div>', unsafe_allow_html=True)

# --- STATYSTYKI ---
st.markdown("---")
suma_mod = sum(u.moduly for u in st.session_state.szyna)
c1, c2, c3 = st.columns(3)
c1.metric("Zajęte moduły", f"{suma_mod} DIN")
c2.metric("Szerokość szyny", f"{suma_mod * 17.5} mm")
c3.info(f"Wybrany system: {producent_key}")
