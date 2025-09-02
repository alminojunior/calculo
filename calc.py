import streamlit as st
import re

st.title("🖨️ Calculadora de Preço para Impressão 3D")

# Função de cálculo
def calcular_preco_projeto(tempo_horas, filamento_gramas, margem_lucro):
    # Busca os valores configurados nos secrets
    custo_impressora_hora = st.secrets["CUSTO_IMPRESSORA_HORA"]
    custo_filamento_kg = st.secrets["CUSTO_FILAMENTO_KG"]
    custo_energia_hora = st.secrets["CUSTO_ENERGIA_HORA"]

    # Cálculos
    custo_impressora = tempo_horas * custo_impressora_hora
    custo_filamento = (filamento_gramas / 1000) * custo_filamento_kg
    custo_energia = tempo_horas * custo_energia_hora

    custo_total = custo_impressora + custo_filamento + custo_energia
    preco_final = custo_total * (1 + margem_lucro / 100)

    return preco_final, custo_total


# Sidebar - Entrada de dados do usuário
st.sidebar.header("⚙️ Configurações")

# Inputs principais
tempo_horas = st.sidebar.number_input("Tempo de impressão (horas)", value=1.0, min_value=0.1, step=0.5)
filamento_gramas = st.sidebar.number_input("Filamento usado (g)", value=10.0, min_value=1.0, step=1.0)
margem_lucro = st.sidebar.slider("Margem de lucro (%)", min_value=0, max_value=300, value=150, step=5)

# Botão de calcular
if st.sidebar.button("Calcular preço"):
    preco_final, custo_total = calcular_preco_projeto(tempo_horas, filamento_gramas, margem_lucro)

    st.subheader("📊 Resultado")
    st.write(f"💰 **Preço sugerido de venda:** R$ {preco_final:.2f}")
    st.write(f"📉 **Custo total (sem lucro):** R$ {custo_total:.2f}")

# Entrada de G-code para extrair tempo e filamento
st.subheader("📂 Upload do G-code (opcional)")
arquivo = st.file_uploader("Carregue um arquivo .gcode para calcular automaticamente", type=["gcode"])

if arquivo is not None:
    conteudo = arquivo.read().decode("utf-8")

    # Extrair tempo total em minutos
    match_tempo = re.search(r";TIME_ELAPSED:(\d+)", conteudo)
    tempo_horas_auto = int(match_tempo.group(1)) / 3600 if match_tempo else None

    # Extrair filamento total em mm (se disponível)
    match_filamento = re.search(r";Filament used: ([\d\.]+)m", conteudo)
    filamento_metros = float(match_filamento.group(1)) if match_filamento else None
    filamento_gramas_auto = filamento_metros * 1.24 if filamento_metros else None  # 1m ≈ 1.24g PLA

    if tempo_horas_auto and filamento_gramas_auto:
        preco_final_auto, custo_total_auto = calcular_preco_projeto(
            tempo_horas_auto, filamento_gramas_auto, margem_lucro
        )

        st.success("✅ Dados extraídos do G-code!")
        st.write(f"⏱️ Tempo: {tempo_horas_auto:.2f} horas")
        st.write(f"🧵 Filamento: {filamento_gramas_auto:.2f} g")
        st.write(f"💰 **Preço sugerido:** R$ {preco_final_auto:.2f}")
        st.write(f"📉 **Custo total:** R$ {custo_total_auto:.2f}")
    else:
        st.error("Não foi possível extrair tempo e filamento do G-code.")
