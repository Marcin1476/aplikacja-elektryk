import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Projektant Rozdzielnicy v1.2", layout="wide")

# --- DEFINICJA PRODUCENTÓW ---
PRODUCENCI = {
    "Eaton": {"primary": "#005EB8", "bg": "#f0f4f8", "text": "#000000"},
    "Legrand": {"primary": "#E20613", "bg": "#f9f1f1", "text": "#000000"},
    "Schneider": {"primary": "#3dcd58", "bg": "#f1f9f2", "text": "#000000"},
    "Hager": {"primary": "#00305d", "bg": "#f0f2f5", "text": "#000000"},
    "Standard": {"primary": "#34495e", "bg": "#ffffff", "text": "#000000"}
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
        min-height: 380px;
        gap: 3px;
    }
    .aparat {
        border: 2px solid #444;
        border-radius: 4px;
        padding: 5px;
        text-align: center;
        box-shadow: 3px 0px 5px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        min-height: 280px;
        flex-shrink: 0;
    }
    .aparat-id {
        font-size: 10px;
        font-weight: bold;
        background: #333;
        color: white;
        padding: 2px;
        border-radius: 2px;
        margin-bottom: 5px;
    }
    .aparat-naglowek {
        font-weight: bold;
        font-size: 9px;
        height: 30px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .aparat-parametry {
        margin: 10px 0;
    }
    .aparat-char {
        font-size: 14px;
        font-weight: bold;
    }
    .aparat-prad {
        font-size: 24px;
        font-weight: 900;
    }
    .aparat-opis-box {
        border: 1px dashed #999;
        background: #fff;
        font-size: 10px;
        padding: 5px 2px;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 10px 0;
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
st.sidebar.header("⚙️ Konfiguracja")
producent_key = st.sidebar.selectbox("Marka aparatury:", list(PRODUCENCI.keys()))
brand = PRODUCENCI[producent_key]

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Nowy Aparat")

biblioteka = [
    Urzadzenie("Wyłącznik 1P", "B", 10, 1),
    Urzadzenie("Wyłącznik 1P", "B", 16, 1),
    Urzadzenie("Wyłącznik 1P", "C", 20, 1),
    Urzadzenie("Wyłącznik 3P", "B", 25, 3),
    Urzadzenie("Wyłącznik 3P", "C", 32, 3),
    Urzadzenie("Różnicówka 4P", "RCCB", 40, 4),
    Urzadzenie("Ochronnik T1+T2", "SPD", "", 4),
]

opcje_tekstowe = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in biblioteka]
wybor_nazwa = st.sidebar.selectbox("Typ urządzenia:", opcje_tekstowe)
opis_obwodu = st.sidebar.text_input("Etykieta (np. Oświetlenie Góra):", "")

if st.sidebar.button("Dodaj do projektu ➡️"):
    idx = opcje_tekstowe.index(wybor_nazwa)
    szablon = biblioteka[idx]
    nowe_urz = Urzadzenie(szablon.nazwa, szablon.charakterystyka, szablon.prad, szablon.moduly, opis_obwodu)
    st.session_state.szyna.append(nowe_urz)
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Usuń ostatni"):
    if st.session_state.szyna:
        st.session_state.szyna.pop(); st.rerun()

if st.sidebar.button("Wyczyść wszystko 🗑️"):
    st.session_state.szyna = []; st.rerun()

# --- WIZUALIZACJA GŁÓWNA ---
st.title("⚡ Wirtualna Szyna Montażowa")



html_items = ""
for i, u in enumerate(st.session_state.szyna):
    szerokosc = u.moduly * 50 # Nieco szerzej dla czytelności
    
    style_aparat = (
        f'width: {szerokosc}px; '
        f'border-top: 12px solid {brand["primary"]}; '
        f'background-color: {brand["bg"]};'
    )
    
    # Budowanie HTML pojedynczego modułu
    html_items += f"""
    <div class="aparat" style="{style_aparat}">
        <div class="aparat-id">S{i+1}</div>
        <div class="aparat-naglowek">{u.nazwa}</div>
        <div class="aparat-parametry">
            <span class="aparat-char" style="color: {brand["primary"]};">{u.charakterystyka}</span>
            <div class="aparat-prad">{u.prad}</div>
        </div>
        <div class="aparat-opis-box">
            {u.opis if u.opis else "---"}
        </div>
        <div class="aparat-footer">{u.moduly} MOD</div>
    </div>
    """

st.markdown(f'<div class="szyna-din">{html_items}</div>', unsafe_allow_html=True)

# --- PODSUMOWANIE ---
st.markdown("---")
suma_mod = sum(u.moduly for u in st.session_state.szyna)
c1, c2, c3 = st.columns(3)
c1.metric("Suma modułów", f"{suma_mod}")
c2.metric("Szerokość szyny", f"{suma_mod * 17.5} mm")
c3.info(f"Producent: {producent_key} | Standard szyny: DIN 35mm")
