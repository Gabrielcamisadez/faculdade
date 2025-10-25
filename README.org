#+title: chat emocional faculdade

* Setup
Criar o ambiente virtual do python ->
: python3 -m venv venv

ATivar o ambiente ->
: source venv/bin/activate

Windows tem q ver qual é que ativa mesmo ->
: venv\Scripts\Activate.ps1
: venv\Scripts\activate.bat
: venv\Scrips\activate.ps1

Instalar as duas unicas dependencias ->
: pip install google-genai streamlit

* Run
Após o simples setup, rodar a aplicação do chatbot com o streamli ->
: streamlit run 2.py

#+begin_src sh
(venv) [15:42][]~/daily/university/chat ✮ streamlit run 2.py

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://172.16.60.21:8501
#+end_src

