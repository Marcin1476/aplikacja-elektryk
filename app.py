import streamlit as st

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Wirtualna Rozdzielnica", layout="wide")

# --- STYLE CSS (opcjonalne, dla lepszego wyglądu) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .device-card { border: 2px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# --- MODELE DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly

    def __str__(self):
        return f"{self.charakterystyka}{self.prad}A | {self.nazwa}"

# --- INICJALIZACJA SESJI (Magazyn danych projektu) ---
if 'projekt_rozdzielnicy' not in st.session_state:
    st.session_state.projekt_rozdzielnicy = []

# --- BIBLIOTEKA URZĄDZEŃ (Fundament) ---
biblioteka = [
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 10, 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 16, 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", 20, 1),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", 25, 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", 32, 3),
    Urzadzenie("Wyłącznik Różnicowoprądowy 4P", "AC", 40, 4),
    Urzadzenie("Ogranicznik przepięć T1+T2", "Klasa", "B+C", 4),
]

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("⚡ Asystent Instalatora: Projektowanie Rozdzielnicy")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("🛠️ Dobór aparatury")
    
    # Wybór urządzenia
    opcje_tekstowe = [str(u) for u in biblioteka]
    wybor = st.selectbox("Wybierz urządzenie z biblioteki:", opcje_tekstowe)
    
    # Przycisk dodawania
    if st.button("Dodaj do szyny DIN"):
        indeks = opcje_tekstowe.index(wybor)
        wybrany_obiekt = biblioteka[indeks]
        st.session_state.projekt_rozdzielnicy.append(wybrany_obiekt)
        st.toast(f"Dodano {wybrany_obiekt.nazwa}!", icon="✅")

    if st.button("Wyczyść wszystko 🗑️"):
        st.session_state.projekt_rozdzielnicy = []
        st.rerun()

with col2:
    st.header("📋 Widok projektu")
    
    if not st.session_state.projekt_rozdzielnicy:
        st.info("Twoja rozdzielnica jest jeszcze pusta. Wybierz aparaty z lewej strony.")
    else:
        suma_modulow = 0
        for i, urz in enumerate(st.session_state.projekt_rozdzielnicy):
            with st.container():
                st.markdown(f"""
                <div class="device-card">
                    <strong>{i+1}. {urz.nazwa}</strong><br>
                    Charakterystyka: <code>{urz.charakterystyka}</code> | Prąd: <code>{urz.prad}A</code> | Szerokość: <code>{urz.moduly} mod.</code>
                </div>
                """, unsafe_allow_html=True)
                suma_modulow += urz.moduly
        
        st.markdown("---")
        st.metric("Całkowita zajętość miejsca", f"{suma_modulow} Modułów DIN")

# Stopka techniczna
st.sidebar.markdown("### ℹ️ Informacje o systemie")
st.sidebar.info("Aplikacja pozwala na wirtualny montaż zabezpieczeń na szynie DIN.")
