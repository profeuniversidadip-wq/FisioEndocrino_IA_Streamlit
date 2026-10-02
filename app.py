
import streamlit as st
import json, random
from pathlib import Path

st.set_page_config(page_title="FisioEndocrino IA", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 15% 15%, rgba(219,234,254,.85), transparent 34%),
      radial-gradient(circle at 85% 12%, rgba(224,242,254,.75), transparent 32%),
      linear-gradient(180deg, #f8fbff 0%, #eef5fb 100%);
}
.block-container{
    max-width:760px;
    padding-top:1rem;
    padding-bottom:2rem;
}
h1{
    font-size:2rem!important;
    margin-bottom:.2rem!important;
    color:#1f2937!important;
}
h2,h3{color:#25324a!important;}
div[data-testid="stMetric"]{
    background:rgba(255,255,255,.78);
    border:1px solid #d8e2ef;
    border-radius:14px;
    padding:.55rem .7rem;
}
.stButton>button{
    min-height:46px;
    border-radius:12px;
    font-size:1rem;
}
button[kind="primary"]{
    font-weight:700;
}
.footer-box{
    margin-top:2.2rem;
    padding-top:.9rem;
    border-top:1px solid #d6dfeb;
    text-align:center;
    color:#667085;
    font-size:.88rem;
}
.restart-note{
    text-align:right;
    color:#8a94a6;
    font-size:.78rem;
    margin-bottom:.25rem;
}
@media(max-width:520px){
    .block-container{
        padding-left:.8rem;
        padding-right:.8rem;
    }
    h1{font-size:1.55rem!important;}
    .stButton>button{font-size:.95rem;}
}
</style>
""", unsafe_allow_html=True)

with open(Path(__file__).with_name("preguntas_endocrino.json"), encoding="utf-8") as f:
    PREGUNTAS=json.load(f)
POR_ID={q["id"]:q for q in PREGUNTAS}
TOTAL=10

def mostrar_footer():
    st.markdown("""
    <div class="footer-box">
      <strong>Desarrollado por Cristian Barahona Videla</strong><br>
      Uso educativo · © 2026
    </div>
    """, unsafe_allow_html=True)

def reset(keep_name=True):
    nombre=st.session_state.get("nombre","") if keep_name else ""
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.nombre=nombre
    st.session_state.iniciada=False
    st.session_state.respondidas=0
    st.session_state.aciertos=0
    st.session_state.errores=0
    st.session_state.intento=1
    st.session_state.bloqueada=False
    st.session_state.feedback=""
    st.session_state.feedback_tipo=""
    st.session_state.siguiente_id=None
    st.session_state.historial=[]
    st.session_state.visitadas=set()

if "iniciada" not in st.session_state:
    reset(False)

def inicio():
    return random.choice([q for q in PREGUNTAS if q["nivel"]==1])["id"]

def siguiente(q, acierto):
    objetivo=q.get("siguienteSiAcierta") if acierto else q.get("siguienteSiFalla")
    if objetivo in POR_ID:
        return objetivo
    nivel=min(4,q["nivel"]+1) if acierto else max(1,q["nivel"]-1)
    cand=[p for p in PREGUNTAS if p["nivel"]==nivel and p["id"] not in st.session_state.visitadas]
    if not cand:
        cand=[p for p in PREGUNTAS if p["id"] not in st.session_state.visitadas]
    return random.choice(cand)["id"] if cand else inicio()

st.title("FisioEndocrino IA")
st.caption("Entrenamiento adaptativo · 10 preguntas por sesión")

if not st.session_state.iniciada:
    st.write("**Cómo funciona:** 10 preguntas, hasta 2 intentos, retroalimentación inmediata y dificultad adaptativa.")
    nombre=st.text_input("Nombre del estudiante", value=st.session_state.nombre)
    if st.button("Comenzar sesión", use_container_width=True, type="primary"):
        if not nombre.strip():
            st.warning("Ingresa tu nombre.")
        else:
            st.session_state.nombre=nombre.strip()
            st.session_state.actual_id=inicio()
            st.session_state.iniciada=True
            st.rerun()
    mostrar_footer()
    st.stop()

if st.session_state.respondidas>=TOTAL:
    st.success(f"Sesión completada, {st.session_state.nombre}.")
    pct=round(st.session_state.aciertos/TOTAL*100)
    a,b,c=st.columns(3)
    a.metric("Aciertos",f"{st.session_state.aciertos}/{TOTAL}")
    b.metric("Errores",st.session_state.errores)
    c.metric("Resultado",f"{pct}%")
    niveles=[h["nivel"] for h in st.session_state.historial]
    if niveles: st.write(f"**Nivel máximo alcanzado:** {max(niveles)}")
    with st.expander("Ver resumen"):
        for i,h in enumerate(st.session_state.historial,1):
            st.write(f"{i}. {'✓' if h['correcta'] else '✗'} Nivel {h['nivel']} · {h['tema']}")
    if st.button("Nueva sesión",use_container_width=True,type="primary"):
        reset(True)
        st.session_state.iniciada=True
        st.session_state.actual_id=inicio()
        st.rerun()
    mostrar_footer()
    st.stop()

q=POR_ID[st.session_state.actual_id]
st.session_state.visitadas.add(q["id"])

c1,c2,c3=st.columns(3)
c1.metric("Pregunta",f"{st.session_state.respondidas+1}/{TOTAL}")
c2.metric("Nivel",q["nivel"])
c3.metric("Intento",f"{st.session_state.intento}/2")
st.progress(st.session_state.respondidas/TOTAL)

st.markdown(f"**Tema:** {q['tema']}")
st.subheader(q["pregunta"])

letras=["A","B","C","D"]
opciones=[f"{letras[i]}. {t}" for i,t in enumerate(q["alternativas"])]
sel=st.radio("Selecciona una alternativa:",opciones,index=None,
             key=f"q_{q['id']}_i_{st.session_state.intento}",
             disabled=st.session_state.bloqueada)

responder=st.button(
    "Responder",
    use_container_width=True,
    type="primary",
    disabled=(sel is None or st.session_state.bloqueada)
)

st.markdown('<div class="restart-note">Opciones de sesión</div>', unsafe_allow_html=True)
_, col_reset = st.columns([4.2, 1.15])
with col_reset:
    if st.button("Reiniciar sesión", use_container_width=True):
        reset(True)
        st.rerun()

if responder:
    idx=opciones.index(sel)
    correcta=(idx==q["correcta"])
    if correcta:
        st.session_state.aciertos+=1
        st.session_state.respondidas+=1
        st.session_state.bloqueada=True
        st.session_state.feedback_tipo="ok"
        st.session_state.feedback="Correcto. "+q["explicacionCorrecta"]
        st.session_state.siguiente_id=siguiente(q,True)
        st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":True})
    else:
        st.session_state.errores+=1
        txt=q["feedbackIncorrecto"][idx] or "Revisa el concepto."
        if st.session_state.intento==1:
            st.session_state.intento=2
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=txt+"\n\n**Tienes un segundo intento.**"
        else:
            st.session_state.respondidas+=1
            st.session_state.bloqueada=True
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=txt+f"\n\n**Respuesta correcta:** {q['alternativas'][q['correcta']]}\n\n**Idea clave:** {q['explicacionCorrecta']}"
            st.session_state.siguiente_id=siguiente(q,False)
            st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":False})
    st.rerun()

if st.session_state.feedback:
    (st.success if st.session_state.feedback_tipo=="ok" else st.warning)(st.session_state.feedback)

if st.session_state.bloqueada:
    if st.button("Continuar",use_container_width=True,type="primary"):
        st.session_state.actual_id=st.session_state.siguiente_id
        st.session_state.intento=1
        st.session_state.bloqueada=False
        st.session_state.feedback=""
        st.session_state.feedback_tipo=""
        st.session_state.siguiente_id=None
        st.rerun()
elif st.session_state.intento==2 and st.session_state.feedback:
    st.info("Vuelve a seleccionar una alternativa y utiliza tu segundo intento.")

mostrar_footer()
