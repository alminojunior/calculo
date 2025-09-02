import streamlit as st
import re
import csv
from pathlib import Path

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
                "Preço de Impressão", "Link MakerWorld"
            ])
        writer.writerow([nome, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link])
    
    st.success("✅ Projeto salvo no CSV com sucesso!")

# ---------------- Sidebar ---------------- #
st.sidebar.header("⚙️ Configurações do Projeto")

nome_projeto = st.sidebar.text_input("Nome do projeto")
arquivo = st.sidebar.file_uploader("📂 Upload do G-code", type=["gcode"])

# ---------------- Página principal ---------------- #
st.subheader("📊 Insira os dados manualmente")

tempo_horas = st.number_input("⏱️ Tempo de impressão (horas)", value=1.0, min_value=0.1, step=0.5)
filamento_gramas = st.number_input("🧵 Filamento usado (g)", value=10.0, min_value=1.0, step=1.0)
link_makerworld = st.text_input("🔗 Link do projeto no MakerWorld")

if st.button("Calcular custos"):
    custo_impressora, custo_filamento, custo_energia, preco_impressao = calcular_custos(tempo_horas, filamento_gramas)

    st.markdown(f"<p style='font-size:18px;'>🖨️ Custo da impressora: R$ {custo_impressora:.2f}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>🧵 Custo do filamento: R$ {custo_filamento:.2f}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>⚡ Custo de energia: R$ {custo_energia:.2f}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:22px; font-weight:bold;'>💰 Preço de impressão R$ {preco_impressao:.2f}</p>", unsafe_allow_html=True)

    if link_makerworld:
        st.markdown(f"<p style='font-size:16px;'>🔗 Link do projeto: <a href='{link_makerworld}' target='_blank'>{link_makerworld}</a></p>", unsafe_allow_html=True)

    salvar_no_csv(nome_projeto, tempo_horas, filamento_gramas, custo_impressora, custo_filamento, custo_energia, preco_impressao, link_makerworld)

# ---------------- Processamento do G-code ---------------- #
if arquivo is not None:
    conteudo = arquivo.read().decode("utf-8")

    match_tempo = re.search(r";TIME_ELAPSED:(\d+)", conteudo)
    tempo_horas_auto = int(match_tempo.group(1)) / 3600 if match_tempo else None

    match_filamento = re.search(r";Filament used: ([\d\.]+)m", conteudo)
    filamento_metros = float(match_filamento.group(1)) if match_filamento else None
    filamento_gramas_auto = filamento_metros * 1.24 if filamento_metros else None

    if tempo_horas_auto and filamento_gramas_auto:
        custo_impressora, custo_filamento, custo_energia, preco_impressao = calcular_custos(tempo_horas_auto, filamento_gramas_auto)

        st.success("✅ Dados extraídos do G-code!")
        st.subheader("📊 Custos extraídos automaticamente")
        st.markdown(f"<p style='font-size:18px;'>⏱️ Tempo de impressão: {tempo_horas_auto:.2f} horas</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px;'>🧵 Quantidade de filamento: {filamento_gramas_auto:.2f} g</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px;'>🖨️ Custo da impressora: R$ {custo_impressora:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px;'>🧵 Custo do filamento: R$ {custo_filamento:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px;'>⚡ Custo de energia: R$ {custo_energia:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:22px; font-weight:bold;'>💰 Preço de impressão R$ {preco_impressao:.2f}</p>", unsafe_allow_html=True)

        if link_makerworld:
            st.markdown(f"<p style='font-size:16px;'>🔗 Link do projeto: <a href='{link_makerworld}' target='_blank'>{link_makerworld}</a></p>", unsafe_allow_html=True)

        salvar_no_csv(nome_projeto, tempo_horas_auto, filamento_gramas_auto, custo_impressora, custo_filamento, custo_energia, preco_impressao, link_makerworld)
    else:
        st.error("❌ Não foi possível extrair tempo e filamento do G-code.")