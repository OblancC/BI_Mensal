import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
import pandas_gbq

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Arrecadação Federal · RFB",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bitter:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background: #faf9f7;
    color: #1a1a1a;
}
.block-container {
    padding: 2.5rem 3rem 3rem 3rem;
    max-width: 1400px;
}

/* cabeçalho editorial */
.page-header {
    border-top: 3px solid #1a1a1a;
    border-bottom: 1px solid #d0cdc8;
    padding: 18px 0 14px 0;
    margin-bottom: 32px;
}
.page-header .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 4px;
}
.page-header h1 {
    font-family: 'Bitter', serif;
    font-size: 2rem;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.15;
    margin: 0;
}
.page-header .subtitle {
    font-size: 0.9rem;
    color: #666;
    margin-top: 6px;
    font-weight: 300;
}

/* KPI */
.kpi-wrap {
    border-top: 2px solid #1a1a1a;
    padding: 14px 0 10px 0;
}
.kpi-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 2px;
}
.kpi-number {
    font-family: 'Bitter', serif;
    font-size: 2.1rem;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1;
}
.kpi-note { font-size: 0.75rem; color: #888; margin-top: 3px; }
.kpi-up   { color: #2d6a4f; }
.kpi-down { color: #9b2226; }

/* seções */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #aaa;
    border-bottom: 1px solid #e5e2dd;
    padding-bottom: 5px;
    margin-bottom: 4px;
    margin-top: 28px;
}
.chart-title {
    font-family: 'Bitter', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 2px;
}
.chart-desc {
    font-size: 0.78rem;
    color: #888;
    margin-bottom: 10px;
    font-weight: 300;
}

/* storytelling */
.finding {
    border-top: 1px solid #d0cdc8;
    padding: 16px 0;
}
.finding-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #bbb;
    margin-bottom: 4px;
}
.finding-title {
    font-family: 'Bitter', serif;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 5px;
    color: #1a1a1a;
}
.finding-body {
    font-size: 0.82rem;
    color: #555;
    line-height: 1.75;
    font-weight: 300;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #f2f0ed;
    border-right: 1px solid #d0cdc8;
}
section[data-testid="stSidebar"] * { color: #1a1a1a !important; }

.footer {
    border-top: 1px solid #d0cdc8;
    margin-top: 48px;
    padding-top: 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #bbb;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DADOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Consultando BigQuery...")
def load_data():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    query = """
        SELECT
            f.valor,
            t.ano, t.mes, t.nome_mes, t.trimestre, t.semestre,
            l.sigla_uf, l.nome_uf, l.regiao,
            tr.BK_Tributo, tr.descricao, tr.categoria
        FROM `mensal-arrecadacao-receita.dw_arrecadacao.fato_arrecadacao` f
        JOIN `mensal-arrecadacao-receita.dw_arrecadacao.dim_tempo`      t  ON f.SK_Tempo      = t.SK_Tempo
        JOIN `mensal-arrecadacao-receita.dw_arrecadacao.dim_localidade` l  ON f.SK_Localidade = l.SK_Localidade
        JOIN `mensal-arrecadacao-receita.dw_arrecadacao.dim_tributo`    tr ON f.SK_Tributo    = tr.SK_Tributo
        WHERE f.valor IS NOT NULL AND f.valor > 0
    """
    df = pandas_gbq.read_gbq(
    query,
    credentials=credentials,
    project_id="mensal-arrecadacao-receita",
    location="southamerica-east1"  # região São Paulo
)
    df['valor_B'] = df['valor'] / 1e9
    return df

df_raw = load_data()

NOMES_MES = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
             7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Arrecadação Federal")
    st.caption("Receita Federal do Brasil · Base dos Dados")
    st.divider()

    anos_disp = sorted(df_raw['ano'].unique())
    st.markdown("**Período**")
    ano_min, ano_max = st.select_slider(
        " ", options=anos_disp,
        value=(min(anos_disp), max(anos_disp))
    )

    st.markdown("**Região**")
    regioes = ["Todas"] + sorted(df_raw['regiao'].dropna().unique().tolist())
    regiao_sel = st.selectbox(" ", regioes, key="reg")

    st.markdown("**Tributo**")
    tributos = ["Todos"] + sorted(df_raw['descricao'].unique().tolist())
    tributo_sel = st.selectbox(" ", tributos, key="trib")

    st.divider()
    st.caption(f"Dados de {min(anos_disp)} a {max(anos_disp)}")


# ─────────────────────────────────────────────
# FILTRO
# ─────────────────────────────────────────────
df = df_raw[df_raw['ano'].between(ano_min, ano_max)].copy()
if regiao_sel  != "Todas": df = df[df['regiao']    == regiao_sel]
if tributo_sel != "Todos": df = df[df['descricao'] == tributo_sel]


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="eyebrow">Ministério da Fazenda · Receita Federal do Brasil</div>
    <h1>Resultado da Arrecadação Federal</h1>
    <div class="subtitle">
        Análise tributária · {ano_min}–{ano_max}
        {'· ' + regiao_sel if regiao_sel != 'Todas' else ''}
        {'· ' + tributo_sel if tributo_sel != 'Todos' else ''}
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
anos_kpi = sorted(df['ano'].unique())
total    = df['valor'].sum()

yoy = 0
if len(anos_kpi) >= 2:
    v_atual = df[df['ano'] == anos_kpi[-1]]['valor'].sum()
    v_ant   = df[df['ano'] == anos_kpi[-2]]['valor'].sum()
    yoy = ((v_atual / v_ant) - 1) * 100 if v_ant > 0 else 0

uf_shares = df.groupby('sigla_uf')['valor'].sum()
uf_lider  = uf_shares.idxmax()
uf_share  = uf_shares.max() / df['valor'].sum() * 100

vol      = df.groupby('descricao')['valor'].std() / df.groupby('descricao')['valor'].mean()
trib_vol = vol.idxmax() if not vol.empty else "—"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-wrap">
        <div class="kpi-eyebrow">Arrecadação total</div>
        <div class="kpi-number">R$ {total/1e12:.2f}T</div>
        <div class="kpi-note">{ano_min} a {ano_max}</div>
    </div>""", unsafe_allow_html=True)

with k2:
    cls  = "kpi-up" if yoy >= 0 else "kpi-down"
    seta = "↑" if yoy >= 0 else "↓"
    ref  = f"{anos_kpi[-2]}→{anos_kpi[-1]}" if len(anos_kpi) >= 2 else "—"
    st.markdown(f"""
    <div class="kpi-wrap">
        <div class="kpi-eyebrow">Crescimento anual</div>
        <div class="kpi-number {cls}">{seta} {abs(yoy):.1f}%</div>
        <div class="kpi-note">{ref}</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-wrap">
        <div class="kpi-eyebrow">Estado líder</div>
        <div class="kpi-number">{uf_lider}</div>
        <div class="kpi-note">{uf_share:.1f}% do total nacional</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-wrap">
        <div class="kpi-eyebrow">Maior volatilidade</div>
        <div class="kpi-number" style="font-size:1.1rem;padding-top:10px">{trib_vol}</div>
        <div class="kpi-note">coef. de variação mais alto</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TEMA PLOTLY
# ─────────────────────────────────────────────
PT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#666', family='Source Sans 3, sans-serif', size=11),
    xaxis=dict(gridcolor='#ece9e4', linecolor='#d0cdc8', tickcolor='#ccc'),
    yaxis=dict(gridcolor='#ece9e4', linecolor='#d0cdc8', tickcolor='#ccc'),
    margin=dict(t=20, b=40, l=50, r=20)
)
CORES_LINHAS = ['#2d6a4f','#e76f51','#264653','#457b9d',
                '#e9c46a','#f4a261','#a8dadc','#1d3557','#52b788']


# ─────────────────────────────────────────────
# LINHA 1 — evolução + heatmap
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Análise temporal</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="chart-title">Evolução mensal por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Arrecadação total em R$ bilhões — cada linha é um ano</div>', unsafe_allow_html=True)
    df_evol = df.groupby(['ano','mes'])['valor_B'].sum().reset_index()
    df_evol['nome_mes'] = df_evol['mes'].map(NOMES_MES)
    fig1 = px.line(df_evol, x='nome_mes', y='valor_B', color='ano',
                   markers=True, color_discrete_sequence=CORES_LINHAS,
                   labels={'valor_B':'R$ Bi','nome_mes':'','ano':'Ano'})
    fig1.update_traces(line_width=1.8, marker_size=4)
    fig1.update_layout(**PT, legend=dict(orientation='h', y=-0.2,
                       font=dict(size=10), title=None))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown('<div class="chart-title">Heatmap de sazonalidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Intensidade da arrecadação por mês e ano</div>', unsafe_allow_html=True)
    df_heat = df.groupby(['ano','mes'])['valor_B'].sum().reset_index()
    piv = df_heat.pivot(index='ano', columns='mes', values='valor_B').fillna(0)
    piv.columns = [NOMES_MES[c] for c in piv.columns]
    fig2 = px.imshow(piv, color_continuous_scale='Greens', aspect='auto',
                     labels=dict(color='R$ Bi'))
    fig2.update_layout(**PT, margin=dict(t=20,b=20,l=50,r=20),
                       coloraxis_colorbar=dict(tickfont=dict(color='#888'), thickness=10))
    st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────
# LINHA 2 — concentração UF + YoY
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Distribuição geográfica</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-title">Concentração por estado</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Participação de cada UF no total arrecadado</div>', unsafe_allow_html=True)
    dm = df.groupby('sigla_uf')['valor_B'].sum().sort_values(ascending=False).reset_index()
    dm['share'] = dm['valor_B'] / dm['valor_B'].sum() * 100
    dm['acum']  = dm['share'].cumsum()
    top = dm[dm['acum'].shift(1, fill_value=0) < 55].copy()
    resto_val   = dm[~dm['sigla_uf'].isin(top['sigla_uf'])]['valor_B'].sum()
    resto_share = dm[~dm['sigla_uf'].isin(top['sigla_uf'])]['share'].sum()
    df_pie = pd.concat([
        top[['sigla_uf','valor_B','share']],
        pd.DataFrame([{'sigla_uf':'Demais','valor_B':resto_val,'share':resto_share}])
    ])
    fig3 = px.pie(df_pie, names='sigla_uf', values='valor_B', hole=0.38,
                  color_discrete_sequence=['#1b4332','#2d6a4f','#40916c',
                                           '#52b788','#74c69d','#d8f3dc'])
    fig3.update_traces(textfont_size=11, textfont_color='white',
                       marker=dict(line=dict(color='#faf9f7', width=2)))
    fig3.update_layout(**PT, showlegend=True,
                       legend=dict(orientation='h', y=-0.1, font=dict(size=10)))
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown('<div class="chart-title">Crescimento 2022 → 2023 por UF</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Variação percentual da arrecadação entre os dois anos</div>', unsafe_allow_html=True)
    df_yy = df[df['ano'].isin([2022,2023])].groupby(['sigla_uf','ano'])['valor_B'].sum().reset_index()
    piv_yy = df_yy.pivot(index='sigla_uf', columns='ano', values='valor_B').dropna()
    if 2022 in piv_yy.columns and 2023 in piv_yy.columns:
        piv_yy['pct'] = ((piv_yy[2023]/piv_yy[2022])-1)*100
        piv_yy = piv_yy.reset_index().sort_values('pct', ascending=True)
        cores_bar = ['#2d6a4f' if v >= 0 else '#9b2226' for v in piv_yy['pct']]
        fig4 = go.Figure(go.Bar(
            x=piv_yy['pct'], y=piv_yy['sigla_uf'], orientation='h',
            marker_color=cores_bar, marker_line_width=0,
            text=piv_yy['pct'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside', textfont=dict(color='#888', size=9)
        ))
        fig4.add_vline(x=0, line_color='#ccc', line_width=1)
        fig4.update_layout(**PT, margin=dict(t=20,b=20,l=50,r=60),
                           xaxis_title='Variação (%)', yaxis_title='')
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Selecione um período que inclua 2022 e 2023.")


# ─────────────────────────────────────────────
# LINHA 3 — IPI setorial + II por região
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Composição tributária</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="chart-title">IPI por setor — Autos, Bebidas e Fumo</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Evolução anual da arrecadação por categoria industrial</div>', unsafe_allow_html=True)
    df_ipi = df[df['descricao'].str.contains('AUTOMOVEIS|BEBIDAS|FUMO', na=False, case=False)]
    df_ipi_g = df_ipi.groupby(['ano','descricao'])['valor_B'].sum().reset_index()
    fig5 = px.line(df_ipi_g, x='ano', y='valor_B', color='descricao',
                   markers=True, color_discrete_sequence=['#2d6a4f','#e76f51','#264653'],
                   labels={'valor_B':'R$ Bi','ano':'','descricao':''})
    fig5.update_traces(line_width=2, marker_size=5)
    fig5.update_layout(**PT, legend=dict(orientation='h', y=-0.2,
                       font=dict(size=10), title=None))
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.markdown('<div class="chart-title">Imposto de Importação por região</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Participação percentual do II no total de cada região</div>', unsafe_allow_html=True)
    df_ii  = df[df['descricao'].str.contains('IMPORTACAO', na=False, case=False)]
    tot_rg = df.groupby('regiao')['valor_B'].sum()
    ii_rg  = df_ii.groupby('regiao')['valor_B'].sum()
    pct_ii = (ii_rg / tot_rg * 100).reset_index()
    pct_ii.columns = ['regiao','pct']
    pct_ii = pct_ii.sort_values('pct', ascending=True)
    fig6 = px.bar(pct_ii, x='pct', y='regiao', orientation='h',
                  color='pct', color_continuous_scale='Greens',
                  labels={'pct':'% do II','regiao':''},
                  text=pct_ii['pct'].apply(lambda x: f"{x:.1f}%"))
    fig6.update_traces(textposition='outside', textfont=dict(color='#888'))
    fig6.update_layout(**PT, coloraxis_showscale=False,
                       margin=dict(t=20,b=20,l=90,r=60))
    st.plotly_chart(fig6, use_container_width=True)


# ─────────────────────────────────────────────
# LINHA 4 — Desvio mensal + Volatilidade
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Sazonalidade e volatilidade</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    st.markdown('<div class="chart-title">Desvio mensal da média histórica</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Meses estruturalmente acima (verde) ou abaixo (vermelho) da média</div>', unsafe_allow_html=True)
    med_mes = df.groupby('mes')['valor_B'].mean()
    mg      = med_mes.mean()
    devs    = ((med_mes - mg)/mg*100).reset_index()
    devs.columns = ['mes','desvio']
    devs['nome_mes'] = devs['mes'].map(NOMES_MES)
    devs['cor'] = devs['desvio'].apply(lambda x: '#2d6a4f' if x >= 0 else '#9b2226')
    fig7 = go.Figure(go.Bar(
        x=devs['nome_mes'], y=devs['desvio'],
        marker_color=devs['cor'], marker_line_width=0,
        text=devs['desvio'].apply(lambda x: f"{x:+.1f}%"),
        textposition='outside', textfont=dict(color='#888', size=9)
    ))
    fig7.add_hline(y=0, line_color='#ccc', line_width=1.2)
    fig7.update_layout(**PT, yaxis_title='Desvio (%)', xaxis_title='')
    st.plotly_chart(fig7, use_container_width=True)

with c8:
    st.markdown('<div class="chart-title">Volatilidade por tributo</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Coeficiente de variação — intensidade das oscilações mensais</div>', unsafe_allow_html=True)
    vol_df = (df.groupby('descricao')['valor_B'].std() /
              df.groupby('descricao')['valor_B'].mean() * 100).reset_index()
    vol_df.columns = ['descricao','cv']
    vol_df = vol_df.sort_values('cv', ascending=True)
    fig8 = px.bar(vol_df, x='cv', y='descricao', orientation='h',
                  color='cv', color_continuous_scale='Oranges',
                  labels={'cv':'Coef. Variação (%)','descricao':''},
                  text=vol_df['cv'].apply(lambda x: f"{x:.1f}%"))
    fig8.update_traces(textposition='outside', textfont=dict(color='#888'))
    fig8.update_layout(**PT, coloraxis_showscale=False,
                       margin=dict(t=20,b=20,l=160,r=60))
    st.plotly_chart(fig8, use_container_width=True)


# ─────────────────────────────────────────────
# STORYTELLING
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Síntese analítica</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""
    <div class="finding">
        <div class="finding-num">01 · Achados</div>
        <div class="finding-title">Sudeste concentra mais da metade da receita</div>
        <div class="finding-body">
        São Paulo e Rio de Janeiro respondem por mais de 50% da arrecadação federal.
        O IRPF e o COFINS lideram em volume absoluto. O IPI-Combustíveis apresenta
        a maior volatilidade histórica, com quedas abruptas em 2020 e 2022.
        </div>
    </div>""", unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="finding">
        <div class="finding-num">02 · Interpretações</div>
        <div class="finding-title">Sazonalidade consistente entre os anos</div>
        <div class="finding-body">
        Janeiro e março concentram os maiores volumes todos os anos, reflexo do
        ajuste anual do IRPJ. Norte e Centro-Oeste registraram os maiores
        crescimentos percentuais de 2022 para 2023, indicando expansão regional.
        </div>
    </div>""", unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="finding">
        <div class="finding-num">03 · Recomendações</div>
        <div class="finding-title">Monitorar combustíveis como indicador antecipado</div>
        <div class="finding-body">
        IPI-Combustíveis deve ser acompanhado trimestralmente como proxy de choques
        econômicos. Estados com YoY negativo merecem atenção em políticas regionais.
        A concentração em SP e RJ indica necessidade de diversificação tributária.
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    Fonte: Receita Federal do Brasil via Base dos Dados ·
    Projeto Mensal BI · {ano_min}–{ano_max}
</div>
""", unsafe_allow_html=True)
