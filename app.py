import streamlit as st

# --- MODELE DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly

    def __str__(self):
        return f"[{self.charakterystyka}{self.prad}A] {self.nazwa} - {self.moduly} mod."

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka", layout="wide")
st.title("⚡ Wirtualna Rozdzielnica")
st.subheader("Fundamenty systemu montażowego")

# --- INICJALIZACJA SESJI (Baza danych w pamięci przeglądarki) ---
if 'projekt' not in st.session_state:
    st.session_state.projekt = []

# --- BIBLIOTEKA URZĄDZEŃ ---
# Tutaj definiujemy Twoją bazę aparatury
biblioteka = [
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 6, 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 10, 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "B", 16, 1),
    Urzadzenie("Wyłącznik nadprądowy 1P", "C", 20, 1),
    Urzadzenie("Wyłącznik nadprądowy 3P", "B", 25, 3),
    Urzadzenie("Wyłącznik nadprądowy 3P", "C", 32, 3),
    Urzadzenie("Różnicówka 4P (RCCB)", "AC", 40, 4),
    Urzadzenie("Ochronnik przepięć T1+T2", "Klasa", "B+C", 4),
]

# --- INTERFEJS UŻYTKOWNIKA ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📦 Biblioteka")
    # Wybór urządzenia z listy
    opcje = [str(u) for u in biblioteka]
    wybrane_z_listy = st.selectbox("Wybierz aparat do montażu:", opcje)
    
    # Przycisk dodawania
    if st.button("Dodaj do rozdzielnicy ➕"):
        indeks = opcje.index(wybrane_z_listy)
        obiekt_do_dodania = biblioteka[indeks]
        st.session_state.projekt.append(obiekt_do_dodania)
        st.success(f"Dodano: {obiekt_do_dodania.nazwa}")

    if st.button("Wyczyść projekt 🗑️"):
        st.session_state.projekt = []
        st.rerun()

with col2:
    st.header("🖼️ Widok Rozdzielnicy")
    if not st.session_state.projekt:
        st.info("Rozdzielnica jest pusta. Dodaj pierwsze urządzenia z lewego panelu.")
    else:
        total_moduly = 0
        for i, u in enumerate(st.session_state.projekt):
            # Wizualizacja urządzenia jako "kafelek"
            with st.container():
                st.markdown(f"""
                <div style="border: 2px solid #4CAF50; border-radius: 5px; padding: 10px; margin: 5px; background-color: #f0f2f6;">
                    <strong>{i+1}. {u.nazwa}</strong><br>
                    Charakterystyka: {u.charakterystyka} | Prąd: {u.prad}A | Szerokość: {u.moduly} mod.
                </div>
                """, unsafe_allow_html=True)
                total_moduly += u.moduly
        
        st.divider()
        st.metric("Suma zajętych modułów", f"{total_moduly} DIN")

# --- STOPKA ---
st.sidebar.markdown("---")
st.sidebar.write("💻 **Status projektu:** Fundamenty (v1.0)")
st.sidebar.write("👨‍🔧 **Dla kogo:** Instalatorzy elektryczni")
