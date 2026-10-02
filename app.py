
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
      radial-gradient(circle at 15% 10%, rgba(219,234,254,.80), transparent 30%),
      radial-gradient(circle at 90% 8%, rgba(224,242,254,.68), transparent 26%),
      linear-gradient(180deg,#f8fbff 0%,#eef5fb 100%);
}
.block-container{
    max-width:1080px;
    padding-top:1.15rem;
    padding-bottom:.6rem;
}
h1{
    font-size:1.58rem!important;
    line-height:1.12!important;
    margin:.15rem 0 .15rem 0!important;
    color:#1f2937!important;
}
h2,h3{
    font-size:1.08rem!important;
    line-height:1.25!important;
    margin:.15rem 0!important;
    color:#25324a!important;
}
p, label, .stMarkdown{
    font-size:.88rem;
}
.stCaption{
    font-size:.72rem!important;
    margin-top:0!important;
}
.stButton>button{
    min-height:36px!important;
    border-radius:9px!important;
    font-size:.84rem!important;
    padding:.25rem .55rem!important;
}
div[data-testid="stPopover"] button{
    min-height:34px!important;
    font-size:.78rem!important;
    padding:.2rem .45rem!important;
}
div[data-testid="stProgress"]{
    margin:.15rem 0 .3rem 0!important;
}
div[role="radiogroup"]{
    gap:.08rem!important;
}
div[role="radiogroup"] label{
    padding:.22rem .15rem!important;
    margin:0!important;
    min-height:30px!important;
}
div[role="radiogroup"] p{
    font-size:.84rem!important;
    line-height:1.18!important;
    margin:0!important;
}
.status-row{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:6px;
    margin:.2rem 0 .25rem 0;
}
.status-card{
    background:linear-gradient(180deg,#dceaf7 0%,#d5e4f2 100%);
    border:1px solid #b8cadc;
    border-radius:8px;
    padding:4px 6px;
    text-align:center;
    min-height:40px;
}
.status-label{
    color:#5d6b7c;
    font-size:.60rem;
    line-height:1.05;
    margin-bottom:2px;
}
.status-value{
    color:#23364b;
    font-size:.84rem;
    font-weight:700;
    line-height:1.05;
}
div[data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:11px!important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div{
    padding:.55rem .7rem!important;
}
.action-card{
    border:1px solid #cbd7e6;
    border-radius:11px;
    padding:8px;
    background:rgba(255,255,255,.78);
}
.feedback-error{
    border-left:3px solid #c2410c;
    background:#fff7ed;
    border-radius:7px;
    padding:8px 10px;
    margin-top:.35rem;
    font-size:.80rem;
    line-height:1.25;
}
.feedback-ok{
    border-left:3px solid #15803d;
    background:#f0fdf4;
    border-radius:7px;
    padding:8px 10px;
    margin-top:.35rem;
    font-size:.80rem;
    line-height:1.25;
}
.feedback-label{
    font-weight:700;
    color:#344054;
}
.small-note{
    color:#7b879a;
    font-size:.68rem;
    line-height:1.15;
}
@media(max-width:700px){
    .block-container{
        padding:.75rem .45rem .45rem .45rem;
    }
    h1{
        font-size:1.25rem!important;
    }
    h2,h3{
        font-size:.98rem!important;
    }
    p, label, .stMarkdown{
        font-size:.80rem;
    }
    .status-row{
        gap:4px;
    }
    .status-card{
        padding:3px 3px;
        min-height:36px;
    }
    .status-label{
        font-size:.55rem;
    }
    .status-value{
        font-size:.78rem;
    }
    .stButton>button{
        min-height:34px!important;
        font-size:.80rem!important;
    }
    div[role="radiogroup"] label{
        padding:.18rem .08rem!important;
        min-height:28px!important;
    }
    div[role="radiogroup"] p{
        font-size:.78rem!important;
    }
    .feedback-error,.feedback-ok{
        font-size:.76rem;
        padding:7px 8px;
    }
}

.custom-header-title{
    font-size:1.65rem;
    font-weight:750;
    line-height:1.1;
    color:#1f2937;
    margin:.2rem 0 .15rem 0;
}
.custom-header-sub{
    font-size:.78rem;
    color:#667085;
    margin-bottom:.35rem;
}
.fixed-footer{
    position:fixed;
    left:0;
    right:0;
    bottom:0;
    z-index:999;
    background:rgba(244,248,252,.96);
    border-top:1px solid #d6dfeb;
    text-align:center;
    padding:5px 8px;
    font-size:.68rem;
    color:#667085;
    backdrop-filter:blur(4px);
}
.block-container{
    padding-bottom:2.2rem!important;
}
@media(max-width:700px){
    .custom-header-title{font-size:1.28rem;}
    .custom-header-sub{font-size:.70rem;}
    .fixed-footer{font-size:.62rem;padding:4px 6px;}
}

</style>
""", unsafe_allow_html=True)

with open(Path(__file__).with_name("preguntas_endocrino.json"), encoding="utf-8") as f:
    PREGUNTAS=json.load(f)

TOTAL=10
POR_NIVEL={n:[q for q in PREGUNTAS if q["nivel"]==n] for n in range(1,5)}

def footer():
    st.markdown("""
    <div class="fixed-footer">
      Creado por <strong>Cristian Barahona Videla</strong> · Uso educativo · © 2026
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
head1, head2 = st.columns([5.6,1.3], vertical_alignment="top")
with head1:
    st.markdown("""
    <div class="custom-header-title">FisioEndocrino IA</div>
    <div class="custom-header-sub">10 preguntas por sesión · banco de 80 preguntas</div>
    """, unsafe_allow_html=True)
with head2:
    if st.session_state.iniciada:
        with st.popover("↻ Reiniciar", use_container_width=True):
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

st.markdown(
    f"""
    <div class="status-row">
      <div class="status-card"><div class="status-label">Pregunta</div><div class="status-value">{st.session_state.respondidas+1}/{TOTAL}</div></div>
      <div class="status-card"><div class="status-label">Nivel</div><div class="status-value">{q['nivel']}</div></div>
      <div class="status-card"><div class="status-label">Intento</div><div class="status-value">{st.session_state.intento}/2</div></div>
      <div class="status-card"><div class="status-label">Sin repetir</div><div class="status-value">{len(st.session_state.usadas_global)}</div></div>
    </div>
    """,
    unsafe_allow_html=True
)
st.progress(st.session_state.respondidas/TOTAL)

# Two-column interaction area: question left, action right.
left,right=st.columns([5.2,1.35], gap="small")

with left:
    with st.container(border=True):
        st.caption(f"Tema: {q['tema']}")
        st.markdown(f"**{q['pregunta']}**")
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
        css_class = "feedback-ok" if st.session_state.feedback_tipo=="ok" else "feedback-error"
        st.markdown(
            f'<div class="{css_class}">{st.session_state.feedback}</div>',
            unsafe_allow_html=True
        )

with right:
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    if not st.session_state.bloqueada:
        responder=st.button(
            "Responder",
            use_container_width=True,
            type="primary",
            disabled=(sel is None)
        )
        if st.session_state.intento==2:
            st.caption("2.º intento")
    else:
        responder=False
        if st.button("Avanzar →", use_container_width=True, type="primary"):
            st.session_state.actual_id=elegir_pregunta(st.session_state.nivel_actual)
            st.session_state.intento=1
            st.session_state.bloqueada=False
            st.session_state.feedback=""
            st.session_state.feedback_tipo=""
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if responder:
    idx=opciones.index(sel)
    correcta=(idx==q["correcta"])
    if correcta:
        st.session_state.aciertos+=1
        st.session_state.respondidas+=1
        st.session_state.bloqueada=True
        st.session_state.feedback_tipo="ok"
        st.session_state.feedback=(
            '<span class="feedback-label">Correcto.</span><br><br>'
            '<span class="feedback-label">Idea clave:</span> '
            + q["explicacionCorrecta"]
        )
        st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":True})
        avanzar_nivel(True)
    else:
        st.session_state.errores+=1
        texto=q["feedbackIncorrecto"][idx] or "Revisa el concepto."
        if st.session_state.intento==1:
            st.session_state.intento=2
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=(
                '<span class="feedback-label">Error porque:</span> '
                + texto
                + '<br><br><span class="feedback-label">Tienes un segundo intento.</span>'
            )
        else:
            st.session_state.respondidas+=1
            st.session_state.bloqueada=True
            st.session_state.feedback_tipo="error"
            st.session_state.feedback=(
                '<span class="feedback-label">Error porque:</span> '
                + texto
                + '<br><br><span class="feedback-label">Respuesta correcta:</span> '
                + q["alternativas"][q["correcta"]]
                + '<br><br><span class="feedback-label">Idea clave:</span> '
                + q["explicacionCorrecta"]
            )
            st.session_state.historial.append({"nivel":q["nivel"],"tema":q["tema"],"correcta":False})
            avanzar_nivel(False)
    st.rerun()

footer()
