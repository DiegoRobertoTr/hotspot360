import streamlit as st

# Título do app
st.title("Meu Primeiro App no Streamlit Cloud")

# Texto inicial
st.write("Bem-vindo ao seu app Streamlit! 🚀")

# Exemplo de entrada de texto
nome = st.text_input("Digite seu nome:")

# Exemplo de interação
if nome:
    st.success(f"Olá, {nome}! Seu app está funcionando perfeitamente.")

# Exemplo de botão
if st.button("Clique aqui"):
    st.info("Você clicou no botão!")
