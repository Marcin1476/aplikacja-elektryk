import streamlit as st
import pandas as pd

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Asystent Elektryka Fundament v2.5.3", layout="wide")

# --- 2. INICJALIZACJA I OBSŁUGA BŁĘDÓW SESJI ---
if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []

# --- 3. PARAMETRY ---
RZAD_MAX_MOD = 12 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}
U_N = 230  

# --- 4. CSS (Wizualizacja) ---
st.markdown("""
    <style>
    .obudowa { background-color: #3d3d3d; padding: 25px; border-radius: 12px; border: 6px solid #222; }
    .szyna-din {
        display: flex; flex-direction: row; align-items: flex-start;
        overflow-x: auto; padding: 40px 15px; background-color: #b0b0b0;
        border-radius: 4px; border-top: 20px solid #777; border-bottom: 20px solid #777;
        min-height: 400px; gap: 8px; margin-bottom: 30px;
    }
    .aparat {
        border: 2px solid #111; border-radius: 4px; text-align: center;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.5); display: flex;
        flex-direction: column; min-height: 360px; flex-shrink: 0; background-color: white;
    }
    .aparat-brand { font-size: 10px; font-weight: bold; color: #fff; padding: 3px 0; text-transform: uppercase; }
    .amp-text { font-size: 30px; font-weight: 900; color: #d35400; display: block; line-height: 1; }
    .aparat-label { border: 1px solid #ccc; background: #fdfdfd; font-size: 11px; min-height: 60px; 
                   display: flex; align-items: center; justify-content: center; margin: 8px; padding: 4px; font-weight: bold; color: #000; }
    .aparat-footer { background: #1a252f; color: #f1c40f; padding: 10px 2px; margin-top: auto; font-size: 11px; border-top: 1px solid #000; }
    .short-circuit { font-size: 11px; color: #c0392b; font-weight: bold; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. KLASA DANYCH ---
class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis="", zs=0.0, rcd_group="Brak"):
        self.nazwa = nazwa
        self.charakterystyka = charakterystyka
        self.prad = prad
        self.moduly = moduly
        self.faza = faza
        self.opis = opis
        self.zs = zs  
        self.rcd_group = rcd_group

# --- 6. BIBLIOTEKA ---
BIBLIOTEKA = [
    {"n": "Rozłącznik Główny 3P", "c": "FR", "p": "100", "m": 3},
    {"n": "Ochronnik T1+T2", "c": "SPD", "p": "B+C", "m": 4},
    {"n": "Różnicówka 4P 30mA", "c": "RCCB", "p": "40", "m": 4},
    {"n": "Różnicówka 2P 30mA", "c": "RCCB", "p": "25", "m": 2},
    {"n": "Wyłącznik 1P", "c": "B", "p": "10", "m": 1},
    {"n": "Wyłącznik 1P", "c": "B", "p": "16", "m": 1},
    {"n": "Wyłącznik 3P", "c": "B", "p": "16", "m": 3},
]

# --- 7. PANEL BOCZNY ---
st.sidebar.title("🛠️ Projektant v2.5.3")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]

opcje_tekst = [f"{u['c']}{u['p']} | {u['n']}" for u in BIBLIOTEKA]
idx = st.sidebar.selectbox("Wybierz aparat:", range(len(BIBLIOTEKA)), format_func=lambda x: opcje_tekst[x])

with st.sidebar.expander("Parametry dodatkowe", expanded=True):
    etyk = st.sidebar.text_input("Nazwa obwodu:", "Gniazda")
    faz = st.sidebar.radio("Zasilanie:", ["L1", "L2", "L3"]) if BIBLIOTEKA[idx]['m'] < 3 else "L123"
    zs_val = st.sidebar.number_input("Impedancja Zs [Ω]:", min_value=0.0, max_value=10.0, value=0.0, step=0.01)
    
    # Dynamiczne budowanie listy grup RCD
    try:
        lista_rcd = ["Brak"] + [f"RCD {i+1}" for i, u in enumerate(st.session_state['szyna']) if "RCCB" in getattr(u, 'charakterystyka', '')]
    except:
        lista_rcd = ["Brak"]
    grupa_rcd = st.sidebar.selectbox("Przypisz do RCD:", lista_rcd)

if st.sidebar.button("Montuj na szynie ➡️", use_container_width=True):
    b = BIBLIOTEKA[idx]
    nowy_aparat = Urzadzenie(b['n'], b['c'], b['p'], b['m'], faz, etyk, zs_val, grupa_rcd)
    st.session_state['szyna'].append(nowy_aparat)
    st.rerun()

if st.sidebar.button("Cofnij ostatni ⬅️"):
    if st.session_state['szyna']:
        st.session_state['szyna'].pop()
        st.rerun()

if st.sidebar.button("Resetuj projekt (Naprawa błędów) 🗑️"):
    st.session_state['szyna'] = []
    st.rerun()

# --- 8. LOGIKA PODZIAŁU NA RZĘDY ---
rzedy = [[]]
akt_mod = 0
for u in st.session_state['szyna']:
    u_mod = getattr(u, 'moduly', 1)
    if akt_mod + u_mod > RZAD_MAX_MOD:
        rzedy.append([u])
        akt_mod = u_mod
    else:
        rzedy[-1].append(u)
        akt_mod += u_mod

# --- 9. WIZUALIZACJA ---
st.title("⚡ Projekt Rozdzielnicy")


st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if not rzad and len(st.session_state['szyna']) == 0:
        st.info("Szafa jest pusta. Dodaj aparaty z panelu bocznego.")
        break
    
    if rzad:
        st.write(f"🏷️ **SZYNIA DIN #{r_i + 1}**")
        html_szyny = '<div class="szyna-din">'
        
        for i, u in enumerate(rzad):
            # Odczyt danych z bezpiecznikiem (getattr chroni przed błędami)
            u_faza = getattr(u, 'faza', 'L1')
            u_zs = getattr(u, 'zs', 0.0)
            u_rcd = getattr(u, 'rcd_group', 'Brak')
            u_nazwa = getattr(u, 'nazwa', '---')
            u_char = getattr(u, 'charakterystyka', '---')
            u_prad = getattr(u, 'prad', '---')
            u_opis = getattr(u, 'opis', '---')
            u_mod = getattr(u, 'moduly', 1)
            
            ico = {"L1": "🔴", "L2": "⚫", "L3": "⚪", "L123": "🌈"}.get(u_faza, "➖")
            ik_val = round(U_N / u_zs, 2) if u_zs > 0 else 0
            
            html_szyny += f"""
            <div class="aparat" style="width:{u_mod*65}px; border-top: 15px solid {brand_color};">
                <div class="aparat-brand" style="background-color:{brand_color};">{prod_name}</div>
                <div style="font-size:11px; font-weight:bold; background:#222; color:#fff; padding:2px;">R{r_i+1}-A{i+1}</div>
                <div style="font-size:14px; margin:5px 0;">{ico} {u_faza}</div>
                <div class="aparat-body">
                    <div style="font-size:9px; font-weight:bold; color:#444;">{u_nazwa}</div>
                    <div style="margin:8px 0;">
                        <span style="font-size:14px; font-weight:bold;">{u_char}</span>
                        <span class="amp-text">{u_prad}A</span>
                    </div>
                    {f'<div class="short-circuit">Ik: {ik_val}A</div>' if ik_val > 0 else ''}
                    {f'<div style="font-size:8px; color:green;">Grp: {u_rcd}</div>' if u_rcd != "Brak" else ''}
                    <div class="aparat-label">{u_opis}</div>
                </div>
                <div class="aparat-footer">{"■"*u_mod}<br>{u_mod} MOD</div>
            </div>"""
        
        html_szyny += '</div>'
        st.markdown(html_szyny, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 10. TABELA ---
if st.session_state['szyna']:
    st.divider()
    st.subheader("📋 Specyfikacja techniczna")
    df_data = []
    for i, u in enumerate(st.session_state['szyna']):
        u_zs = getattr(u, 'zs', 0.0)
        df_data.append({
            "Aparat": f"F{i+1}",
            "Typ": f"{getattr(u,'charakterystyka','')}{getattr(u,'prad','')}",
            "Opis": getattr(u, 'opis', ''),
            "Zs [Ω]": u_zs,
            "Ik [A]": round(U_N / u_zs, 2) if u_zs > 0 else 0,
            "Zabezpieczenie RCD": getattr(u, 'rcd_group', 'Brak')
        })
    st.table(pd.DataFrame(df_data))
