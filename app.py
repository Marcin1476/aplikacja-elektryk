import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy", layout="wide")

# --- CUSTOM CSS (Wygląd Aparatów) ---
st.markdown("""
    <style>
    .szyna-din {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        overflow-x: auto;
        padding: 20px;
        background-color: #e0e0e0;
        border-radius: 5px;
        border-top: 15px solid #bdc3c7;
        border-bottom: 15px solid #bdc3c7;
        min-height: 350px;
    }
    .aparat {
        background-color: #ffffff;
        border: 2px solid #333;
        border-radius: 4px;
        margin-right: 2px;
        padding: 10px 5px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .aparat-naglowek {
        font-weight: bold;
        font-size: 12px;
        border-bottom: 1px solid #ccc;
        margin-bottom: 10px;
        background: #f0f0f0;
    }
    .aparat-prad {
        font-size: 18px;
        font-weight: bold;
        color: #d35400;
    }
    .aparat-char {
        font-size: 14px;
        color: #2c3e50;
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

# --- BIBLIOTEKA (W SIDEBARZE) ---
st.sidebar.header("🛠️ Panel Konfiguracyjny")

biblioteka = [
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 10, 1, "#3498db"),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 16, 1, "#3498db"),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", 20, 1, "#2980b9"),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", 25, 3, "#e67e22"),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", 32, 3, "#d35400"),
    Urzadzenie("Różnicówka 4P", "RCCB", 40, 4, "#27ae60"),
    Urzadzenie("Ochronnik przepięć", "T1+T2", "SPD", 4, "#c0392b"),
]

opcje_tekstowe = [f"{u.nazwa} ({u.charakterystyka}{u.prad})" for u in biblioteka]
wybor_nazwa = st.sidebar.selectbox("Wybierz aparat:", opcje_tekstowe)

if st.sidebar.button("Dodaj do szyny ➡️"):
    wybrany = biblioteka[opcje_tekstowe.index(wybor_nazwa)]
    st.session_state.szyna.append(wybrany)
    st.toast(f"Dodano {wybrany.nazwa}")

if st.sidebar.button("Usuń ostatni ⬅️"):
    if st.session_state.szyna:
        st.session_state.szyna.pop()
        st.rerun()

if st.sidebar.button("Wyczyść rozdzielnicę 🗑️"):
    st.session_state.szyna = []
    st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title("⚡ Wirtualna Szyna DIN")
st.write("Aparaty montowane od lewej do prawej:")

# Generowanie HTML dla szyny
html_szyny = '<div class="szyna-din">'

for u in st.session_state.szyna:
    # Szerokość modułu: 1 moduł = ok. 40px
    szerokosc = u.moduly * 45
    html_szyny += f"""
    <div class="aparat" style="width: {szerokosc}px; border-top: 10px solid {u.kolor};">
        <div class="aparat-naglowek">{u.nazwa}</div>
        <div class="aparat-char">{u.charakterystyka}</div>
        <div class="aparat-prad">{u.prad if u.prad != "SPD" else ""}</div>
        <div style="font-size: 10px; margin-top: auto;">{u.moduly} MOD</div>
    </div>
    """

html_szyny += '</div>'

st.markdown(html_szyny, unsafe_allow_html=True)

# Statystyki poniżej
st.markdown("---")
suma_mod = sum(u.moduly for u in st.session_state.szyna)
st.metric("Całkowita szerokość", f"{suma_mod} modułów")
