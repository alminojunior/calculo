import streamlit as st
import re
import csv
from pathlib import Path
import urllib.parse
import webbrowser

# Configuração da página
st.set_page_config(page_title="Calculadora para Impressão 3D", layout="centered")
st.title("🖨️ Calculadora para Impressão 3D")

CSV_FILE = "projetos_3d.csv"
csv_path = Path(CSV_FILE)

# ---------------- Função de cálculo ---------------- #
def calcular_custos(tempo_horas, filamento_gramas):
    custo_impressora_hora = st.secrets["CUSTO_IMPRESSORA_HORA"]
    custo_filamento_kg = st.secrets["CUSTO_FILAMENTO_KG"]
    custo_energia_hora = st.secrets["CUSTO_ENERGIA_HORA"]
    margem_lucro = st.secrets["MARGEM_LUCRO"]

    custo_impressora = tempo_horas * custo_impressora_hora
    custo_filamento = (filamento_gramas / 1000) * custo_filamento_kg
    custo_energia = tempo_horas * custo_energia_hora

    preco_impressao = (custo_impressora + custo_filamento + custo_energia) * (1 + margem_lucro / 100)

    return custo_impressora, custo_filamento, custo_energia, preco_impressao

# ---------------- Função para salvar CSV ---------------- #
def salvar_no_csv(nome, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link):
    file_exists = csv_path.exists()
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        if not file_exists:
            writer.writerow([
                "Projeto", "Tempo (h)", "Filamento (g)", 
                "Custo Impressora", "Custo Filamento", "Custo Energia", 
                "Preço Final", "Link MakerWorld"
            ])
        writer.writerow([nome, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link])

# ---------------- Sidebar: entradas ---------------- #
st.sidebar.header("Configurações da Impressão")
nome_projeto = st.sidebar.text_input("Nome do Projeto")
tempo = st.sidebar.number_input("Tempo de impressão (horas)", min_value=0.0, step=0.5)
filamento = st.sidebar.number_input("Quantidade de filamento (g)", min_value=0.0, step=1.0)

# ---------------- Página Principal ---------------- #
link_makerworld = st.text_input("🔗 Link do projeto no MakerWorld (opcional)")

if st.sidebar.button("Calcular"):
    custo_impressora, custo_filamento, custo_energia, preco = calcular_custos(tempo, filamento)

    st.subheader("📊 Detalhamento dos Custos")
    st.write(f"🕒 Tempo de impressão: **{tempo:.2f} h**")
    st.write(f"🧵 Filamento usado: **{filamento:.2f} g**")
    st.write(f"💰 Custo da impressora: R$ {custo_impressora:.2f}")
    st.write(f"🎨 Custo do filamento: R$ {custo_filamento:.2f}")
    st.write(f"⚡ Custo de energia: R$ {custo_energia:.2f}")
    st.markdown(f"### 💵 Preço de impressão: **R$ {preco:.2f}**")

    # Salva no CSV
    salvar_no_csv(nome_projeto, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link_makerworld)

    # ---------------- Botão WhatsApp ---------------- #
    resumo = f"""Solicitação de Impressão 3D
📌 Projeto: {nome_projeto if nome_projeto else "Não informado"}
🔗 Link: {link_makerworld if link_makerworld else "Não informado"}
🕒 Tempo: {tempo:.2f} h
🧵 Filamento: {filamento:.2f} g
💵 Valor: R$ {preco:.2f}"""

    mensagem = urllib.parse.quote(resumo)
    whatsapp_url = f"https://wa.me/5592981246146?text={mensagem}"

    if st.button("📲 Solicitar Impressão"):
        js = f"window.open('{whatsapp_url}')"  # abre em nova aba
        st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)