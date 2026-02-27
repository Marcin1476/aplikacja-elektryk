import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka Pro v2.2", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- PARAMETRY ---
RZAD_MAX_MOD = 12 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}
DOBOR_PRZEWODU = {
    "6": "1.5 mm²", "10": "1.5 mm²", "13": "1.5 mm²",
    "16": "2.5 mm²", "20": "4.0 mm²", "25": "4.0 mm²",
    "32": "6.0 mm²", "40": "10.0 mm²", "63": "16.0 mm²"
}

# --- CSS (Wizualizacja) ---
st.markdown("""
    <style>
    .obudowa { background-color: #444; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 35px 15px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 18px solid #777; border-bottom: 18px solid #777;
        min-height: 380px; gap: 5px; margin-bottom: 30px;
    }
    .aparat {
        border: 2px solid #111; border-radius: 3px; text-align: center;
        box-shadow: 4px 4px 6px rgba(0,0,0,0.4); display: flex;
        flex-direction: column; min-height: 340px; flex-shrink: 0; background-color: white;
    }
    .aparat-faza { font-size: 14px; padding: 2px; font-weight: bold; }
    .amp-text { font-size: 30px; font-weight: 900; color: #e67e22; display: block; line-height: 1.1; }
    .aparat-label { border: 1px solid #ccc; background: #fff; font-size: 11px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 4px; font-weight: bold; color: #333; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 8px 2px; margin-top: auto; font-size: 12px; }
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
        self.przewod = DOBOR_PRZEWODU.get(prad, "wg projektu")

# --- BIBLIOTEKA ---
BIBLIOTEKA = [
    Urzadzenie("Rozłącznik Główny 3P", "FR", "100", 3, "L123"),
    Urzadzenie("Ochronnik T1+T2", "SPD", "B+C", 4, "L123"),
    Urzadzenie("Różnicówka 4P 30mA", "RCCB", "40", 4, "L123"),
    Urzadzenie("Różnicówka 2P 30mA", "RCCB", "25", 2, "L1"),
    Urzadzenie("Wyłącznik 1P", "B", "10", 1, "L1"),
    Urzadzenie("Wyłącznik 1P", "B", "16", 1, "L1"),
    Urzadzenie("Wyłącznik 3P", "B", "16", 3, "L123"),
]

# --- SIDEBAR ---
st.sidebar.title("🛠️ Kreator Projektu")
prod = st.sidebar.selectbox("Marka:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod]

opcje_tekst = [f"{u.charakterystyka}{u.prad} | {u.nazwa}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Dodaj aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])
etyk = st.sidebar.text_input("Nazwa obwodu:", "Gniazda")
faz = st.sidebar.radio("Zasilanie:", ["L1", "L2", "L3"]) if BIBLIOTEKA[idx].moduly < 3 else "L123"

if st.sidebar.button("Dodaj do szafy ➡️"):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b.nazwa, b.charakterystyka, b.prad, b.moduly, faz, etyk))
    st.rerun()

if st.sidebar.button("Resetuj 🗑️"):
    st.session_state['szyna'] = []; st.rerun()

# --- LOGIKA PODZIAŁU NA RZĘDY ---
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    if akt_mod + u.moduly > RZAD_MAX_MOD:
        rzedy.append([u])
        akt_mod = u.moduly
    else:
        rzedy[-1].append(u)
        akt_mod += u.moduly

# --- WIZUALIZACJA ---
st.title("⚡ Projekt Rozdzielnicy")
st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if not rzad and r_i == 0:
        st.info("Dodaj urządzenia, aby zobaczyć wizualizację.")
        break
    st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
    html = '<div class="szyna-din">'
    for i, u in enumerate(rzad):
        ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u.faza, "➖")
        html += f"""
        <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {brand_color};">
            <div style="font-size:10px; font-weight:bold; background:#222; color:#fff; padding:2px;">R{r_i+1}-A{i+1}</div>
            <div class="aparat-faza">{ico} {u.faza}</div>
            <div class="aparat-body">
                <div class="aparat-header">{u.nazwa}</div>
                <div style="margin:10px 0;"><span style="font-size:14px; font-weight:bold;">{u.charakterystyka}</span><span class="amp-text">{u.prad}A</span></div>
                <div class="aparat-label">{u.opis}</div>
            </div>
            <div class="aparat-footer">{"■"*u.moduly}<br>{u.moduly} MOD</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SPECYFIKACJA PODZIELONA NA RZĘDY ---
st.divider()
if st.session_state['szyna']:
    st.subheader("📋 Specyfikacja techniczna (podział na szyny)")
    
    # Przechodzimy przez rzędy, aby stworzyć eleganckie zestawienie
    for r_idx, rzad in enumerate(rzedy):
        if rzad:
            st.write(f"**Szyna DIN nr {r_idx + 1}**")
            dane_rzedu = [{
                "Nr": f"A{i+1}",
                "Aparat": u.nazwa,
                "Zabezpieczenie": f"{u.charakterystyka}{u.prad}A",
                "Faza": u.faza,
                "Przewód": u.przewod,
                "Przeznaczenie": u.opis
            } for i, u in enumerate(rzad)]
            
            st.table(pd.DataFrame(dane_rzedu))
            
            suma_m = sum(u.moduly for u in rzad)
            st.caption(f"Zajętość na szynie: {suma_m}/{RZAD_MAX_MOD} modułów")
else:
    st.info("Specyfikacja pojawi się po dodaniu aparatów.")
