import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka v1.0", layout="wide")

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
        min-height: 320px;
        gap: 2px;
    }
    .aparat {
        background-color: #ffffff;
        border: 2px solid #444;
        border-radius: 4px;
        padding: 10px 2px;
        text-align: center;
        box-shadow: 3px 0px 5px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        min-height: 240px;
        flex-shrink: 0;
    }
    .aparat-naglowek {
        font-weight: bold;
        font-size: 9px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #eee;
        margin-bottom: 10px;
        text-transform: uppercase;
        overflow: hidden;
    }
    .aparat-char {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
    }
    .aparat-prad {
        font-size: 22px;
        font-weight: 900;
        color: #d35400;
    }
    .aparat-footer {
        margin-top: auto;
        font-size: 9px;
        font-weight: bold;
        color: #95a5a6;
        padding-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MODELE DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, kolor="#3498db"):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.kolor = kolor

# --- INICJALIZACJA SESJI ---
if 'szyna' not in st.session_state:
    st.session_state.szyna = []

# --- PANEL BOCZNY ---
st.sidebar.header("🛠️ Panel Konfiguracyjny")

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", 10, 1, "#3498db"),
    Urzadzenie("Wyłącznik 1P", "B", 16, 1, "#3498db"),
    Urzadzenie("Wyłącznik 1P", "C", 20, 1, "#2980b9"),
    Urzadzenie("Wyłącznik 3P", "B", 25, 3, "#e67e22"),
    Urzadzenie("Wyłącznik 3P", "C", 32, 3, "#d35400"),
    Urzadzenie("Różnicówka 4P", "RCCB", 40, 4, "#27ae60"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "ABC", 4, "#c0392b"),
]

opcje_tekstowe = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in biblioteka]
wybor_nazwa = st.sidebar.selectbox("Wybierz aparat:", opcje_tekstowe)

if st.sidebar.button("Dodaj do szyny ➡️"):
    indeks = opcje_tekstowe.index(wybor_nazwa)
    wybrany = biblioteka[indeks]
    st.session_state.szyna.append(wybrany)
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Cofnij (Usuń ostatni)"):
    if st.session_state.szyna:
        st.session_state.szyna.pop()
        st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state.szyna = []
    st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title("⚡ Wirtualny Montaż Rozdzielnicy")

html_items = ""
for u in st.session_state.szyna:
    szerokosc = u.moduly * 45
    html_items += (
        f'<div class="aparat" style="width: {szerokosc}px; border-top: 12px solid {u.kolor};">'
        f'<div class="aparat-naglowek">{u.nazwa}</div>'
        f'<div class="aparat-char">{u.charakterystyka}</div>'
        f'<div class="aparat-prad">{u.prad}</div>'
        f'<div class="aparat-footer">{u.moduly} MOD</div>'
        f'</div>'
    )

st.markdown(f'<div class="szyna-din">{html_items}</div>', unsafe_allow_html=True)

# --- STATYSTYKI ---
st.markdown("---")
suma_mod = sum(u.moduly for u in st.session_state.szyna)
cols = st.columns(3)
cols[0].metric("Zajęte moduły", f"{suma_mod} DIN")
cols[1].metric("Szerokość szyny", f"{suma_mod * 17.5} mm")
cols[2].
