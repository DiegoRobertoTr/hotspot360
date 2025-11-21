import streamlit as st
from datetime import datetime

try:
    from .. import utils
    from modules import auth
except Exception:
    import sys
    sys.path.append(".")
    from modules import auth, utils


def render_captive_portal():

    st.set_page_config(
        page_title="Tracecom Wi-Fi",
        page_icon="📶",
        layout="centered"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        # Exija que exista um arquivo logo.png na raiz do app
        try:
            st.image("logo.png", width=80)
        except Exception:
            st.write("")  # sem logo, segue em frente
    with col2:
        st.title("📶 Bem-vindo à rede Tracecom!")

    st.markdown(
        "Para melhorar nosso atendimento, preencha os dados abaixo. "
        "**Seu acesso à internet será liberado a seguir!**"
    )

    query_params = st.experimental_get_query_params()
    ap_mac = query_params.get("ap_mac", [None])[0]
    client_mac = query_params.get("client_mac", [None])[0]
    client_ip = query_params.get("client_ip", [None])[0]

    # Conexão com banco
    try:
        db = auth.get_db_connection().tracecom
        hotspots_coll = db.hotspots
        locais_coll = db.locais
        leads_coll = db.leads_hotspot
    except Exception:
        st.error("❌ Erro ao conectar ao banco de dados.")
        st.stop()

    nome_local = "nosso estabelecimento"
    hotspot = None

    if ap_mac:
        try:
            hotspot = hotspots_coll.find_one({
                "mac": ap_mac.upper().replace("-", ":"),
                "ativo": True
            })
            if hotspot and hotspot.get("local_id"):
                local = locais_coll.find_one({"_id": hotspot["local_id"]})
                if local:
                    nome_local = local.get("nome", nome_local)
        except Exception:
            # não falha o portal por erro de busca
            hotspot = None

    with st.form("form_captive"):
        nome = st.text_input("👤 Nome completo *", placeholder="Ex: Diego Roberto")
        email = st.text_input("📧 E-mail", placeholder="seuemail@provedor.com (opcional)")
        telefone = st.text_input("📱 Telefone", placeholder="(11) 99999-9999 (opcional)")

        termo_texto = (
            "✅ Ao prosseguir, você concorda com o tratamento dos seus dados pessoais pela Tracecom Soluções, "
            "conforme a LGPD (Lei 13.709/2018). Os dados serão usados para autenticação, segurança e comunicações opcionais. "
            "📥 [Ler Política completa](#termos)"
        )

        consentimento = st.checkbox(termo_texto, value=False)
        submitted = st.form_submit_button("📤 Enviar", type="primary")

    if st.session_state.get("mostrar_termos"):
        st.markdown("---")
        st.header("📜 Termos de Uso e Política de Privacidade")

        with st.expander("Política de Privacidade – Tracecom Soluções"):
            st.markdown(""" 
            **1. Introdução**  
            A Tracecom Soluções trata dados pessoais conforme a LGPD.

            **2. Dados coletados**  
            - Nome completo  
            - Telefone, e-mail  
            - IP, MAC, logs de acesso  
            - Informações adicionais de cadastro

            **3. Finalidade**  
            Autenticação Wi-Fi, segurança, estatísticas, contato comercial opcional.

            **4. Seus direitos**  
            Acesso, correção, exclusão, portabilidade.  
            📧 **comercial1@tracecom.net.br**
            """)
        with st.expander("Termos de Uso do Wi-Fi"):
            st.markdown(""" 
            - Acesso temporário à internet.  
            - É proibido uso para atividades ilícitas.  
            - Logs mantidos por 1 ano (Marco Civil).  
            """)
        if st.button("Fechar termos"):
            st.session_state["mostrar_termos"] = False
            st.rerun()

    if submitted:
        if not nome or len(nome.strip()) < 3:
            st.error("❌ Por favor, informe seu nome completo.")
            st.stop()

        if not consentimento:
            st.warning("⚠️ É necessário aceitar os termos.")
            st.stop()

        lead = {
            "nome": nome.strip().title(),
            "email": email.strip() or None,
            "telefone": utils.normalize_phone(telefone) if telefone else None,
            "data_acesso": datetime.utcnow(),
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "client_ip": client_ip,
            "local_id": hotspot.get("local_id") if hotspot else None,
            "consentimento": True,
            "consentimento_timestamp": datetime.utcnow(),
            "modo_acesso": "splash_page"
        }

        try:
            leads_coll.insert_one(lead)
        except Exception:
            st.warning("⚠️ Registro parcial: falha ao salvar no banco.")

        # Envia e-mail opcional
        if lead.get("email"):
            try:
                utils.enviar_email_confirmacao(
                    nome=lead["nome"],
                    email=lead["email"],
                    token="",
                    nome_local=nome_local
                )
            except Exception:
                pass

        st.success(f"🎉 Obrigado, {nome.split()[0]}! Seu acesso está liberado.")
        st.balloons()

        st.markdown(
            """
            <meta http-equiv="refresh" content="3; url=https://tracecom.net.br" />
            <small>Se não for redirecionado, clique aqui.</small>
            """,
            unsafe_allow_html=True
        )
        st.stop()

    if st.button("📜 Ler Termos completos"):
        st.session_state["mostrar_termos"] = True
        st.rerun()
