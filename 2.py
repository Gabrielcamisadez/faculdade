import streamlit as st
from google import genai
import time

# Chave de API
API_KEY = "AIzaSyDtocGiEG0AnRP6O5lfS5louLs13bJoBww"

# Inicializa o cliente Gemini
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro ao inicializar o cliente Gemini: {e}")
    st.stop()

# --- Funções do Chatbot/IA ---

def gerar_perfil_mentor_ia(objetivo, dificuldade):
    """Gera um perfil fictício de mentor e sua instrução de sistema."""
    
    prompt = (
        f"Com base no objetivo do aluno ('{objetivo}') e dificuldade ('{dificuldade}'), "
        "gere um nome fictício, uma área de especialidade e uma breve biografia para um mentor ideal. "
        "Formate a resposta estritamente da seguinte maneira: \n\n"
        "NOME: [Nome Fictício, use apenas o primeiro nome e sobrenome]\n"
        "ESPECIALIDADE: [Área Fictícia, ex: Matemática e Gestão de Ansiedade]\n"
        "BIO: [Breve descrição de 3 linhas sobre a experiência do mentor]\n\n"
        "Em seguida, gere a INSTRUÇÃO DE SISTEMA que este mentor deve seguir em um chat, "
        "dando ênfase à empatia e ao acompanhamento. "
        "Comece a instrução com: INSTRUÇÃO DO CHAT: Você é [Nome do Mentor]. Sua especialidade é [Especialidade]. Você deve guiar o aluno em seus desafios de [Dificuldade do Aluno] com empatia e foco no objetivo [Objetivo do Aluno]."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Erro ao gerar perfil: {e}"

def obter_resposta_mentor_simulado(perfil_e_instrucao, mensagem_aluno):
    """Chama a IA para atuar como o mentor simulado, mantendo a conversa."""
    
    partes = perfil_e_instrucao.split("INSTRUÇÃO DO CHAT:")
    if len(partes) < 2:
        return "Erro de formato na instrução do mentor. Tente novamente.", None
        
    instrucao_mentor = partes[1].strip()
    
    # Formata a conversa histórica para manter o contexto
    conteudo_conversacao = [
        {"role": "user" if m["role"] == "user" else "model", 
         "parts": [{"text": m["content"]}]}
        for m in st.session_state.mentor_messages
    ]

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_conversacao,
            config=genai.types.GenerateContentConfig(
                system_instruction=instrucao_mentor
            )
        )
        return response.text, instrucao_mentor
    except Exception as e:
        return f"Desculpe, houve um erro: {e}", instrucao_mentor

# --- Configuração de Páginas ---

st.set_page_config(page_title="Rede de Mentoria Digital", layout="centered")

def tela_login_e_perfil():
    st.title("Rede de Mentoria Digital 🤝")
    st.subheader("Inclusão Socioemocional e Aprendizagem")
    st.write("Bem-vindo(a)! Escolha seu perfil para iniciar o acolhimento.")
    
    col1, col2 = st.columns(2)
    
    if col1.button("Sou Aluno(a)", use_container_width=True):
        st.session_state.page = 'formulario'
        st.rerun()

    if col2.button("Sou Mentor(a) Voluntário(a)", use_container_width=True, disabled=True):
        st.info("Funcionalidade de cadastro de mentor indisponível no protótipo básico.")

def tela_formulario():
    st.title("Qual a sua necessidade?")
    st.write("Para encontrarmos o mentor ideal, precisamos entender seus objetivos e desafios.")

    # Inicializa keys se não existirem
    if "objetivo" not in st.session_state: st.session_state.objetivo = ""
    if "dificuldade" not in st.session_state: st.session_state.dificuldade = ""

    with st.form("form_aluno"):
        objetivo_input = st.text_input("1. Qual seu objetivo principal agora? (Ex: Melhorar notas, Lidar com a ansiedade)", value=st.session_state.objetivo)
        dificuldade_input = st.text_area("2. Descreva sua dificuldade emocional ou de aprendizado. (Ex: Sinto muita pressão, não consigo me concentrar)", value=st.session_state.dificuldade)
        
        submitted = st.form_submit_button("Buscar Meu Mentor Ideal (IA)")
        
        if submitted:
            if objetivo_input and dificuldade_input:
                st.session_state.objetivo = objetivo_input
                st.session_state.dificuldade = dificuldade_input
                st.session_state.page = 'pareamento'
                st.rerun()
            else:
                st.error("Por favor, preencha ambos os campos.")

def tela_pareamento():
    st.title("Processando Pareamento Inteligente... 🤖")
    st.info("A IA está usando Machine Learning para encontrar a melhor compatibilidade para você!")

    if "perfil_mentor_simulado" not in st.session_state:
        # Tenta gerar o perfil se ainda não foi gerado
        with st.spinner("Conectando com a IA para encontrar seu mentor..."):
            st.session_state.perfil_mentor_simulado = gerar_perfil_mentor_ia(
                st.session_state.objetivo,
                st.session_state.dificuldade
            )

    perfil = st.session_state.perfil_mentor_simulado
    
    # Check 1: Erro de API (ex: chave inválida ou problema de conexão)
    if "Erro ao gerar perfil:" in perfil:
        st.error(f"Falha na conexão com a IA: {perfil}")
        st.button("Voltar e Tentar Novamente", on_click=lambda: st.session_state.update(page='formulario', perfil_mentor_simulado=None), key="voltar_err_api")
        return
    
    # Check 2: Erro de Parsing (IA não seguiu o formato estrito)
    if "INSTRUÇÃO DO CHAT:" not in perfil:
        st.error("A IA não conseguiu gerar o perfil no formato correto. Tente novamente.")
        st.code(f"Resposta bruta da IA: {perfil}")
        st.button("Voltar e Tentar Novamente", on_click=lambda: st.session_state.update(page='formulario', perfil_mentor_simulado=None), key="voltar_err_parse")
        return
    
    # Se chegou aqui, o perfil é válido
    st.success("Pareamento concluído com sucesso!")
    st.header("Seu Mentor Recomendado")

    # Exibe o perfil gerado pela IA
    perfil_formatado = perfil.split("INSTRUÇÃO DO CHAT:")[0].strip()
    st.markdown(f"**{perfil_formatado}**")
    
    # Extração do nome para a mensagem inicial do chat
    perfil_partes = perfil.split("NOME: ")
    nome_mentor = perfil_partes[1].splitlines()[0].strip() if len(perfil_partes) > 1 else "Meu Mentor"

    if st.button("Iniciar Chat Seguro com o Mentor", use_container_width=True):
        st.session_state.page = 'chat'
        # Inicializa o chat com a primeira mensagem do mentor simulado
        st.session_state.mentor_messages = [{"role": "model", "content": f"Olá! Sou {nome_mentor}, seu mentor. Recebi seu formulário. Estou aqui para te dar suporte emocional e acompanhar seu progresso. Conte-me mais sobre o que te incomoda, ou como podemos começar!"}]
        st.rerun()

    st.button("Tentar Novamente", on_click=lambda: st.session_state.update(page='formulario', perfil_mentor_simulado=None), key="tentar_nov")
    
def tela_chat():
    st.title("Chat Seguro - Mentor ")
    st.caption("oferecendo suporte emocional e acompanhamento.")

    if "mentor_messages" not in st.session_state:
         st.session_state.mentor_messages = []

    for message in st.session_state.mentor_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Envie uma mensagem para seu mentor..."):
        st.session_state.mentor_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("model"):
            with st.spinner("O Mentor está digitando..."):
                
                resposta_mentor, instrucao = obter_resposta_mentor_simulado(
                    st.session_state.perfil_mentor_simulado, prompt
                )
                
                if "Erro" in resposta_mentor:
                    st.error(resposta_mentor)
                else:
                    st.markdown(resposta_mentor)
                    st.session_state.mentor_messages.append({"role": "model", "content": resposta_mentor})

    if st.button("Ver Painel de Progresso", key="ir_progresso"):
        st.session_state.page = 'progresso'
        st.rerun()

def tela_progresso():
    st.title("Painel de Progresso e Apoio ✨")
    st.subheader("Acompanhamento")
    
    st.markdown("**Status do seu Acolhimento Socioemocional**:")
    
    if "objetivo" in st.session_state:
        st.progress(70, text=f"Progresso em '{st.session_state.objetivo}': 70% Concluído")
        st.write("Seu mentor revisará este painel semanalmente para definir os próximos passos.")
    else:
        st.info("Preencha o formulário para ver o progresso simulado.")

    st.markdown("---")
    st.subheader("Comunidade de Apoio")
    st.info("Criação de uma Rede Colaborativa: Este espaço em breve permitirá que você interaja com outros alunos e mentores de forma anônima.")
    st.markdown("*Recurso indisponível na versão protótipo.*")

    if st.button("Voltar ao Login"):
        # Limpa o estado da sessão ao sair para começar do zero
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = 'login'
        st.rerun()

# --- Controle de Navegação Principal ---

if 'page' not in st.session_state:
    st.session_state.page = 'login'

if st.session_state.page == 'login':
    tela_login_e_perfil()
elif st.session_state.page == 'formulario':
    tela_formulario()
elif st.session_state.page == 'pareamento':
    tela_pareamento()
elif st.session_state.page == 'chat':
    tela_chat()
elif st.session_state.page == 'progresso':
    tela_progresso()
