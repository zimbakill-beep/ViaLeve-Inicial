import os
import streamlit as st
from typing import Dict, Any, List
from datetime import date

st.set_page_config(page_title="ViaLeve - Sua Vida Mais Leve Começa Aqui", page_icon="💊", layout="centered")

LOGO_SVG = """
<svg width="720" height="180" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0EA5A4" />
      <stop offset="100%" stop-color="#94E7E3" />
    </linearGradient>
  </defs>
  <g transform="translate(10,20)">
    <circle cx="70" cy="70" r="62" fill="url(#g1)"/>
    <path d="M45 70 C60 45, 80 40, 100 55 C95 60, 85 68, 75 78 C68 84, 60 90, 55 94 C58 84, 58 78, 60 70 Z" fill="#ffffff" opacity="0.95"/>
    <path d="M55 90 L70 105 L105 70" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>
  </g>
  <g transform="translate(160,40)">
    <text x="0" y="55" font-size="64" font-family="Inter, Arial, Helvetica, sans-serif" font-weight="700" fill="#0EA5A4">Via</text>
    <text x="98" y="55" font-size="64" font-family="Inter, Arial, Helvetica, sans-serif" font-weight="600" fill="#0EA5A4">Leve</text>
    <text x="0" y="105" font-size="20" font-family="Inter, Arial, Helvetica, sans-serif" fill="#475569">Sua Vida Mais Leve Começa Aqui</text>
  </g>
</svg>
"""

st.markdown(
    """
    <style>
      :root { --brand: #0EA5A4; --brandSoft: #94E7E3; --ink: #0F172A; }
      .logo-wrap { display:flex; align-items:center; gap:14px; margin: 0 0 12px 0; }
      .logo-wrap svg { max-width: 100%; height: auto; }
      .card {
        background: linear-gradient(135deg, #0EA5A4 0%, #26C0BE 60%, #94E7E3 100%);
        border: 0;
        border-radius: 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,.12);
        color: #ffffff !important;
      }
      .card * { color: #ffffff !important; }
      .crumbs { display:flex; gap:8px; flex-wrap:wrap; margin: 10px 0 16px 0;}
      .crumb { padding:6px 10px; border-radius:999px; border:1px solid #e2e8f0; background:#fff; color:#0f172a; font-size:0.85rem;}
      .crumb.active { background: var(--brandSoft); border-color: #c7f3ef; }
      .muted { color:#0F172A; font-size:0.9rem; }
      .actions { margin-top: .5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

def init_state():
    defaults = {"step": 0, "answers": {}, "eligibility": None, "exclusion_reasons": [], "consent_ok": False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def go_to(step: int):
    st.session_state.step = max(0, min(5, step))
    st.experimental_rerun()

def next_step(): go_to(st.session_state.step + 1)
def prev_step(): go_to(st.session_state.step - 1)

def reset_flow():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state(); st.experimental_rerun()

def calc_idade(d: date | None) -> int | None:
    if not d: return None
    today = date.today()
    return today.year - d.year - ((today.month, today.day) < (d.month, d.day))

EXCIPIENTES_COMUNS = [
    "Polietilenoglicol (PEG)",
    "Metacresol / Fenol",
    "Fosfatos (fosfato dissódico etc.)",
    "Látex (agulhas/rolhas/camisinha)",
    "Carboximetilcelulose",
    "Trometamina (TRIS)",
    "Não tenho alergia a esses componentes",
]

def evaluate_rules(a: Dict[str, Any]):
    exclusion = []
    g = lambda k, d=None: a.get(k, d)

    if g("data_nascimento"):
        try:
            dob = g("data_nascimento")
            if isinstance(dob, str):
                dob = date.fromisoformat(dob)
            idade = calc_idade(dob)
            if idade is not None:
                a["idade"] = idade
                a["idade_calculada"] = idade
        except Exception:
            pass

    if g("idade") is not None and g("idade") < 18: exclusion.append("Menor de 18 anos.")
    if g("gravidez") == "sim": exclusion.append("Gestação em curso.")
    if g("amamentando") == "sim": exclusion.append("Amamentação em curso.")
    if g("tratamento_cancer") == "sim": exclusion.append("Tratamento oncológico ativo.")
    if g("pancreatite_previa") == "sim": exclusion.append("História de pancreatite prévia.")
    if g("historico_mtc_men2") == "sim": exclusion.append("História pessoal/familiar de carcinoma medular de tireoide (MTC) ou MEN2.")
    if g("alergia_glp1") == "sim": exclusion.append("Hipersensibilidade conhecida a análogos de GLP-1.")
    if g("alergias_componentes"):
        if g("alergias_componentes") != ["Não tenho alergia a esses componentes"]:
            exclusion.append("Alergia relatada a excipientes comuns de formulações injetáveis (ver detalhes).")
    if g("gi_grave") == "sim": exclusion.append("Doença gastrointestinal grave ativa.")
    if g("gastroparesia") == "sim": exclusion.append("Gastroparesia diagnosticada.")
    if g("colecistite_12m") == "sim": exclusion.append("Colecistite/colelitíase sintomática nos últimos 12 meses.")
    if g("insuf_renal") in ["moderada", "grave"]: exclusion.append("Insuficiência renal moderada/grave (necessita avaliação médica).")
    if g("insuf_hepatica") in ["moderada", "grave"]: exclusion.append("Insuficiência hepática moderada/grave (necessita avaliação médica).")
    if g("transtorno_alimentar") == "sim": exclusion.append("Transtorno alimentar ativo.")
    if g("uso_corticoide") == "sim": exclusion.append("Uso crônico de corticoide (requer avaliação).")
    if g("antipsicoticos") == "sim": exclusion.append("Uso de antipsicóticos (requer avaliação).")

    peso, altura = g("peso"), g("altura")
    try:
        imc = float(peso) / (float(altura) ** 2) if peso and altura else None
    except Exception:
        imc = None
    if imc is not None and imc < 27 and g("tem_comorbidades") == "nao":
        exclusion.append("IMC < 27 sem comorbidades relevantes.")

    return ("excluido" if exclusion else "potencialmente_elegivel"), exclusion

STEP_NAMES=["Sobre você","Sua saúde","Condições importantes","Medicações & alergias","Histórico & objetivo","Revisar & confirmar"]
def crumbs():
    st.markdown("<div class='crumbs'>" + "".join([f"<span class='crumb {'active' if i==st.session_state.step else ''}'>{i+1}. {n}</span>" for i,n in enumerate(STEP_NAMES)]) + "</div>", unsafe_allow_html=True)

def norm_orgao(v: str) -> str:
    mapa = {"Está normal":"normal","Normal":"normal","normal":"normal","Leve":"leve","leve":"leve","Moderada":"moderada","moderada":"moderada","Grave":"grave","grave":"grave","Não sei informar":"desconhecido","não sei informar":"desconhecido"}
    return mapa.get(v, "desconhecido")

# App
init_state()
st.markdown(f"<div class='logo-wrap'>{LOGO_SVG}</div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="card">
  <b>Como funciona</b>
  <ul style="margin: .5rem 0 0 .9rem;">
    <li>Em poucos minutos você responde perguntas simples.</li>
    <li>Cada pessoa tem uma história única — queremos conhecer a sua.</li>
    <li>Depois das respostas, nosso <b>time médico</b> confere tudo com cuidado.</li>
    <li>Se estiver tudo adequado, seguimos com a orientação terapêutica e prescrição.</li>
  </ul>
</div>
""",
    unsafe_allow_html=True,
)

crumbs()
st.progress((st.session_state.step + 1) / 6)

if st.session_state.step == 0:
    st.subheader("1) Vamos começar?")
    with st.form("step0"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo *", value=st.session_state.answers.get("nome", ""), placeholder="Seu nome e sobrenome")
            email = st.text_input("E-mail *", value=st.session_state.answers.get("email", ""), placeholder="voce@exemplo.com")
        with col2:
            hoje = date.today()
            default_iso = st.session_state.answers.get("data_nascimento")
            if isinstance(default_iso, str) and default_iso:
                try:
                    d = date.fromisoformat(default_iso)
                    dia_default, mes_default, ano_default = d.day, d.month, d.year
                except Exception:
                    dia_default, mes_default, ano_default = 1, 1, 1990
            else:
                dia_default, mes_default, ano_default = 1, 1, 1990

            st.markdown("<div class='muted'>Preencha sua <b>data de nascimento</b> nos campos abaixo (Dia / Mês / Ano).</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,2])
            dia = c1.selectbox("Dia ", list(range(1,32)), index=dia_default-1, placeholder="Selecione o dia")
            mes = c2.selectbox("Mês ", list(range(1,13)), index=mes_default-1, placeholder="Selecione o mês")
            anos = list(range(1900, hoje.year+1))
            try:
                idx = anos.index(ano_default)
            except ValueError:
                idx = len(anos)//2
            ano = c3.selectbox("Ano ", anos, index=idx, placeholder="Selecione o ano")

            identidade = st.selectbox("Como você se identifica? (opcional)", ["Feminino","Masculino","Prefiro não informar"], index=(["Feminino","Masculino","Prefiro não informar"].index(st.session_state.answers.get("identidade","Feminino")) if st.session_state.answers.get("identidade") else 0), placeholder="Selecione uma opção")

        erro = None
        try:
            data_nascimento = date(ano, mes, dia)
            if data_nascimento > date.today():
                erro = "Data de nascimento no futuro não é válida."
        except Exception:
            erro = "Data inválida. Verifique dia/mês/ano."

        st.session_state.answers.update({"nome": nome, "email": email, "identidade": identidade, "data_nascimento": (str(data_nascimento) if not erro else "")})

        colA, colB = st.columns(2)
        with colB:
            b_cont = st.form_submit_button("Continuar ▶️", use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back:
            prev_step()
        if b_cont:
            if not nome.strip(): st.error("Por favor, preencha o nome completo.")
            elif not email.strip(): st.error("Por favor, preencha o e-mail.")
            elif erro: st.error(erro)
            else: next_step()

elif st.session_state.step == 1:
    st.subheader("2) Medidas e saúde atual 🩺")
    with st.form("step1"):
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso (kg) *", min_value=30, max_value=400, step=1, value=int(st.session_state.answers.get("peso", 90)), format="%d")
            tem_comorbidades = st.selectbox("Você tem alguma dessas condições de saúde? (ex.: diabetes tipo 2, pressão alta, apneia do sono, colesterol alto)", ["Sim","Não"], index=0 if st.session_state.answers.get("tem_comorbidades","sim")=="sim" else 1, placeholder="Selecione uma opção")
        with col2:
            altura = st.number_input("Altura (m) *", min_value=1.30, max_value=2.20, step=0.01, value=float(st.session_state.answers.get("altura", 1.70)), help="Ex.: 1.70")
            comorbidades = st.text_area("Se sim, quais comorbidades? (opcional)", value=st.session_state.answers.get("comorbidades", ""))

        st.session_state.answers.update({"peso": peso, "altura": altura, "tem_comorbidades": ("sim" if tem_comorbidades=="Sim" else "nao"), "comorbidades": comorbidades})

        colA, colB = st.columns(2)
        with colB:
            b_cont = st.form_submit_button("Continuar ▶️", use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back: prev_step()
        if b_cont: next_step()

elif st.session_state.step == 2:
    st.subheader("3) Algumas perguntas importantes ⚠️")
    with st.form("step2"):
        col1, col2 = st.columns(2)
        with col1:
            gravidez = st.selectbox("Está grávida?", ["Não","Sim"], index=0 if st.session_state.answers.get("gravidez","nao")=="nao" else 1, placeholder="Selecione uma opção")
            amamentando = st.selectbox("Está amamentando?", ["Não","Sim"], index=0 if st.session_state.answers.get("amamentando","nao")=="nao" else 1, placeholder="Selecione uma opção")
            tratamento_cancer = st.selectbox("Está em tratamento oncológico ativo?", ["Não","Sim"], index=0 if st.session_state.answers.get("tratamento_cancer","nao")=="nao" else 1, placeholder="Selecione uma opção")
            gi_grave = st.selectbox("Doença gastrointestinal grave ativa?", ["Não","Sim"], index=0 if st.session_state.answers.get("gi_grave","nao")=="nao" else 1, placeholder="Selecione uma opção")
            gastroparesia = st.selectbox("Diagnóstico de gastroparesia (esvaziamento gástrico lento)?", ["Não","Sim"], index=0 if st.session_state.answers.get("gastroparesia","nao")=="nao" else 1, placeholder="Selecione uma opção")
        with col2:
            pancreatite_previa = st.selectbox("Já teve pancreatite?", ["Não","Sim"], index=0 if st.session_state.answers.get("pancreatite_previa","nao")=="nao" else 1, placeholder="Selecione uma opção")
            historico_mtc_men2 = st.selectbox("História pessoal/familiar de carcinoma medular de tireoide (MTC) ou MEN2?", ["Não","Sim"], index=0 if st.session_state.answers.get("historico_mtc_men2","nao")=="nao" else 1, placeholder="Selecione uma opção")
            colecistite_12m = st.selectbox("Cólica de vesícula/colecistite nos últimos 12 meses?", ["Não","Sim"], index=0 if st.session_state.answers.get("colecistite_12m","nao")=="nao" else 1, placeholder="Selecione uma opção")
            outras_contra = st.text_area("Outras condições clínicas relevantes? (opcional)", value=st.session_state.answers.get("outras_contra",""))

        st.session_state.answers.update({
            "gravidez": "sim" if gravidez=="Sim" else "nao",
            "amamentando": "sim" if amamentando=="Sim" else "nao",
            "tratamento_cancer": "sim" if tratamento_cancer=="Sim" else "nao",
            "gi_grave": "sim" if gi_grave=="Sim" else "nao",
            "gastroparesia": "sim" if gastroparesia=="Sim" else "nao",
            "pancreatite_previa": "sim" if pancreatite_previa=="Sim" else "nao",
            "historico_mtc_men2": "sim" if historico_mtc_men2=="Sim" else "nao",
            "colecistite_12m": "sim" if colecistite_12m=="Sim" else "nao",
            "outras_contra": outras_contra,
        })

        colA, colB = st.columns(2)
        with colB:
            b_cont = st.form_submit_button("Continuar ▶️", use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back: prev_step()
        if b_cont: next_step()

elif st.session_state.step == 3:
    st.subheader("4) Medicações e alergias 💉")
    with st.form("step3"):
        col1, col2 = st.columns(2)
        with col1:
            insuf_renal = st.selectbox("Como estão seus rins?", ["Normal","Leve","Moderada","Grave","Não sei informar"], index=(["Normal","Leve","Moderada","Grave","Não sei informar"].index(st.session_state.answers.get("insuf_renal","Normal").capitalize()) if st.session_state.answers.get("insuf_renal") else 0), placeholder="Selecione uma opção")
            insuf_hepatica = st.selectbox("E o fígado?", ["Normal","Leve","Moderada","Grave","Não sei informar"], index=(["Normal","Leve","Moderada","Grave","Não sei informar"].index(st.session_state.answers.get("insuf_hepatica","Normal").capitalize()) if st.session_state.answers.get("insuf_hepatica") else 0), placeholder="Selecione uma opção")
            transtorno_alimentar = st.selectbox("Tem transtorno alimentar ativo? (anorexia, bulimia, compulsão alimentar)", ["Não","Sim"], index=0 if st.session_state.answers.get("transtorno_alimentar","nao")=="nao" else 1, placeholder="Selecione uma opção")
            uso_corticoide = st.selectbox("Usa corticoide todos os dias há mais de 3 meses?", ["Não","Sim"], index=0 if st.session_state.answers.get("uso_corticoide","nao")=="nao" else 1, placeholder="Selecione uma opção")
            antipsicoticos = st.selectbox("Usa medicamentos antipsicóticos atualmente?", ["Não","Sim"], index=0 if st.session_state.answers.get("antipsicoticos","nao")=="nao" else 1, placeholder="Selecione uma opção")
        with col2:
            alergias_componentes = st.multiselect("É alérgico(a) a algum destes componentes comuns?", options=EXCIPIENTES_COMUNS, default=st.session_state.answers.get("alergias_componentes", []), placeholder="Selecione os componentes (pode marcar mais de um)")
            if "Não tenho alergia a esses componentes" in alergias_componentes and len(alergias_componentes) > 1:
                alergias_componentes = ["Não tenho alergia a esses componentes"]
            outros_componentes = st.text_input("Alguma outra alergia importante? (opcional)", value=st.session_state.answers.get("outros_componentes",""))
            alergia_glp1 = st.selectbox("Alergia conhecida a medicamentos do tipo GLP-1?", ["Não","Sim"], index=0 if st.session_state.answers.get("alergia_glp1","nao")=="nao" else 1, placeholder="Selecione uma opção")

        st.session_state.answers.update({
            "insuf_renal": norm_orgao(insuf_renal),
            "insuf_hepatica": norm_orgao(insuf_hepatica),
            "transtorno_alimentar": "sim" if transtorno_alimentar=="Sim" else "nao",
            "uso_corticoide": "sim" if uso_corticoide=="Sim" else "nao",
            "antipsicoticos": "sim" if antipsicoticos=="Sim" else "nao",
            "alergias_componentes": alergias_componentes,
            "outros_componentes": outros_componentes,
            "alergia_glp1": "sim" if alergia_glp1=="Sim" else "nao",
        })

        colA, colB = st.columns(2)
        with colB:
            b_cont = st.form_submit_button("Continuar ▶️", use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back: prev_step()
        if b_cont: next_step()

elif st.session_state.step == 4:
    st.subheader("5) Histórico e objetivo 🎯")
    with st.form("step4"):
        col1, col2 = st.columns(2)
        with col1:
            usou_antes = st.selectbox("Já usou medicação para emagrecer?", ["Não","Sim"], index=0 if st.session_state.answers.get("usou_antes","nao")=="nao" else 1, placeholder="Selecione uma opção")
            quais = st.multiselect("Quais? (opcional)", options=["Semaglutida","Tirzepatida","Liraglutida","Orlistate","Bupropiona/Naltrexona","Outros"], default=st.session_state.answers.get("quais", []), placeholder="Selecione as medicações")
            efeitos = st.text_area("Teve algum efeito colateral? (opcional)", value=st.session_state.answers.get("efeitos",""))
        with col2:
            objetivo = st.selectbox("Qual seu objetivo principal?", ["Perda de peso","Controle de comorbidades","Manutenção do peso"], index=(["Perda de peso","Controle de comorbidades","Manutenção do peso"].index(st.session_state.answers.get("objetivo","Perda de peso")) if st.session_state.answers.get("objetivo") else 0), placeholder="Selecione uma opção")
            gestao_expectativas = st.slider("Quão pronto(a) está para mudanças no dia a dia (0–10)?", 0, 10, value=st.session_state.answers.get("pronto_mudar", 6))

        st.session_state.answers.update({"usou_antes": ("sim" if usou_antes=="Sim" else "nao"), "quais": quais, "efeitos": efeitos, "objetivo": objetivo, "pronto_mudar": gestao_expectativas})

        colA, colB = st.columns(2)
        with colB:
            b_cont = st.form_submit_button("Continuar ▶️", use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back: prev_step()
        if b_cont:
            try:
                dob = date.fromisoformat(st.session_state.answers.get("data_nascimento"))
                st.session_state.answers["idade"] = calc_idade(dob)
                st.session_state.answers["idade_calculada"] = st.session_state.answers["idade"]
            except Exception:
                pass
            status, reasons = evaluate_rules(st.session_state.answers)
            st.session_state.eligibility = status
            st.session_state.exclusion_reasons = reasons
            next_step()

elif st.session_state.step == 5:
    st.subheader("6) Seu resultado ✅")
    status = st.session_state.eligibility
    reasons = st.session_state.exclusion_reasons

    if status == "potencialmente_elegivel":
        st.success("🎉 **Parabéns!** Você pode se **beneficiar do tratamento farmacológico**. Vamos seguir para o agendamento da sua consulta.")
        st.info("Na consulta on-line, um médico vai revisar seus dados e, se tudo estiver adequado, definir a melhor estratégia de tratamento para o seu caso.")
        sched = os.environ.get("VIALEVE_SCHED_URL", "")
        if sched:
            st.link_button("Agendar minha consulta agora", sched, use_container_width=True)
        else:
            st.button("Agendar minha consulta (configure VIALEVE_SCHED_URL)", disabled=True, use_container_width=True)
    else:
        st.warning("ℹ️ **Obrigado por responder!** Neste momento, precisamos de uma **avaliação médica** antes de seguir com a prescrição médica.")
        if reasons:
            with st.expander("Entenda o porquê", expanded=False):
                for r in reasons:
                    st.write(f"- {r}")
        st.info("Isso **não significa** que você não pode tratar. Nossa equipe pode orientar um plano seguro e personalizado para você.")

    st.divider()
    st.subheader("Consentimento e autorização")
    with st.expander("Leia o termo completo", expanded=False):
        st.markdown("""
**Termo de Consentimento Informado e Autorização de Teleconsulta (ViaLeve)**

1. **O que é isso?** Este formulário é uma **pré-triagem** e **não** é consulta médica.
2. **Riscos e benefícios:** todo tratamento pode ter efeitos (náuseas, dor abdominal, cálculos na vesícula, pancreatite etc.). A indicação é **individual** e feita pelo médico.
3. **Alternativas:** mudanças de estilo de vida, plano nutricional, atividade física e, quando indicado, procedimentos cirúrgicos.
4. **Privacidade (LGPD):** autorizo o uso dos meus dados **somente** para este serviço, com segurança e possibilidade de revogar o consentimento.
5. **Teleconsulta:** autorizo a **consulta on-line** (telemedicina) e sei que, se necessário, ela pode virar consulta presencial.
6. **Veracidade:** declaro que as informações aqui são verdadeiras.
7. **Assinatura eletrônica:** meu aceite eletrônico tem validade jurídica.
        """)

    with st.form("consent"):
        c1, c2 = st.columns(2)
        with c1:
            aceite_termo = st.checkbox("Li e **aceito** o Termo de Consentimento.", value=st.session_state.answers.get("aceite_termo", False))
            autoriza_teleconsulta = st.checkbox("**Autorizo** a consulta on-line (telemedicina).", value=st.session_state.answers.get("autoriza_teleconsulta", False))
        with c2:
            lgpd = st.checkbox("Autorizo o uso dos meus dados (LGPD).", value=st.session_state.answers.get("lgpd", False))
            veracidade = st.checkbox("Confirmo que as informações são verdadeiras.", value=st.session_state.answers.get("veracidade", False))

        st.session_state.answers.update({"aceite_termo": aceite_termo, "autoriza_teleconsulta": autoriza_teleconsulta, "lgpd": lgpd, "veracidade": veracidade})
        st.session_state.consent_ok = all([aceite_termo, autoriza_teleconsulta, lgpd, veracidade])

        colA, colB = st.columns(2)
        with colB:
            st.download_button("Baixar minhas respostas (JSON)", data=str(st.session_state.answers), file_name="vialeve_respostas.json", mime="application/json", disabled=not st.session_state.consent_ok, use_container_width=True)
        with colA:
            b_back = st.form_submit_button("⬅️ Voltar", use_container_width=True)

        if b_back:
            prev_step()

st.markdown("---")
st.caption("ViaLeve • Protótipo v0.10.1 — PT-BR • Streamlit (Python)")
