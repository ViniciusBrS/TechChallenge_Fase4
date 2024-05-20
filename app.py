import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

#Capturar dados do petróleo Brent - Ipea
def get_ipea(code, cols=None):
    v_tabelas = pd.read_html(f'http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid={code}&oper=view', thousands='.', decimal=',', header=0, encoding='UTF-8')
    df = v_tabelas[2]
    if cols is not None:
        df.columns = cols
        df[cols[0]] = pd.to_datetime(df[cols[0]], dayfirst=True)
    return df

df_petr = get_ipea(1650971490, ['Data', 'Preco_USD'])
df_petr['Dia'] = df_petr['Data'].dt.day
df_petr['Ano'] = df_petr['Data'].dt.year
df_petr['AnoMes'] = df_petr['Data'].dt.year * 100 + df_petr['Data'].dt.month
df_petr['Quarter'] = df_petr['Data'].dt.year * 100 + df_petr['Data'].dt.quarter
df_petr['dif_d_seguinte'] = round((df_petr['Preco_USD'].shift(1) - df_petr['Preco_USD']).fillna(0),2)

#filtros do periodo da pandemia
df_pand_ant_20 = df_petr.query("AnoMes < 202001") #historico antes de 2020
df_pand_19_20 = df_petr.query("AnoMes >= 201901 and AnoMes <= 202012") #2019 e 2020
df_pand_20 = df_petr.query("AnoMes >= 202001 and AnoMes <= 202012") #apenas 2020

v_menor_valor = df_pand_20['Preco_USD'].min() #menor valor durante 2020
v_menor_valor_hist = df_pand_ant_20['Preco_USD'].min() #menor valor periodo completo antes de 20

v_media_19 = df_pand_19_20.query("AnoMes < 202001")['Preco_USD'].mean() #media do valor em 19
v_menor_diff = round(v_menor_valor / v_media_19 * 100,2)

#filtro guerra da ucrania
df_guerra = df_petr.query("AnoMes >= 202101 and AnoMes <= 202212")

### PAGINA PRINCIPAL

st.markdown("# Análise Petróleo Brent")
st.markdown("Petróleo é um combustível fóssil, considerado um dos principais recursos naturais utilizados como fonte de energia da atualidade.")
st.markdown("O petróleo, apesar de já ser conhecido anteriormente, passou a ser explorado em meados do século XIX e utilizado em larga escala a partir da criação dos motores movidos a gasolina ou a óleo diesel.")
st.markdown("Na década de 70, o petróleo representava o carro chefe da economia, correspondendo a quase 50% do consumo mundial de energia e mesmo que atualmente seu uso esteja dando lugar a fontes alternativas de energia, ainda é uma das fontes de energia mais utilizadas no mundo. [¹](https://brasilescola.uol.com.br/geografia/petroleo.htm)")
st.markdown("Para a precificação do petróleo, a referência global é o Brent, essa precificação é influenciada por diversos de fatores, desde a geopolítica internacional até (como qualquer commodity) leis da oferta e demanda ")
st.markdown("Abaixo podemos analisar os impactos no preço do petróleo causados pela pandemia da Covid-19 e pela guerra da Russia e Ucrânia ")

tab1, tab2 = st.tabs(["Pandemia - COVID 19", "Guerra - Russia x Ucrânia"])

with tab1:
    st.write("A pandemia de COVID-19 provocou uma queda brusca na demanda global por petróleo, por conta dos lockdowns que foram se instaurando nos países atingidos, o consumo da commotidy foi severamente impactado.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Menor valor histórico (Dez/1998)", "$ {}".format(round(v_menor_valor_hist,2)))
    col2.metric("Menor valor durante a pandemia (Abril/2020)", "$ {}".format(round(v_menor_valor,2)))
    col3.metric("Valor médio em 2019", "$ {}".format(round(v_media_19,2)))
    tab1.write("Durante a pandemia tivemos o segundo menor valor de cotação do Brent desde o início dos registros em 1987, além de uma queda de 85,6% em relação a média do ano anterior.")
    plt.ylim(bottom=0)
    fig, ax = plt.subplots()
    fig.set_size_inches(9, 5, forward=True)
    ax.plot(df_pand_19_20['Data'], df_pand_19_20['Preco_USD'])
    ax.set(xlabel='Data', ylabel='Preço (USD)', title='Preço do Petróleo Brent - Jan/19 à Dez/20')
    ax.grid(axis='y')
    st.pyplot(fig)

with tab2:
    st.write("No contexto Geopolitico, a guerra entre Rússia e Ucrânia é um bom exemplo recente de como questões políticas podem impactar diretamente no preço do petróleo.")
    st.write("As tensões entre os países já aconteciam desde meados de 2014, mas em Fevereiro de 2022 a Rússia iniciou as invasões ao território ucraniano.")
    st.write("Como represália as ações da Russia, os países do ocidente aplicaram sanções econômicas que impactaram diretamente o preço do petróleo, pois a Russia na época era o segundo maior produtor de petróleo do mundo.")
    fig2, ax2 = plt.subplots()
    fig2.set_size_inches(9, 5, forward=True)
    ax2.plot(df_guerra['Data'], df_guerra['Preco_USD'])
    ax2.set(xlabel='Data', ylabel='Preço (USD)',
        title='Preço do Petróleo Brent - Jan/21 à Dez/22')
    ax2.grid(axis='y')
    st.pyplot(fig2)
    st.write("""No primeiro semestre de 2021, é possível observar um movimento de recuperação do preço em razão do aumento do consumo devido ao inicio do fim da pandemia,
                porém em fevereiro os preços começaram a disparar, chegando a 133 doláres em março por conta da invasão russa.""")



### SIDEBAR
# with st.sidebar:
#     st.page_link("app.py", label="Análise", icon='🔍')
#     st.page_link(r"pages\dashboard.py", label="Dashboard", icon='📊')
#     st.page_link(r"pages\modelo.py", label="Previsão de preço", icon='🔮')
base_dir = os.getcwd()
path_dash = os.path.join(base_dir, "pages", "dashboard.py")
path_modelo = os.path.join(base_dir, "pages", "modelo.py")
with st.sidebar:
    st.page_link("app.py", label="Análise", icon='🔍')
    st.page_link(path_dash, label="Dashboard", icon='📊')
    st.page_link(path_modelo, label="Previsão de preço", icon='🔮')