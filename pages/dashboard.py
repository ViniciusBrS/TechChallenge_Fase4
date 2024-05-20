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

@st.cache_data
def convert_df(df):
    return df.to_csv(sep=';', decimal=',').encode("utf-8")

### Dataframes
df_petr = get_ipea(1650971490, ['Data', 'Preco_USD'])
df_petr['Dia'] = df_petr['Data'].dt.day
df_petr['Ano'] = df_petr['Data'].dt.year
df_petr['AnoMes'] = df_petr['Data'].dt.year * 100 + df_petr['Data'].dt.month
df_petr['Quarter'] = df_petr['Data'].dt.year * 100 + df_petr['Data'].dt.quarter
df_petr['dif_d_seguinte'] = round((df_petr['Preco_USD'].shift(1) - df_petr['Preco_USD']).fillna(0),2)
lst = [i for i in df_petr['Ano'].unique() if i >= 1990]

df_ano = df_petr.query("Ano >= 1990").groupby(by="Ano").agg({'Preco_USD':['min','max']})

df_media_movel = df_petr.query("Ano >= 1990")
df_media_movel['mediaMovel'] = df_media_movel.sort_values(by="Data")['Preco_USD'].rolling(window=30).mean()


### SIDEBAR
with st.sidebar:
    # st.page_link("app.py", label="Análise", icon='🔍')
    # st.page_link(r"pages\dashboard.py", label="Dashboard", icon='📊')
    # st.page_link(r"pages\modelo.py", label="Previsão de preço", icon='🔮')
    base_dir = os.getcwd()
    path_dash = os.path.join(base_dir, "pages", "dashboard.py")
    path_modelo = os.path.join(base_dir, "pages", "modelo.py")
    st.page_link("app.py", label="Análise", icon='🔍')
    st.page_link(path_dash, label="Dashboard", icon='📊')
    st.page_link(path_modelo, label="Previsão de preço", icon='🔮')
    st.divider()
    ano = st.select_slider("Selecione o ano:", options=lst)
    df_petr_filtro = df_petr.query("Ano == @ano")
    df_petr_filtro_ant = df_petr.query("Ano == @ano - 1")


### PAGINA

media_anual = df_petr_filtro['Preco_USD'].mean()
media_anual_ant = df_petr_filtro_ant['Preco_USD'].mean()
variacao_anual = (1-media_anual_ant/media_anual)*100
col1, col2, col3 = st.columns(3)
col1.metric(f"Média de Preço em {ano}", "$ {}".format(round(media_anual,2)))
col2.metric(f"Média Preço em {ano-1}", "$ {}".format(round(media_anual_ant,2)))
col3.metric("% Variação", "{} %".format(round(variacao_anual,1)))

fig, ax = plt.subplots()
fig.set_size_inches(9, 5, forward=True)

ax.plot(df_ano.index, df_ano['Preco_USD']['min'], color="#ffa600")
ax.plot(df_ano.index, df_ano['Preco_USD']['max'], color="#003f5c")

ax.set(xlabel='Ano', ylabel='Preço (USD)',
       title='Valor mínimo e máximo por ano')

ax.grid(axis='y')
st.pyplot(fig)

st.divider()

fig2, ax2 = plt.subplots()
fig2.set_size_inches(9, 5, forward=True)

ax2.plot(df_media_movel['Data'], df_media_movel['mediaMovel'], color='#16c172')

ax2.set(xlabel='Ano', ylabel='Preço (USD)',
       title='Média movel - 30 dias')
ax2.grid(axis='y')
st.pyplot(fig2)

st.divider()

st.dataframe(df_petr_filtro)
st.download_button(
    label="Download",
    data=convert_df(df_petr_filtro),
    file_name=f"Dataframe_petroleo_{ano}.csv",
    mime="text/csv",
)