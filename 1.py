import streamlit as st
from google import genai

API_KEY = "AIzaSyDtocGiEG0AnRP6O5lfS5louLs13bJoBww"

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro ao inicializar o cliente Gemini: {e}")
    st.stop()

SYSTEM_INSTRUCTION = (
    "Você é um chatbot de apoio emocional com o papel de oferecer escuta ativa e suporte imediato "
    "para alunos que enfrentam dificuldades emocionais. "
    "Sua resposta deve ser sempre empática, acolhedora e focar em reconhecer o sentimento do usuário. "
    "Mantenha as respostas breves e encorajadoras. Não substitua um mentor humano; apenas forneça o primeiro acolhimento."
)

st.set_page_config(page_title="Chatbot de Apoio Emocional - Rede de Mentoria", layout="centered")
st.title("Rede de Mentoria Digital: Chatbot de Apoio Emocional")
st.subheader("Simulação de Suporte Imediato por IA")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Diga como você está se sentindo ou qual é a sua dificuldade..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Aguarde, o chatbot está processando..."):
            
            conteudo_conversacao = [
                {"role": "user" if m["role"] == "user" else "model", 
                 "parts": [{"text": m["content"]}]}
                for m in st.session_state.messages
            ]

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=conteudo_conversacao,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                resposta_ia = response.text
                st.markdown(resposta_ia)
                
            except Exception as e:
                resposta_ia = f"Desculpe, houve um erro ao processar sua solicitação: {e}"
                st.error(resposta_ia)

            st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
