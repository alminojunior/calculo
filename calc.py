import streamlit as st


preco_filamento = float(st.secrets["FILAMENTO_PRECO"])  # R$/kg
preco_kwh = float(st.secrets["PRECO_KWH"])              # R$/kWh
potencia_media_w = float(st.secrets["POTENCIA_MEDIA_W"]) # W


st.title("💰 Calculadora de Custo de Impressão 3D")

# Entradas do usuário
filamento_g = st.number_input("Quantidade de filamento usada (g)", min_value=0.0, step=0.1)
tempo_input = st.text_input("Duração da impressão (ex.: '2h30' ou '150min')")

# Função para converter tempo
def parse_tempo(tempo_str):
    tempo_str = tempo_str.lower().replace(" ", "")
    horas = minutos = 0
    if "h" in tempo_str:
        partes = tempo_str.split("h")
        horas = int(partes[0]) if partes[0] else 0
        if len(partes) > 1 and "min" in partes[1]:
            minutos = int(partes[1].replace("min", ""))
    elif "min" in tempo_str:
        minutos = int(tempo_str.replace("min", ""))
    else:
        return float(tempo_str)  # assume minutos puros
    return horas + minutos/60

# Cálculo
if tempo_input:
    try:
        horas = parse_tempo(tempo_input)

        custo_filamento = (filamento_g/1000) * preco_filamento
        consumo_kwh = (potencia_media_W * horas) / 1000
        custo_energia = consumo_kwh * preco_kwh
        custo_total = custo_filamento + custo_energia

        st.markdown(f"""
        ### 📊 Resultado
        - **Custo do filamento:** R$ **:blue[{custo_filamento:.2f}]**
        - **Custo da energia:** R$ **:blue[{custo_energia:.2f}]**
        - **Custo total:** 💵 **:green[{custo_total:.2f}]**
        """)
    except Exception as e:
        st.error("Erro ao interpretar o tempo. Use formatos como `2h30` ou `150min`.")
