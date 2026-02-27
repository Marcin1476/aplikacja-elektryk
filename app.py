import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka Pro v2.0", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- PARAMETRY TECHNICZNE ---
RZAD_MAX_MOD = 12  # Standardowa szerokość rzędu

DOBOR_PRZEWODU = {
    "6": "1.5 mm²", "10": "1.5 mm²", "13": "1.5 mm²",
    "16": "2.5 mm²", "20": "4.0 mm²", "25": "4.0 mm²",
    "32": "6.0 mm²", "40": "10.0 mm²", "63": "16.0 mm²",
    "SPD": "16.0 mm²", "RCCB": "Zależnie od zasilania"
}

PRODUCENCI = {
    "Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"
}

# --- CSS (Wielorzędowość) ---
st.markdown("""
    <style>
    .obudowa { background-color: #333; padding: 20px; border-radius: 10px; border: 5px solid #555; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 30px 15px; background-color: #c0c0c0;
        border-radius: 4px; border-top: 15px solid #888; border-bottom: 15px solid #888;
        min-height: 380px; gap: 4px; margin-bottom: 20px;
    }
    .aparat {
        border: 2px solid #333; border-radius: 4px; text-align: center;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.3); display: flex;
        flex-direction: column; min-height: 320px; flex-shrink: 0; background-color: white;
    }
    .aparat-id { font-size: 10px; font-weight: bold; background: #222; color: #fff; padding: 2px; }
    .aparat-faza { font-size: 12px; margin: 2px 0; }
    .amp-text { font-size: 28px; font-weight: 900; color: #d35400; display: block; }
    .aparat-label { border: 1px solid #bbb; background: #fff; font-size: 11px; min-height: 50px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 4px; font-weight: bold; }
    .aparat-footer { background: #2c3e50; color: #f1c40f; padding: 5px 2px; margin-top: auto; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis
        # Dobór przewodu
        self.przewod = DOBOR_PRZEWODU.get(prad, "Do dobrania")

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    Urzadzenie("Rozłącznik 3P", "FR", "100", 3, "L123"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "B+C", 4, "L123"),
    Urzadzenie("Różnicówka 4P", "RCCB", "40", 4, "L123"),
    Urzadzenie("Różnicówka 2P", "RCCB", "25", 2, "L1"),
    Urzadzenie("Wyłącznik 1P", "B", "10", 1, "L1"),
    Urzadzenie("Wyłącznik 1P", "B", "16", 1, "L1"),
    Urzadzenie("Wyłącznik 1P", "C", "20", 1, "L1"),
    Urzadzenie("Wyłącznik 3P", "B", "16", 3, "L123"),
]

# --- SIDEBAR ---
st.sidebar.header("📦 Konfiguracja Projektu")
producent = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
kolor_marki = PRODUCENCI[producent]

opcje = [f"{u.charakterystyka}{u.prad} | {u.nazwa}" for u in BIBLIOTEKA]
wybor_idx = st.sidebar.selectbox("Dodaj aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje[x])
etykieta = st.sidebar.text_input("Nazwa obwodu:", "")
faza = st.sidebar.radio("Faza (dla 1P/2P):", ["L1", "L2", "L3"]) if BIBLIOTEKA[wybor_idx].moduly < 3 else "L123"

if st.sidebar.button("Dodaj do szafy ➡️"):
    base = BIBLIOTEKA[wybor_idx]
    st.session_state['szyna'].append(Urzadzenie(base.nazwa, base.charakterystyka, base.prad, base.moduly, faza, etykieta))
    st.rerun()

if st.sidebar.button("Wyczyść projekt 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- LOGIKA PODZIAŁU NA RZĘDY (Punkt 3) ---
rzedy = [[]]
aktualny_modul = 0

for u in st.session_state['szyna']:
    if aktualny_modul + u.moduly > RZAD_MAX_MOD:
        rzedy.append([u])
        aktualny_modul = u.moduly
    else:
        rzedy[-1].append(u)
        aktualny_modul += u.moduly

# --- WIZUALIZACJA ---
st.title("⚡ Profesjonalny Projekt Rozdzielnicy")
st.write(f"Szerokość szyny: **{RZAD_MAX_MOD} modułów**")



st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_idx, rzad in enumerate(rzedy):
    st.write(f"**SZYNIA DIN #{r_idx + 1}**")
    html_rzad = '<div class="szyna-din">'
    for i, u in enumerate(rzad):
        szer = u.moduly * 65
        f_ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u.faza, "➖")
        html_rzad += f"""
        <div class="aparat" style="width:{szer}px; border-top: 15px solid {kolor_marki};">
            <div class="aparat-id">R{r_idx+1}-A{i+1}</div>
            <div class="aparat-faza">{f_ico} {u.faza}</div>
            <div class="aparat-body">
                <div class="aparat-header">{u.nazwa}</div>
                <div class="aparat-specs">
                    <span style="font-size:14px; font-weight:bold;">{u.charakterystyka}</span>
                    <span class="amp-text">{u.prad}A</span>
                </div>
                <div class="aparat-label">{u.opis if u.opis else "WOLNE"}</div>
            </div>
            <div class="aparat-footer">{"■"*u.moduly}<br>{u.moduly} MOD</div>
        </div>"""
    html_rzad += '</div>'
    st.markdown(html_rzad, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- RAPORT I DOBÓR PRZEWODÓW (Punkt 1 i 2) ---
st.divider()
st.subheader("📋 Zestawienie Materiałowe i Techniczne")

if st.session_state['szyna']:
    dane_raportu = []
    for u in st.session_state['szyna']:
        dane_raportu.append({
            "Aparat": u.nazwa,
            "Typ": f"{u.charakterystyka}{u.prad}A",
            "Faza": u.faza,
            "Szerokość": f"{u.moduly} MOD",
            "Sugerowany Przewód": u.przewod,
            "Opis Obwodu": u.opis
        })
    
    df = pd.DataFrame(dane_raportu)
    st.table(df)
    
    # Podsumowanie zakupowe
    st.write("**Podsumowanie ilościowe:**")
    st.write(df['Aparat'].value_counts())
else:
    st.info("Dodaj urządzenia, aby wygenerować raport.")
