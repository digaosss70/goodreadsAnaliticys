import streamlit as st
from extract import getAll

st.title('Extrair e Salvar dados do Goodreads')

if st.button('extrair'):
    with st.spinner('Extraindo...'):
        logs = getAll()
        # Exibe os logs no Streamlit
        #for log in logs:
        st.write(logs)
