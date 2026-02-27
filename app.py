import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="Projektant Rozdzielnicy - Marcin Szymański", layout="wide")

if 'szyna' not in st.session_state:
    st.session_state['szyna'] = []
if 'next_faza_idx' not in st.session_state:
    st.session_state['next_faza_idx'] = 0

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'DOKUMENTACJA TECHNICZNA ROZDZIELNICY', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Projektant: Marcin Szymański | Strona {self.page_no()}', 0, 0, 'C')

def generuj_pdf_operat(dane_klienta, dane_miejsce, lista_aparatów, schemat_tekst):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    pdf.cell(200, 10, txt=f"Inwestor: {dane_klienta}", ln=True)
    pdf.cell(200, 10, txt=f"Lokalizacja: {dane_miejsce}", ln=True)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d.%m.%Y')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="1. Specyfikacja techniczna", ln=True)
    pdf.set_font("Arial", size=9)
    
    col_width = 190 / 4
    pdf.cell(col_width, 7, "Aparat", border=1)
    pdf.cell(col_width, 7, "Faza", border=1)
    pdf.cell(col_width, 7, "Przewod", border=1)
    pdf.cell(col_width, 7, "Opis", border=1)
    pdf.ln()

    for u in lista_aparatów:
        pdf.cell(col_width, 6, f"{u.charakterystyka}{u.prad}", border=1)
        pdf.cell(col_width, 6, str(u.faza), border=1)
        pdf.cell(col_width, 6, str(u.przekroj), border=1)
        pdf.cell(col_width, 6, str(u.opis), border=1)
        pdf.ln()

    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="2. Schemat jednokreskowy ideowy", ln=True)
    pdf.ln(5)
    pdf.set_font("Courier", size=9)
    
    for line in schemat_tekst.split('\n'):
        pdf.cell(0, 5, txt=line, ln=True)

    return pdf.output(dest='S').encode('latin-1', errors='replace')

st.markdown("""
    <style>
    .obudowa { background-color: #333; padding: 25px; border-radius: 12px; }
    .szyna-din {
        display: flex; flex-direction: row; background-color: #b0b0b0;
        padding: 25px 5px; border-top: 10px solid #777; border-bottom: 10px solid #777;
        gap: 4px; margin-bottom: 15px; overflow-x: auto;
    }
    .header-box {
        border: 3px solid #1f1f1f;
        padding: 0;
        margin-bottom: 25px;
        background-color: #ffffff;
    }
    .header-top {
        background-color: #1f1f1f;
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .schemat-box {
        font-family: 'Courier New', Courier, monospace;
        border: 2px solid #000;
        padding: 20px;
        background-color: #ffffff;
        white-space: pre;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

RZAD_MAX_MOD = 18 
PRODUCENCI = {"Eaton": "#005EB8", "Legrand": "#E20613", "Schneider": "#3dcd58", "Hager": "#00305d"}

DB_APARATY = {
    "Zabezpieczenia Nadprądowe (MCB)": [
        {"n": "Wyłącznik 1P", "c": "B", "p": ["6", "10", "13", "16", "20", "25", "32", "40"], "m": 1},
        {"n": "Wyłącznik 3P", "c": "B", "p": ["16", "20", "25", "32", "40"], "m": 3},
    ],
    "Różnicowoprądowe (RCD)": [
        {"n": "Różnicówka 2P 30mA", "c": "Typ A", "p": ["25", "40"], "m": 2},
        {"n": "Różnicówka 4P 30mA", "c": "Typ A", "p": ["25", "40", "63"], "m": 4},
    ],
    "Pozostałe": [
        {"n": "Rozłącznik Główny 3P", "c": "FR", "p": ["63", "100"], "m": 3},
        {"n": "Ochronnik T1+T2", "c": "SPD", "p": ["B+C"], "m": 4},
        {"n": "Lampka Kontrolna", "c": "L-3", "p": ["230V"], "m": 1},
    ]
}

def wylicz_przekroj(prad_str):
    try:
        p = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad_str))))
        if p <= 13: return "1.5 mm2"
        elif p <= 20: return "2.5 mm2"
        elif p <= 25: return "4.0 mm2"
        elif p <= 40: return "6.0 mm2"
        else: return "10.0 mm2"
    except: return "2.5 mm2"

class Urzadzenie:
    def __init__(self, nazwa, charakterystyka, prad, moduly, faza, opis=""):
        self.nazwa, self.charakterystyka, self.prad, self.moduly = nazwa, charakterystyka, prad, moduly
        self.faza, self.opis = faza, opis
        self.przekroj = wylicz_przekroj(prad)
        try: self.val_a = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(prad))))
        except: self.val_a = 0.0

st.sidebar.title("Kreator Projektu")
prod_name = st.sidebar.selectbox("Producent:", list(PRODUCENCI.keys()))
brand_color = PRODUCENCI[prod_name]
klient = st.sidebar.text_input("Inwestor:", "Jan Kowalski")
miejsce = st.sidebar.text_input("Lokalizacja:", "Rozdzielnica R1")
wsp_j = st.sidebar.slider("Wspolczynnik:", 0.1, 1.0, 0.6)
limit_a = st.sidebar.number_input("Limit [A]:", value=25)
kat = st.sidebar.selectbox("Kategoria:", list(DB_APARATY.keys()))
ap_typ = st.sidebar.selectbox("Urzadzenie:", DB_APARATY[kat], format_func=lambda x: f"{x['n']} ({x['c']})")
ap_prad = st.sidebar.selectbox("Prad:", ap_typ['p'])
f_auto = "L123" if ap_typ['m'] >= 3 else st.sidebar.selectbox("Faza:", ["L1", "L2", "L3"], index=st.session_state['next_faza_idx'])
etyk = st.sidebar.text_input("Opis:", "Obwod")

if st.sidebar.button("Dodaj aparat"):
    st.session_state['szyna'].append(Urzadzenie(ap_typ['n'], ap_typ['c'], ap_prad, ap_typ['m'], f_auto, etyk))
    if ap_typ['m'] < 3: st.session_state['next_faza_idx'] = (st.session_state['next_faza_idx'] + 1) % 3
    st.rerun()

if st.sidebar.button("Wyczysc szafe"):
    st.session_state['szyna'] = []; st.rerun()

st.markdown(f'<div class="header-box"><div class="header-top">Dokumentacja Techniczna Rozdzielnicy</div></div>', unsafe_allow_html=True)

rzedy = [[]]; akt_m = 0
for u in st.session_state['szyna']:
    if akt_m + u.moduly > RZAD_MAX_MOD: rzedy.append([u]); akt_m = u.moduly
    else: rzedy[-1].append(u); akt_m += u.moduly

st.markdown('<div class="obudowa">', unsafe_allow_html=True)
for r_i, rzad in enumerate(rzedy):
    if rzad:
        st.write(f"SZYNIA DIN {r_i+1}")
        html = '<div class="szyna-din">'
        for u in rzad:
            html += f'<div style="width:{u.moduly*45}px; border:1px solid #000; background:#fff; text-align:center; min-height:200px; border-top:8px solid {brand_color};">' \
                    f'<div style="font-size:10px;">{u.faza}</div>' \
                    f'<div style="font-size:18px; font-weight:bold;">{u.charakterystyka}{u.prad}</div>' \
                    f'<div style="font-size:9px;">{u.opis}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['szyna']:
    st.subheader("Schemat jednokreskowy")
    sch_lines = ["ZASILANIE: Siec TN-S 3x230/400V", "I"]
    for u in st.session_state['szyna']:
        sym = "---[" if u.moduly == 1 else "---[==="
        sch_lines.append(f"I---({u.faza}){sym} {u.charakterystyka}{u.prad} ]---> {u.opis}")
    
    sch_final = "\n".join(sch_lines)
    st.markdown(f'<div class="schemat-box">{sch_final}</div>', unsafe_allow_html=True)

    pdf_data = generuj_pdf_operat(klient, miejsce, st.session_state['szyna'], sch_final)
    st.sidebar.download_button(label="POBIERZ PELNA DOKUMENTACJE (PDF)", data=pdf_data, file_name="dokumentacja_rozdzielnicy.pdf", mime="application/pdf", use_container_width=True)

st.markdown(f'<div style="text-align:right; font-size:10px;">© {datetime.now().year} Marcin Szymanski</div>', unsafe_allow_html=True)
