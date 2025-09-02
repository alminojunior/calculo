import streamlit as st
import re
import csv
from pathlib import Path

st.title("🖨️ Calculadora de Custos de Impressão 3D")

CSV_FILE = "projetos_3d.csv"
csv_path = Path(CSV_FILE)

# Função de cálculo
def calcular_custos(tempo_horas, filamento_gramas):
    custo_impressora_hora = st.secrets["CUSTO_IMPRESSORA_HORA"]
    custo_filamento_kg = st.secrets["CUSTO_FILAMENTO_KG"]
    custo_energia_hora = st.secrets["CUSTO_ENERGIA_HORA"]
    margem_lucro = st.secrets["MARGEM_LUCRO"]

    # Custos individuais
    custo_impressora = tempo_horas * custo_impressora_hora
    custo_filamento = (filamento_gramas / 1000) * custo_filamento_kg
    custo_energia = tempo_horas * custo_energia_hora

    # Preço final
    preco_impressao = (custo_impressora + custo_filamento + custo_energia) * (1 + margem_lucro / 100)

    return custo_impressora, custo_filamento, custo_energia, preco_impressao

# Função para salvar no CSV
def salvar_no_csv(nome, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link):
    file_exists = csv_path.exists()
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        if not file_exists:
            writer.writerow(["Projeto", "Tempo (h)", "Filamento (g)", "Custo Impressora", "Custo Filamento", "Custo Energia", "Preço de Impressão", "Link MakerWorld"])
        writer.writerow([nome, tempo, filamento, custo_impressora, custo_filamento, custo_energia, preco, link])
    
    st.success("✅ Projeto salvo no CSV com sucesso!")

# Sidebar - Entrada de dados
st.sidebar.header("⚙️ Configurações")

tempo_horas = st.sidebar.number_input("Tempo de impressão (horas)", value=1.0, min_value=0.1, step=0.5)
filamento_gramas = st.sidebar.number_input("Filamento usado (g)", value=10.0, min_value=1.0, step=1.0)
nome_projeto = st.sidebar.text_input("Nome do projeto")
link_makerworld = st.sidebar.text_input("🔗 Link do projeto no MakerWorld")

# Botão de calcular
if st.sidebar.button("Calcular custos"):
    custo_impressora, custo_filamento, custo_energia, preco_impressao = calcular_custos(tempo_horas, filamento_gramas)

    st.subheader("📊 Detalhamento dos Custos")
    st.write(f"🖨️ **Custo da impressora:** R$ {custo_impressora:.2f}")
    st.write(f"🧵 **Custo do filamento:** R$ {custo_filamento:.2f}")
    st.write(f"⚡ **Custo de energia:** R$ {custo_energia:.2f}")
    st.markdown(f"💰 **Preço de impressão (com margem): R$ {preco_impressao:.2f}**")

    if link_makerworld:
        st.write(f"🔗 **Link do projeto:** {link_makerworld}")

    # Salvar no CSV
    salvar_no_csv(nome_projeto, tempo_horas, filamento_gramas, custo_impressora, custo_filamento, custo_energia, preco_impressao, link_makerworld)

# Entrada de G-code (opcional)
st.subheader("📂 Upload do G-code (opcional)")
arquivo = st.file_uploader("Carregue um arquivo .gcode para calcular automaticamente", type=["gcode"])

if arquivo is not None:
    conteudo = arquivo.read().decode("utf-8")
    match_tempo = re.search(r";TIME_ELAPSED:(\d+)", conteudo)
    tempo_horas_auto = int(match_tempo.group(1)) / 3600 if match_tempo else None
    match_filamento = re.search(r";Filament used: ([\d\.]+)m", conteudo)
    filamento_metros = float(match_filamento.group(1)) if match_filamento else None
    filamento_gramas_auto = filamento_metros * 1.24 if filamento_metros else None

    if tempo_horas_auto and filamento_gramas_auto:
        custo_impressora, custo_filamento, custo_energia, preco_impressao = calcular_custos(
            tempo_horas_auto, filamento_gramas_auto
        )

        st.success("✅ Dados extraídos do G-code!")
        st.subheader("📊 Detalhamento dos Custos")
        st.write(f"🖨️ **Custo da impressora:** R$ {custo_impressora:.2f}")
        st.write(f"🧵 **Custo do filamento:** R$ {custo_filamento:.2f}")
        st.write(f"⚡ **Custo de energia:** R$ {custo_energia:.2f}")
        st.markdown(f"💰 **Preço de impressão (com margem): R$ {preco_impressao:.2f}**")

        if link_makerworld:
            st.write(f"🔗 **Link do projeto:** {link_makerworld}")

        # Salvar no CSV
        salvar_no_csv(nome_projeto, tempo_horas_auto, filamento_gramas_auto, custo_impressora, custo_filamento, custo_energia, preco_impressao, link_makerworld)
    else:
        st.error("Não foi possível extrair tempo e filamento do G-code.")
