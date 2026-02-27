import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent Elektryka Fundament v2.4", layout="wide")

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

# --- CSS (Stylizacja Projektu) ---
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
        flex-direction: column; min-height: 350px; flex-shrink: 0; background-color: white;
    }
    .aparat-brand { font-size: 9px; font-weight: bold; color: #fff; padding: 2px 0; text-transform: uppercase; }
    .aparat-id { font-size: 10px; font-weight: bold; background: #222; color: #fff; padding: 2px; }
    .aparat-faza { font-size: 13px; font-weight: bold; margin-top: 5px; }
    .amp-text { font-size: 30px; font-weight: 900; color: #e67e22; display: block; line-height: 1.1; }
    .aparat-label { border: 1px solid #ccc; background: #fff; font-size: 11px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 5px; padding: 4px; font-weight: bold; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 8px 2px; margin-top: auto; font-size: 11px; }
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
    Urzadzenie("Wyłącznik 1P", "C", "20", 1, "L1"),
    Urzadzenie("Wyłącznik 3P", "B", "16", 3, "L123"),
    Urzadzenie("Wyłącznik 3P", "C", "25", 3, "L123"),
]

# --- SIDEBAR (Panel Sterowania) ---
st.sidebar.title("🛠️ Kreator Projektu")
wybrany_producent = st.sidebar.selectbox("Producent osprzętu:", list(PRODUCENCI.keys()))
kolor_brandu = PRODUCENCI[wybrany_producent]

st.sidebar.divider()
opcje_tekst = [f"{u.charakterystyka}{u.prad} | {u.nazwa}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Dodaj aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])
etyk = st.sidebar.text_input("Nazwa obwodu:", "Gniazda Salon")
faz = st.sidebar.radio("Zasilanie:", ["L1", "L2", "L3"]) if BIBLIOTEKA[idx].moduly < 3 else "L123"

c1, c2 = st.sidebar.columns(2)
if c1.button("Dodaj ➡️"):
    b = BIBLIOTEKA[idx]
    st.session_state['szyna'].append(Urzadzenie(b.nazwa, b.charakterystyka, b.prad, b.moduly, faz, etyk))
    st.rerun()

if c2.button("Usuń ostatni ⬅️"):
    if st.session_state['szyna']: st.session_state['szyna'].pop(); st.rerun()

if st.sidebar.button("Resetuj projekt 🗑️", use_container_width=True):
    st.session_state['szyna'] = []; st.rerun()

# --- ANALIZA BEZPIECZEŃSTWA (Smart Audit) ---
def wykonaj_audit():
    bledy = []
    ma_spd = any("SPD" in u.charakterystyka for u in st.session_state['szyna'])
    ma_fr = any("FR" in u.charakterystyka for u in st.session_state['szyna'])
    if not ma_fr: bledy.append("⚠️ Brak Rozłącznika Głównego!")
    if not ma_spd: bledy.append("⚠️ Brak Ochronnika Przepięć (SPD)!")
    return bledy

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
st.title("⚡ Projekt Rozdzielnicy - Tryb Smart")

# Wyświetlanie błędów audytu
audit_msg = wykonaj_audit()
if audit_msg and st.session_state['szyna']:
    for msg in audit_msg: st.error(msg)

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if not rzad and r_i == 0:
        st.info("Pusta rozdzielnica. Dodaj aparaty z panelu bocznego.")
        break
    st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
    html = '<div class="szyna-din">'
    for i, u in enumerate(rzad):
        ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u.faza, "➖")
        html += f"""
        <div class="aparat" style="width:{u.moduly*65}px; border-top: 15px solid {kolor_brandu};">
            <div class="aparat-brand" style="background-color:{kolor_brandu};">{wybrany_producent}</div>
            <div class="aparat-id">R{r_i+1}-A{i+1}</div>
            <div class="aparat-faza">{ico} {u.faza}</div>
            <div class="aparat-body">
                <div style="font-size:9px; font-weight:bold; color:#555;">{u.nazwa}</div>
                <div style="margin:8px 0;"><span style="font-size:14px; font-weight:bold;">{u.charakterystyka}</span><span class="amp-text">{u.prad}A</span></div>
                <div class="aparat-label">{u.opis}</div>
            </div>
            <div class="aparat-footer">{"■"*u.moduly}<br>{u.moduly} MOD</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- RAPORTY I PODSUMOWANIA ---
if st.session_state['szyna']:
    st.divider()
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("📋 Specyfikacja Szyn DIN")
        for r_idx, rzad in enumerate(rzedy):
            if rzad:
                st.write(f"**Szyna {r_idx + 1}**")
                df_rzad = pd.DataFrame([{
                    "Nr": f"A{i+1}", "Aparat": u.nazwa, "Parametry": f"{u.charakterystyka}{u.prad}A",
                    "Faza": u.faza, "Przewód": u.przewod, "Opis": u.opis
                } for i, u in enumerate(rzad)])
                st.table(df_rzad)

    with col_b:
        st.subheader("🛒 Lista Zakupowa (BOM)")
        lista_nazw = [f"{u.nazwa} {u.charakterystyka}{u.prad}" for u in st.session_state['szyna']]
        bom = pd.Series(lista_nazw).value_counts().reset_index()
        bom.columns = ['Urządzenie', 'Sztuk']
        st.dataframe(bom, hide_index=True, use_container_width=True)
        
        total_mod = sum(u.moduly for u in st.session_state['szyna'])
        st.info(f"📐 Razem modułów: {total_mod}\n\n📦 Zalecana obudowa: min. {len(rzedy)}x12 DIN")
