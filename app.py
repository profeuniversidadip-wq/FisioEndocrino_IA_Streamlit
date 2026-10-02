
import streamlit as st
import json, random
from pathlib import Path

st.set_page_config(
    page_title="FisioEndocrino IA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp{
    background:
      radial-gradient(circle at 15% 12%, rgba(219,234,254,.88), transparent 33%),
      radial-gradient(circle at 88% 8%, rgba(224,242,254,.72), transparent 28%),
      linear-gradient(180deg,#f8fbff 0%,#eef5fb 100%);
}
.block-container{max-width:1120px;padding-top:.85rem;padding-bottom:2rem}
h1{font-size:2rem!important;margin:.1rem 0!important;color:#1f2937!important}
h2,h3{color:#25324a!important}
div[data-testid="stMetric"]{
    background:rgba(255,255,255,.82);
    border:1px solid #d8e2ef;
    border-radius:14px;
    padding:.45rem .65rem;
}
.stButton>button{min-height:46px;border-radius:12px;font-size:1rem}
.footer-box{
    margin-top:2rem;padding-top:.85rem;border-top:1px solid #d6dfeb;
    text-align:center;color:#667085;font-size:.88rem
}
.action-card{
    border:1px solid #d8e2ef;
    border-radius:16px;
    padding:14px;
    background:rgba(255,255,255,.76);
}
.small-note{color:#7b879a;font-size:.82rem}
@media(max-width:700px){
    .block-container{padding-left:.75rem;padding-right:.75rem}
    h1{font-size:1.55rem!important}
    .stButton>button{font-size:.95rem}
}
</style>
""", unsafe_allow_html=True)

with open(Path(__file__).with_name("preguntas_endocrino.json"), encoding="utf-8") as f:
    PREGUNTAS=json.load(f)

TOTAL=10
POR_NIVEL={n:[q for q in PREGUNTAS if q["nivel"]==n] for n in range(1,5)}

def footer():
    st.markdown("""
    <div class="footer-box">
      <strong>Desarrollado por Cristian Barahona Videla</strong><br>
      Uso educativo · © 2026
    </div>
    """, unsafe_allow_html=True)

def init():
    defaults={
        "iniciada":False,"nombre":"","respondidas":0,"aciertos":0,"errores":0,
        "nivel_actual":1,"intento":1,"bloqueada":False,"feedback":"",
        "feedback_tipo":"","actual_id":None,"historial":[],"usadas_global":set(),
        "usadas_sesion":set(),"sesiones_completadas":0
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def reset_sesion(keep_history=True):
    nombre=st.session_state.get("nombre","")
    usadas=set(st.session_state.get("usadas_global",set())) if keep_history else set()
    sesiones=st.session_state.get("sesiones_completadas",0) if keep_history else 0
    for k in ["respondidas","aciertos","errores","intento","bloqueada","feedback",
              "feedback_tipo","actual_id","historial","usadas_sesion"]:
        if k in st.session_state: del st.session_state[k]
    st.session_state.nombre=nombre
    st.session_state.respondidas=0
    st.session_state.aciertos=0
    st.session_state.errores=0
    st.session_state.intento=1
    st.session_state.bloqueada=False
    st.session_state.feedback=""
    st.session_state.feedback_tipo=""
    st.session_state.actual_id=None
    st.session_state.historial=[]
    st.session_state.usadas_sesion=set()
    st.session_state.usadas_global=usadas
    st.session_state.sesiones_completadas=sesiones
    st.session_state.nivel_actual=1

def elegir_pregunta(nivel):
    # Prioridad: pregunta no usada globalmente del nivel objetivo.
    candidatas=[q for q in POR_NIVEL[nivel] if q["id"] not in st.session_state.usadas_global]
    # Si ese nivel se agotó, usa una no repetida de cualquier nivel.
    if not candidatas:
        candidatas=[q for q in PREGUNTAS if q["id"] not in st.session_state.usadas_global]
    # Si las 80 ya fueron usadas, reinicia el historial de no repetición.
    if not candidatas:
        st.session_state.usadas_global=set()
        candidatas=POR_NIVEL[nivel][:]
    q=random.choice(candidatas)
    st.session_state.usadas_global.add(q["id"])
    st.session_state.usadas_sesion.add(q["id"])
    return q["id"]

def avanzar_nivel(acierto):
    if acierto:
        st.session_state.nivel_actual=min(4, st.session_state.nivel_actual+1)
    else:
        st.session_state.nivel_actual=max(1, st.session_state.nivel_actual-1)

def iniciar():
    reset_sesion(True)
    st.session_state.actual_id=elegir_pregunta(1)
    st.session_state.iniciada=True

init()

# Header: title left, safe restart at top-right using popover confirmation.
head1, head2 = st.columns([6,1.55], vertical_alignment="top")
with head1:
    st.title("FisioEndocrino IA")
    st.caption("Entrenamiento adaptativo · 10 preguntas por sesión · banco de 80 preguntas")
with head2:
    if st.session_state.iniciada:
        with st.popover("↻ Reiniciar sesión", use_container_width=True):
            st.warning("Se perderá el avance de esta sesión.")
            if st.button("Confirmar reinicio", use_container_width=True):
                reset_sesion(True)
                st.session_state.iniciada=False
                st.rerun()

if not st.session_state.iniciada:
    st.markdown("""
    **Cómo funciona**
    - 10 preguntas por sesión.
    - 2 intentos por pregunta.
    - La dificultad aumenta con respuestas correctas y refuerza con errores.
    - El banco contiene 20 preguntas por cada nivel (80 en total).
    - Las preguntas usadas se evitan en las sesiones siguientes mientras mantengas abierta la aplicación.
    """)
    nombre=st.text_input("Nombre del estudiante", value=st.session_state.nombre)
    if st.button("Comenzar sesión", use_container_width=True, type="primary"):
        if nombre.strip():
            st.session_state.nombre=nombre.strip()
            iniciar()
            st.rerun()
        else:
            st.warning("Ingresa tu nombre.")
    footer()
    st.stop()

if st.session_state.respondidas>=TOTAL:
    st.session_state.sesiones_completadas += 1
    st.success(f"Sesión completada, {st.session_state.nombre}.")
    pct=round(st.session_state.aciertos/TOTAL*100)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Aciertos",f"{st.session_state.aciertos}/{TOTAL}")
    c2.metric("Errores",st.session_state.errores)
    c3.metric("Resultado",f"{pct}%")
    c4.metric("Preguntas únicas usadas",len(st.session_state.usadas_global))
    niveles=[h["nivel"] for h in st.session_state.historial]
    if niveles:
        st.write(f"**Nivel máximo alcanzado:** {max(niveles)}")
    with st.expander("Ver resumen de la sesión"):
        for i,h in enumerate(st.session_state.historial,1):
            st.write(f"{i}. {'✓' if h['correcta'] else '✗'} Nivel {h['nivel']} · {h['tema']}")
    if st.button("Nueva sesión sin repetir preguntas", use_container_width=True, type="primary"):
        iniciar()
        st.rerun()
    st.caption("La no repetición se conserva durante esta sesión del navegador. Si se recarga completamente la app, Streamlit puede reiniciar ese historial.")
    footer()
    st.stop()

q=next(q for q in PREGUNTAS if q["id"]==st.session_state.actual_id)

m1,m2,m3,m4=st.columns(4)
m1.metric("Pregunta",f"{st.session_state.respondidas+1}/{TOTAL}")
m2.metric("Nivel",q["nivel"])
m3.metric("Intento",f"{st.session_state.intento}/2")
m4.metric("Sin repetir",len(st.session_state.usadas_global))
st.progress(st.session_state.respondidas/TOTAL)

# Two-column interaction area: question left, action right.
left,right=st.columns([4.6,1.55], gap="large")

with left:
    st.markdown(f"**Tema:** {q['tema']}")
    st.subheader(q["pregunta"])
    letras=["A","B","C","D"]
    opciones=[f"{letras[i]}. {txt}" for i,txt in enumerate(q["alternativas"])]
    sel=st.radio(
        "Selecciona una alternativa:",
        opciones,
        index=None,
        key=f"q_{q['id']}_i_{st.session_state.intento}",
        disabled=st.session_state.bloqueada
    )
    if st.session_state.feedback:
        if st.session_state.feedback_tipo=="ok":
            st.success(st.session_state.feedback)
        else:
            st.warning(st.session_state.feedback)

with right:
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown("**Acción**")
    if not st.session_state.bloqueada:
        responder=st.button(
            "Responder",
            use_container_width=True,
            type="primary",
            disabled=(sel is None)
        )
        if st.session_state.intento==2:
            st.caption("Segundo intento")
    else:
        responder=False
        if st.button("Avanzar →", use_container_width=True, type="primary"):
            st.session_state.actual_id=elegir_pregunta(st.session_state.nivel_actual)
            st.session_state.intento=1
            st.session_state.bloqueada=False
            st.session_state.feedback=""
            st.session_state.feedback_tipo=""
            st.rerun()
    st.markdown('<div class="small-note">El botón de avance permanece aquí para evitar desplazamientos.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if responder:
    idx=opciones.index(sel)
    correcta=(idx==q["correcta"])
    if correcta:
        st.session_state.aciertos+=1
        st.session_state.respondidas+=1
        st.session_state.bloqueada=True
        st.session_state.feedback_tipo="ok"
        st.session_state.feedback="Correcto. "+q["explicacionCorrecta"]
        st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":True})
        avanzar_nivel(True)
    else:
        st.session_state.errores+=1
        texto=q["feedbackIncorrecto"][idx] or "Revisa el concepto."
        if st.session_state.intento==1:
            st.session_state.intento=2
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=texto+"\n\n**Tienes un segundo intento.**"
        else:
            st.session_state.respondidas+=1
            st.session_state.bloqueada=True
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=(
                texto+
                f"\n\n**Respuesta correcta:** {q['alternativas'][q['correcta']]}"+
                f"\n\n**Idea clave:** {q['explicacionCorrecta']}"
            )
            st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":False})
            avanzar_nivel(False)
    st.rerun()

footer()
