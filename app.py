import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy", layout="wide")

# --- POPRAWIONY CUSTOM CSS ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex;
        flex-direction: row;
        align-items: stretch; /* Rozciąga aparaty do tej samej wysokości */
        overflow-x: auto;
        padding: 30px 20px;
        background-color: #d1d1d1;
        border-radius: 8px;
        border-top: 20px solid #a0a0a0;
        border-bottom: 20px solid #a0a0a0;
        min-height: 300px;
        gap: 2px; /* Odstęp między aparatami */
    }
    .aparat {
        background-color: #ffffff;
        border: 2px solid #444;
        border-radius: 4px;
        padding: 15px 5px;
        text-align: center;
        box-shadow: 3px 0px 5px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        min-height: 220px;
    }
    .aparat-naglowek {
        font-weight: bold;
        font-size: 10px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #eee;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    .aparat-char {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
    }
    .aparat-prad {
        font-size: 24px;
        font-weight: 900;
        color: #d35400;
        margin-bottom: 10px;
    }
    .aparat-footer {
        margin-top: auto;
        font-size: 10px;
        font-weight: bold;
        color: #7f8c8d;
        border-top: 1px solid #eee;
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

# --- PANEL BOCZNY (Sidebar) ---
st.sidebar.header("🛠️ Panel Instalatora")

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", 10, 1, "#3498db"),
    Urzadzenie("Wyłącznik 1P", "B", 16, 1, "#3498db"),
    Urzadzenie("Wyłącznik 1P", "C", 20, 1, "#2980b9"),
    Urzadzenie("Wyłącznik 3P", "B", 25, 3, "#e67e22"),
    Urzadzenie("Wyłącznik 3P", "C", 32, 3, "#d35400"),
    Urzadzenie("Różnicówka 4P", "RCCB", 40, 4, "#27ae60"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "", 4, "#c0392b"),
]

opcje_tekstowe = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in biblioteka]
wybor_nazwa = st.sidebar.selectbox("Wybierz aparat do montażu:", opcje_tekstowe)

if st.sidebar.button("Dodaj do szyny ➡️"):
    wybrany = biblioteka[opcje_tekstowe.index(wybor_nazwa)]
    st.session_state.szyna.append(wybrany)
    st.rerun()

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state.szyna:
        st.session_state.szyna.pop()
        st.rerun()

if st.sidebar.button("Wyczyść projekt 🗑️"):
    st.session_state.szyna = []
    st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title("⚡ Wirtualna Rozdzielnica")
st.info("Aparaty montowane na szynie DIN (widok od lewej do prawej)")

# START KONTENERA SZYNY (poza pętlą!)
html_output = '<div class="szyna-din">'

# PĘTLA GENERUJĄCA APARATY
for u in st.session_state.szyna:
    szerokosc = u.moduly * 45  # 1 moduł = 45px
    html_output += f"""
    <div class="aparat" style="width: {szerokosc}px; border-top: 12px solid {u.kolor};">
        <div class="aparat-naglowek">{u.nazwa}</div>
        <div class="aparat-char">{u.charakterystyka}</div>
        <div class="aparat-prad">{u.prad}</div>
        <div class="aparat-footer">{u.moduly} MOD</div>
    </div>
    """

# KONIEC KONTENERA SZYNY (poza pętlą!)
html_output += '</div>'

# WYŚWIETLENIE GOTOWEGO HTML
st.markdown(html_output, unsafe_allow_html=True)

# STATYSTYKI
st.markdown("---")
suma_mod = sum(u.moduly for u in st.session_state.szyna)
c1, c2, c3 = st.columns(3)
c1.metric("Suma modułów", f"{suma_mod} / 12")
c2.metric("Szerokość mm", f"{suma_mod * 17.5} mm")
c3.write("Status: Fundamenty poprawne ✅")
