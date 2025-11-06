import streamlit as st
from calculations.materials import get_concrete_properties
from calculations.flexion import calc_flexural_capacity
from calculations.shear import calc_shear_capacity
from calculations.visualization import visualize_stress_block, visualize_strain_diagram
from utils.helpers import validate_section

st.set_page_config(page_title="Verifica SLU - Sezioni in C.A.", page_icon="🏗️", layout="wide")

# === Carica CSS personalizzato ===
def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/style.css")

# === Header interfaccia principale ===
st.markdown('<h1 class="main-header">🏗️ Verifica SLU Sezioni in Calcestruzzo Armato</h1>', unsafe_allow_html=True)

# === Sidebar - Parametri di input ===
st.sidebar.header("📋 Parametri di Input")
classe_cls = st.sidebar.selectbox(
    "Classe calcestruzzo",
    ['C20/25','C25/30','C28/35','C30/37','C32/40','C35/45','C40/50','C45/55','C50/60'],
    index=1
)
props = get_concrete_properties(classe_cls)
fck = props['fck']

fyk = st.sidebar.selectbox("Tensione caratteristica acciaio fyk (MPa)", [450], index=0)

gamma_c = st.sidebar.number_input("γc (calcestruzzo)", value=1.5, min_value=1.0, max_value=2.0, step=0.05)
gamma_s = st.sidebar.number_input("γs (acciaio)", value=1.15, min_value=1.0, max_value=2.0, step=0.01)

B = st.sidebar.number_input("Larghezza sezione B (cm)", value=30.0, min_value=10.0) * 10
H = st.sidebar.number_input("Altezza sezione H (cm)", value=50.0, min_value=15.0) * 10
c = st.sidebar.number_input("Copriferro c (cm)", value=3.0, min_value=1.0) * 10

st.sidebar.subheader("Armature longitudinali (barre)")
n_bars_inf = st.sidebar.number_input("Numero barre inferiori", value=3, min_value=0, max_value=20, step=1)
phi_inf = st.sidebar.selectbox("Diametro barre inferiori (mm)", [8,10,12,14,16,18,20,22,24,26,28,30], index=2)
n_bars_sup = st.sidebar.number_input("Numero barre superiori", value=3, min_value=0, max_value=20, step=1)
phi_sup = st.sidebar.selectbox("Diametro barre superiori (mm)", [8,10,12,14,16,18,20,22,24,26,28,30], index=2)

st.sidebar.subheader("Armature trasversali (staffe)")
phi_staffe = st.sidebar.number_input("Diametro staffe [mm]", min_value=6, max_value=20, value=8)
n_bracci = st.sidebar.number_input("N° bracci staffe", min_value=1, max_value=6, value=2)
passo_staffe = st.sidebar.number_input("Passo staffe s [cm]", min_value=5, max_value=50, value=20)

st.sidebar.subheader("Sollecitazioni")
M_Ed = st.sidebar.number_input("Momento sollecitante MEd (kNm)", value=50.0, min_value=0.0)
V_Ed = st.sidebar.number_input("Taglio sollecitante VEd (kN)", value=30.0, min_value=0.0)

# === Validazione geometrica ===
valid, msg = validate_section(B, H, c)
if not valid:
    st.error(msg)
    st.stop()

# === Calcoli ===
flex = calc_flexural_capacity(
    B=B, H=H, c=c,
    n_inf=int(n_bars_inf), phi_inf=float(phi_inf),
    n_sup=int(n_bars_sup), phi_sup=float(phi_sup),
    fck=float(fck), fyk=float(fyk), M_Ed=float(M_Ed),
    gamma_c=float(gamma_c), gamma_s=float(gamma_s)
)

shear = calc_shear_capacity(
    B=B, d=flex['d'], fcd=flex['fcd'], fyd=flex['fyd'],
    phi_staffe=float(phi_staffe), n_bracci=int(n_bracci),
    passo_staffe=float(passo_staffe), V_Ed=float(V_Ed), z=flex.get('z_concrete', None)
)

results = {**flex, **shear}

# === Sezione 1: Risultati numerici principali ===
with st.container():
    st.header("🔢 Risultati numerici principali")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("MRd [kNm]", f"{results['M_Rd']:.2f}")
        st.metric("MEd [kNm]", f"{M_Ed:.2f}", delta=f"{results['M_Rd'] - M_Ed:.2f}")
        st.write(f"Rapporto di verifica = {results['M_Rd']/M_Ed:.2f}" if M_Ed > 0 else "MEd = 0")

    with col2:
        st.metric("VRd [kN]", f"{results['V_Rd']:.2f}")
        st.metric("VEd [kN]", f"{V_Ed:.2f}", delta=f"{results['V_Rd'] - V_Ed:.2f}")
        st.write(f"Rapporto di verifica = {results['rapporto_taglio']:.2f}" if V_Ed > 0 else "VEd = 0")
        
st.markdown("### ✅ Riepilogo Verifiche")
if results['M_Rd'] >= M_Ed and results['V_Rd'] >= V_Ed:
    st.success("Entrambe le verifiche (flessione e taglio) sono SUPERATE ✅")
else:
    st.error("Almeno una verifica NON è soddisfatta ❌")

# === Sezione 2: Visualizzazioni (grafici affiancati) ===
with st.container():
    st.markdown("### 📊 Visualizzazioni")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = visualize_stress_block(
            B=B, H=H, x=results['x'], c=c, fcd=results['fcd'], fyd=results['fyd'],
            n_bars_sup=int(n_bars_sup), n_bars_inf=int(n_bars_inf),
            phi_sup=float(phi_sup), phi_inf=float(phi_inf), results=results
        )
        st.pyplot(fig1)

    with col2:
        fig2 = visualize_strain_diagram(x=results['x'], d=results['d'], H=H, results=results)
        st.pyplot(fig2)

# === Sezione 3: Verifiche e riepilogo ===
with st.container():
    st.markdown("### 🧾 Dettaglio risultati")
    st.write(results)

    st.info(
        "Progetto creato automaticamente a partire da uno script di verifica. "
        "Controlla parametri e formule prima dell'uso in progetto reale."
    )
