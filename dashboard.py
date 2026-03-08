import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

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
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; background: #ffffff; color: #111111; }
.block-container { padding: 2.5rem 3rem 3rem 3rem; max-width: 1400px; background: #ffffff; }
.page-header { border-top: 3px solid #111111; border-bottom: 1px solid #cccccc; padding: 18px 0 14px 0; margin-bottom: 32px; }
.page-header .eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: #555555; margin-bottom: 4px; }
.page-header h1 { font-family: 'Bitter', serif; font-size: 2rem; font-weight: 600; color: #111111; line-height: 1.15; margin: 0; }
.page-header .subtitle { font-size: 0.9rem; color: #444444; margin-top: 6px; font-weight: 400; }
.kpi-wrap { border-top: 2px solid #111111; padding: 18px 16px 16px 16px; background: #fafafa; border-radius: 0 0 4px 4px; height: 100%; }
.kpi-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #555555; margin-bottom: 6px; }
.kpi-number { font-family: 'Bitter', serif; font-size: 2.1rem; font-weight: 600; color: #111111; line-height: 1; }
.kpi-note { font-size: 0.75rem; color: #555555; margin-top: 6px; }
.kpi-up { color: #1a5c38; } .kpi-down { color: #8b1a1a; }
.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: #777777; border-bottom: 1px solid #cccccc; padding-bottom: 5px; margin-bottom: 8px; margin-top: 32px; }
.chart-title { font-family: 'Bitter', serif; font-size: 1.1rem; font-weight: 600; color: #111111; margin-bottom: 4px; }
.chart-desc { font-size: 0.82rem; color: #555555; margin-bottom: 10px; font-weight: 400; }
.question-badge { display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; background: #111111; color: #ffffff; padding: 2px 8px; border-radius: 2px; margin-bottom: 6px; }
.question-text { font-size: 0.84rem; color: #333333; font-style: italic; margin-bottom: 10px; line-height: 1.6; border-left: 3px solid #cccccc; padding-left: 10px; }
.finding { border-top: 1px solid #cccccc; padding: 16px 0; }
.finding-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #888888; margin-bottom: 4px; }
.finding-title { font-family: 'Bitter', serif; font-size: 1rem; font-weight: 600; margin-bottom: 6px; color: #111111; }
.finding-body { font-size: 0.85rem; color: #333333; line-height: 1.8; font-weight: 400; }
section[data-testid="stSidebar"] { background: #f5f5f5; border-right: 1px solid #cccccc; }
section[data-testid="stSidebar"] * { color: #111111 !important; }
section[data-testid="stSidebar"] input { background: #ffffff !important; color: #111111 !important; }
section[data-testid="stSidebar"] select { background: #ffffff !important; color: #111111 !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #ffffff !important; color: #111111 !important; border-color: #cccccc !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] span { color: #111111 !important; }
section[data-testid="stSidebar"] [role="listbox"] { background: #ffffff !important; }
section[data-testid="stSidebar"] [role="option"] { background: #ffffff !important; color: #111111 !important; }
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] { background: #111111 !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #111111 !important; }
section[data-testid="stSidebar"] .stSlider label { color: #111111 !important; }
.footer { border-top: 1px solid #cccccc; margin-top: 48px; padding-top: 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #888888; }
/* Expander fechado: fundo branco, letra preta */
[data-testid="stExpander"] { border: 1px solid #cccccc !important; border-radius: 4px !important; }
[data-testid="stExpander"] summary { background: #ffffff !important; color: #111111 !important; }
[data-testid="stExpander"] summary p { color: #111111 !important; }
[data-testid="stExpander"] summary svg { fill: #111111 !important; }
/* Expander aberto: fundo preto, letra branca */
[data-testid="stExpander"][open] summary { background: #111111 !important; color: #ffffff !important; }
[data-testid="stExpander"][open] summary p { color: #ffffff !important; }
[data-testid="stExpander"][open] summary svg { fill: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAPEAMENTOS
# ─────────────────────────────────────────────
REGIOES = {
    'AC':'Norte','AM':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','AP':'Norte','TO':'Norte',
    'MA':'Nordeste','PI':'Nordeste','CE':'Nordeste','RN':'Nordeste','PB':'Nordeste',
    'PE':'Nordeste','AL':'Nordeste','SE':'Nordeste','BA':'Nordeste',
    'MT':'Centro-Oeste','MS':'Centro-Oeste','GO':'Centro-Oeste','DF':'Centro-Oeste',
    'SP':'Sudeste','RJ':'Sudeste','MG':'Sudeste','ES':'Sudeste',
    'PR':'Sul','SC':'Sul','RS':'Sul'
}
NOMES_MES = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
             7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
ESTACOES = {12:'Verão',1:'Verão',2:'Verão',3:'Outono',4:'Outono',5:'Outono',
            6:'Inverno',7:'Inverno',8:'Inverno',9:'Primavera',10:'Primavera',11:'Primavera'}
COLS_TRIBUTOS = ['imposto_importacao','ipi_fumo','ipi_bebidas','ipi_automoveis',
                 'cide_combustiveis','irpf','irpj_demais_empresas','cofins','pis_pasep']
DESC_TRIBUTO = {
    'imposto_importacao':'IMPOSTO IMPORTACAO','ipi_fumo':'IPI FUMO',
    'ipi_bebidas':'IPI BEBIDAS','ipi_automoveis':'IPI AUTOMOVEIS',
    'cide_combustiveis':'CIDE COMBUSTIVEIS','irpf':'IRPF',
    'irpj_demais_empresas':'IRPJ DEMAIS EMPRESAS','cofins':'COFINS','pis_pasep':'PIS PASEP'
}
CORES_ANO = {
    2016:'steelblue',2017:'darkorange',2018:'green',2019:'red',
    2020:'purple',2021:'brown',2022:'teal',2023:'crimson',2024:'gold'
}
CORES_TRIBUTO = {
    'COFINS':'#3b82f6','PIS PASEP':'#8b5cf6','IRPF':'#f97316',
    'IRPJ DEMAIS EMPRESAS':'#22c55e','IMPOSTO IMPORTACAO':'#ef4444',
    'IPI AUTOMOVEIS':'#eab308','IPI FUMO':'#6b7280',
    'IPI BEBIDAS':'#ec4899','CIDE COMBUSTIVEIS':'#14b8a6'
}

# ─────────────────────────────────────────────
# ETL — replica o notebook
# ─────────────────────────────────────────────
DATA = "Data"

@st.cache_data(show_spinner="Processando dados...")
def load_data():
    df_raw = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_uf.csv.gz"), compression="gzip")
    df_raw['regiao']   = df_raw['sigla_uf'].map(REGIOES)
    df_raw['nome_mes'] = df_raw['mes'].map(NOMES_MES)
    df_raw['estacao']  = df_raw['mes'].map(ESTACOES)
    for col in COLS_TRIBUTOS:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').fillna(0)

    df_completo = pd.melt(
        df_raw,
        id_vars=['ano','mes','nome_mes','estacao','sigla_uf','regiao'],
        value_vars=COLS_TRIBUTOS,
        var_name='BK_Tributo',
        value_name='valor'
    )
    df_completo['descricao'] = df_completo['BK_Tributo'].map(DESC_TRIBUTO)
    df_completo['valor_B']   = df_completo['valor'] / 1e9
    df_completo = df_completo[df_completo['valor'] > 0].copy()
    return df_completo

@st.cache_data(show_spinner="Carregando população IBGE...")
def load_populacao():
    df_pop = pd.read_csv(
        os.path.join(DATA, "br_ibge_populacao_uf.csv.gz"), compression="gzip"
    )
    df_pop = df_pop.dropna(subset=["sigla_uf"])
    df_pop["ano"] = df_pop["ano"].astype(int)
    return df_pop[["ano", "sigla_uf", "populacao"]]

df_completo  = load_data()
df_populacao = load_populacao()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Arrecadação Federal")
    st.caption("Receita Federal do Brasil")
    st.divider()

    anos_disp = [a for a in sorted(df_completo['ano'].unique()) if 2016 <= a <= 2024]
    st.markdown("**Período**")
    ano_min, ano_max = st.select_slider(
        " ", options=anos_disp, value=(2016, 2024)
    )

    st.markdown("**Região**")
    regioes_disp = ["Todas"] + sorted(df_completo['regiao'].dropna().unique().tolist())
    regiao_sel = st.selectbox(" ", regioes_disp, key="reg")

    st.markdown("**Tributo**")
    trib_disp = ["Todos"] + sorted(df_completo['descricao'].dropna().unique().tolist())
    tributo_sel = st.selectbox(" ", trib_disp, key="trib")

    st.divider()
    st.caption("Dados de 2016 a 2024")

    st.divider()
    st.markdown("**Ir para KPI**")
    st.markdown("""
<style>
.kpi-nav a {
    display: block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #111111;
    background: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 6px 12px;
    margin-bottom: 6px;
    text-decoration: none;
    transition: background 0.15s;
}
.kpi-nav a:hover { background: #e8e8e8; }
.kpi-nav .kpi-tag {
    font-size: 0.6rem;
    background: #111111;
    color: #ffffff;
    padding: 1px 5px;
    border-radius: 2px;
    margin-right: 6px;
}
</style>
<div class="kpi-nav">
  <a href="#kpis"><span class="kpi-tag">KPI 1</span>Arrecadação Total</a>
  <a href="#kpis"><span class="kpi-tag">KPI 2</span>Crescimento Anual</a>
  <a href="#kpis"><span class="kpi-tag">KPI 3</span>Estado Líder</a>
  <a href="#kpis"><span class="kpi-tag">KPI 4</span>Composição Tributária</a>
  <a href="#kpi5"><span class="kpi-tag">KPI 5</span>Per Capita · IBGE</a>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTRO
# ─────────────────────────────────────────────
df = df_completo[df_completo['ano'].between(ano_min, ano_max)].copy()
if regiao_sel  != "Todas": df = df[df['regiao']    == regiao_sel]
if tributo_sel != "Todos": df = df[df['descricao'] == tributo_sel]

# ─────────────────────────────────────────────
# KPIs 
# ─────────────────────────────────────────────
total = df['valor'].sum()
anos_kpi = sorted(df['ano'].unique())

# YoY fixo 2022 -> 2023 (2024 incompleto)
yoy = 0
df_yoy_base = df_completo[df_completo['ano'].isin([2022, 2023])]
if regiao_sel  != 'Todas': df_yoy_base = df_yoy_base[df_yoy_base['regiao']    == regiao_sel]
if tributo_sel != 'Todos': df_yoy_base = df_yoy_base[df_yoy_base['descricao'] == tributo_sel]
v_2022 = df_yoy_base[df_yoy_base['ano'] == 2022]['valor'].sum()
v_2023 = df_yoy_base[df_yoy_base['ano'] == 2023]['valor'].sum()
if v_2022 > 0:
    yoy = ((v_2023 / v_2022) - 1) * 100

uf_shares    = df.groupby('sigla_uf')['valor'].sum().sort_values(ascending=False)
uf_lider     = uf_shares.idxmax() if not uf_shares.empty else "—"
uf_share_pct = uf_shares.max() / uf_shares.sum() * 100 if not uf_shares.empty else 0
top3_uf      = (uf_shares / uf_shares.sum() * 100).head(3).reset_index()
top3_uf.columns = ['sigla_uf', 'share_pct']

vol         = df.groupby('descricao')['valor'].std() / df.groupby('descricao')['valor'].mean()
trib_vol    = vol.idxmax() if not vol.empty else "—"

# KPI 4 — Mix de impostos: participação % de cada tributo no total
_mix = df.groupby('descricao')['valor'].sum().sort_values(ascending=False).reset_index()
_mix_total = _mix['valor'].sum()
_mix['share_pct'] = _mix['valor'] / _mix_total * 100

_LABEL = {
    'IRPJ DEMAIS EMPRESAS':'IRPJ',
    'IMPOSTO IMPORTACAO':'Imp. Import.',
    'COFINS':'COFINS',
    'IRPF':'IRPF',
    'PIS PASEP':'PIS/PASEP',
    'IPI AUTOMOVEIS':'IPI Autos',
    'IPI BEBIDAS':'IPI Bebidas',
    'IPI FUMO':'IPI Fumo',
    'CIDE COMBUSTIVEIS':'CIDE',
}
_mix['label'] = _mix['descricao'].map(_LABEL).fillna(_mix['descricao'])

# KPI 5 
_arrec_pc  = df_completo[df_completo['ano'].between(ano_min, ano_max)].groupby(['ano','sigla_uf'])['valor'].sum().reset_index()
_pop_pc    = df_populacao[df_populacao['ano'].between(ano_min, ano_max)][['ano','sigla_uf','populacao']]
_df_pc_kpi = _arrec_pc.merge(_pop_pc, on=['ano','sigla_uf'], how='left')
_df_pc_kpi['per_capita'] = _df_pc_kpi['valor'] / _df_pc_kpi['populacao']
_top5_pc   = _df_pc_kpi.nlargest(5, 'per_capita')[['sigla_uf','ano','per_capita']]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
subtitulo = f"Análise tributária · {ano_min}–{ano_max}"
if regiao_sel  != "Todas": subtitulo += f" · {regiao_sel}"
if tributo_sel != "Todos": subtitulo += f" · {tributo_sel}"

st.markdown(f"""
<div id="topo"></div>
<div class="page-header">
    <div class="eyebrow">Ministério da Fazenda · Receita Federal do Brasil</div>
    <h1>Resultado da Arrecadação Federal</h1>
    <div class="subtitle">{subtitulo}</div>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 Perguntas Analíticas — clique para navegar", expanded=False):
    st.markdown("""
<style>
.qa-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 4px; }
.qa-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 14px;
           border: 1px solid #e0e0e0; border-radius: 4px; text-decoration: none;
           background: #fafafa; transition: background 0.15s; }
.qa-item:hover { background: #f0f0f0; }
.qa-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; font-weight: 600;
          color: #ffffff; background: #111111; padding: 2px 7px; border-radius: 2px;
          white-space: nowrap; margin-top: 2px; }
.qa-text { font-size: 0.83rem; color: #222222; line-height: 1.45; }
</style>
<div class="qa-grid">
  <a class="qa-item" href="#q1"><span class="qa-num">Q1</span><span class="qa-text">Qual a evolução mensal da arrecadação federal total por UF?</span></a>
  <a class="qa-item" href="#q2"><span class="qa-num">Q2</span><span class="qa-text">Quais estados apresentaram maior crescimento percentual comparando 2022 vs. 2023?</span></a>
  <a class="qa-item" href="#q3"><span class="qa-num">Q3</span><span class="qa-text">Qual a participação percentual do Imposto de Importação por região?</span></a>
  <a class="qa-item" href="#q4"><span class="qa-num">Q4 · Q5</span><span class="qa-text">Existe sazonalidade no IPI (Automóveis e Bebidas)? Como o IPI-Fumo se comporta em relação aos outros setores?</span></a>
  <a class="qa-item" href="#q6"><span class="qa-num">Q6</span><span class="qa-text">Quais UFs são responsáveis por mais de 50% da arrecadação total do país?</span></a>
  <a class="qa-item" href="#q7"><span class="qa-num">Q7</span><span class="qa-text">Qual o peso do IPI-Bebidas na arrecadação total nos meses de verão vs. inverno?</span></a>
  <a class="qa-item" href="#q8"><span class="qa-num">Q8</span><span class="qa-text">Quais UFs são mais dependentes de um único tributo?</span></a>
  <a class="qa-item" href="#q9"><span class="qa-num">Q9</span><span class="qa-text">Qual mês do ano historicamente concentra mais arrecadação?</span></a>
  <a class="qa-item" href="#q10"><span class="qa-num">Q10</span><span class="qa-text">Qual tributo possui a maior volatilidade mensal?</span></a>
  <a class="qa-item" href="#kpi5"><span class="qa-num">KPI 5</span><span class="qa-text">Qual a arrecadação per capita por UF? (cruzamento com IBGE)</span></a>
  <a class="qa-item" href="#kpis"><span class="qa-num">KPI 1–4</span><span class="qa-text">Arrecadação total · Crescimento YoY · Estado líder · Maior volatilidade</span></a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="kpis"></div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns([1, 1, 1.4, 1.6, 1.4])
with k1:
    st.markdown(f"""<div class="kpi-wrap">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <div class="kpi-eyebrow">Arrecadação total</div>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;background:#111111;color:#fff;padding:1px 6px;border-radius:2px;">KPI 1</span>
        </div>
        <div class="kpi-number">R$ {total/1e12:.2f}T</div>
        <div class="kpi-note">{ano_min} a {ano_max}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    cls = "kpi-up" if yoy >= 0 else "kpi-down"
    seta = "↑" if yoy >= 0 else "↓"
    st.markdown(f"""<div class="kpi-wrap">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <div class="kpi-eyebrow">Crescimento anual</div>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;background:#111111;color:#fff;padding:1px 6px;border-radius:2px;">KPI 2</span>
        </div>
        <div class="kpi-number {cls}">{seta} {abs(yoy):.1f}%</div>
        <div class="kpi-note">2022 → 2023</div>
    </div>""", unsafe_allow_html=True)
with k3:
    pos3 = ['1º','2º','3º']
    cor3 = ['#b8860b','#707070','#8b4513']
    rows3_uf = ""
    for i, row in enumerate(top3_uf.itertuples()):
        rows3_uf += (
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;padding:2px 0;border-bottom:1px solid #f0f0f0;">'
            f'<span style="display:flex;gap:5px;">'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:{cor3[i]};font-weight:600;">{pos3[i]}</span>'
            f'<span style="font-weight:600;color:{cor3[i]};">{row.sigla_uf}</span>'
            f'</span>'
            f'<span style="color:#333;font-family:IBM Plex Mono,monospace;font-size:0.72rem;">{row.share_pct:.1f}%</span>'
            f'</div>'
        )
    html_k3 = (
        f'<div class="kpi-wrap">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'<div class="kpi-eyebrow">Top 3 estados · market share</div>'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;background:#111111;color:#fff;padding:1px 6px;border-radius:2px;">KPI 3</span>'
        f'</div>'
        f'{rows3_uf}'
        f'</div>'
    )
    st.markdown(html_k3, unsafe_allow_html=True)
with k4:
    rows3_vol = ""
with k4:
    rows_mix = ""
    for i, row in enumerate(_mix.itertuples()):
        cor_m = cor3[i] if i < 3 else '#444444'
        pos_m = pos3[i] if i < 3 else f'{i+1}º'
        rows_mix += (
            f'<div style="display:flex;justify-content:space-between;font-size:0.75rem;padding:3px 0;border-bottom:1px solid #f0f0f0;">'
            f'<span style="display:flex;gap:5px;align-items:center;">'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:{cor_m};font-weight:600;">{pos_m}</span>'
            f'<span style="font-weight:600;color:{cor_m};font-size:0.72rem;">{row.label}</span>'
            f'</span>'
            f'<span style="color:#333;font-family:IBM Plex Mono,monospace;font-size:0.72rem;">{row.share_pct:.1f}%</span>'
            f'</div>'
        )
    html_k4 = (
        f'<div class="kpi-wrap">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'<div class="kpi-eyebrow">Mix de impostos (principais)</div>'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;background:#111111;color:#fff;padding:1px 6px;border-radius:2px;">KPI 4</span>'
        f'</div>'
        f'{rows_mix}'
        f'</div>'
    )
    st.markdown(html_k4, unsafe_allow_html=True)
with k5:
    posicoes = ['1º', '2º', '3º', '4º', '5º']
    cores    = ['#b8860b', '#707070', '#8b4513', '#333333', '#333333']
    top5_rows = ""
    for i, row in enumerate(_top5_pc.itertuples()):
        pos   = posicoes[i]
        cor   = cores[i]
        uf    = row.sigla_uf
        ano_r = row.ano
        pc    = f"R$ {row.per_capita:,.0f}"
        top5_rows += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'font-size:0.78rem;padding:3px 0;border-bottom:1px solid #f0f0f0;">'
            f'<span style="display:flex;align-items:center;gap:5px;">'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:{cor};font-weight:600;">{pos}</span>'
            f'<span style="font-weight:600;color:{cor};">{uf}</span>'
            f'<span style="color:#aaa;font-size:0.82rem;">{ano_r}</span>'
            f'</span>'
            f'<span style="color:#333;font-family:IBM Plex Mono,monospace;font-size:0.72rem;">{pc}</span>'
            f'</div>'
        )
    header_kpi5 = f'<div class="kpi-eyebrow">Top 5 per capita · {ano_min}–{ano_max}</div>'
    html_kpi5 = (
        f'<div class="kpi-wrap">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'{header_kpi5}'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;background:#111111;'
        f'color:#fff;padding:1px 6px;border-radius:2px;">'
        f'<a href="#kpi5" style="color:#fff;text-decoration:none;">KPI 5</a></span>'
        f'</div>'
        f'{top5_rows}'
        f'</div>'
    )
    st.markdown(html_kpi5, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 1 — Sazonalidade 
# Sazonalidade da Arrecadação por mês/ano
# ─────────────────────────────────────────────
st.markdown('<div id="q9"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Análise de Sazonalidade</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 9</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Sazonalidade da Arrecadação Federal</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual mês do ano historicamente concentra mais arrecadação?</div>', unsafe_allow_html=True)

df_sazonalidade = df.groupby(['ano','mes'])['valor_B'].sum().reset_index()
fig_saz = px.line(
    df_sazonalidade, x='mes', y='valor_B', color='ano',
    markers=True,
    labels={'valor_B':'Bilhões de Reais (R$)', 'mes':'Mês', 'ano':'Ano'}
)
fig_saz.update_layout(
    yaxis_tickformat='.2f',
    yaxis_ticksuffix=' B',
    yaxis_title='Bilhões de Reais (R$)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111'), tickmode='linear', tick0=1, dtick=1,
               tickvals=list(range(1,13)), ticktext=list(NOMES_MES.values())),
    yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    legend=dict(orientation='h', y=-0.2, title=None, font=dict(size=11, color='#111111')),
    margin=dict(t=20, b=60, l=60, r=20)
)
st.plotly_chart(fig_saz, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 2 + 3 — Top 5 UFs e Tributos
# ─────────────────────────────────────────────
st.markdown('<div id="q6"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Ranking de Arrecadação</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="question-badge">Questão 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Top 5 Estados com Maior Arrecadação</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-text">Quais UFs são responsáveis por mais de 50% da arrecadação total do país?</div>', unsafe_allow_html=True)
    df_ranking = df.groupby('sigla_uf')['valor_B'].sum().reset_index()
    df_top5 = df_ranking.sort_values('valor_B', ascending=False).head(5)
    fig_ranking = px.bar(
        df_top5, x='sigla_uf', y='valor_B',
        labels={'valor_B':'Total em Bilhões (R$)', 'sigla_uf':'Estado'},
        color='valor_B', text_auto='.2f',
        color_continuous_scale='Sunset'
    )
    fig_ranking.update_layout(
        yaxis_ticksuffix=' B', coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111111', family='Source Sans 3, sans-serif'),
        xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')), yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
        margin=dict(t=20, b=40, l=60, r=20)
    )
    st.plotly_chart(fig_ranking, width="stretch")
    st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="question-badge">Questões 4 · 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Participação por Tipo de Tributo</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-text">Como cada tributo contribui para a arrecadação total? Como o IPI-Fumo se comporta em relação aos outros setores?</div>', unsafe_allow_html=True)
    df_tributo_rank = df.groupby('descricao')['valor_B'].sum().reset_index()
    df_tributo_rank = df_tributo_rank.sort_values('valor_B', ascending=True)
    fig_tributos = px.bar(
        df_tributo_rank, x='valor_B', y='descricao', orientation='h',
        labels={'valor_B':'Total (R$ Bilhões)', 'descricao':'Tributo'},
        text_auto='.2f', color='valor_B',
        color_continuous_scale='Sunset'
    )
    fig_tributos.update_layout(
        yaxis={'categoryorder':'total ascending', 'gridcolor':'#e0e0e0', 'tickfont':{'color':'#111111'}, 'title_font':{'color':'#111111'}}, height=400,
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111111', family='Source Sans 3, sans-serif'),
        xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
        margin=dict(t=20, b=40, l=160, r=20)
    )
    st.plotly_chart(fig_tributos, width="stretch")
    st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 4 — Evolução mensal por UF
# ─────────────────────────────────────────────
st.markdown('<div id="q1"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Evolução Geográfica</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 1</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Evolução Mensal da Arrecadação por UF</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual a evolução mensal da arrecadação federal total por Unidade da Federação (UF)?</div>', unsafe_allow_html=True)

ufs_disp = sorted(df['sigla_uf'].unique())
ufs_sel = st.multiselect("Estados", ufs_disp, default=ufs_disp[:5])
df_evol_uf = df[df['sigla_uf'].isin(ufs_sel)].groupby(['ano','mes','sigla_uf'])['valor_B'].sum().reset_index()

anos_evol = sorted(df_evol_uf['ano'].unique())
n_anos = len(anos_evol)
n_cols = 3
n_rows = -(-n_anos // n_cols)  # teto da divisão

fig_evol = px.line(
    df_evol_uf, x='mes', y='valor_B', color='sigla_uf',
    facet_col='ano', facet_col_wrap=n_cols,
    labels={'valor_B':'R$ Bi','mes':'Mês','sigla_uf':'UF'},
    height=320 * n_rows
)
fig_evol.update_layout(
    yaxis_ticksuffix=' B',
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    margin=dict(t=40, b=40, l=60, r=20),
    legend=dict(orientation='h', y=-0.05, font=dict(size=11, color='#111111'))
)
fig_evol.update_xaxes(
    tickmode='linear', tick0=1, dtick=2,
    tickfont=dict(color='#111111'), title_font=dict(color='#111111')
)
fig_evol.update_yaxes(
    tickfont=dict(color='#111111'), title_font=dict(color='#111111')
)
st.plotly_chart(fig_evol, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 5 — Sazonalidade IPI 
# ─────────────────────────────────────────────
st.markdown('<div id="q4"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">IPI Setorial</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questões 4 · 5</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Sazonalidade IPI: Fumo vs Automóveis vs Bebidas</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Existe sazonalidade identificável na arrecadação de IPI (Automóveis e Bebidas) ao longo dos anos? Como o IPI-Fumo se comporta em relação aos outros setores industriais?</div>', unsafe_allow_html=True)

setores_ipi = ['AUTOMOVEIS','BEBIDAS','FUMO']
df_setores = df[df['descricao'].str.contains('|'.join(setores_ipi), na=False)]
df_ipi_sazonal = df_setores.groupby(['ano','mes','descricao'])['valor'].sum().reset_index()

fig_ipi = px.line(
    df_ipi_sazonal, x='mes', y='valor', color='ano',
    facet_col='descricao',
    labels={'valor':'Arrecadação (R$)','mes':'Mês','ano':'Ano','descricao':''}
)
fig_ipi.update_yaxes(matches=None, tickfont=dict(color='#111111'), title_font=dict(color='#111111'))
fig_ipi.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    legend=dict(orientation='h', y=-0.2, title=None, font=dict(size=11, color='#111111')),
    margin=dict(t=40, b=60, l=60, r=20)
)
fig_ipi.update_xaxes(tickmode='linear', tick0=1, dtick=1,
                     tickvals=list(range(1,13)), ticktext=list(NOMES_MES.values()),
                     tickfont=dict(color='#111111'), title_font=dict(color='#111111'))
st.plotly_chart(fig_ipi, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 6 — IPI Bebidas por estação 
# ─────────────────────────────────────────────
st.markdown('<div id="q7"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Sazonalidade Estacional</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 7</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Peso % do IPI-Bebidas na Arrecadação Total</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual o peso do IPI-Bebidas na arrecadação total nos meses de verão vs inverno no recorte temporal de 2016 a 2024?</div>', unsafe_allow_html=True)

df_completo_f = df.copy()
df_completo_f['estacao'] = df_completo_f['mes'].map(ESTACOES)

total_mensal = df_completo_f.groupby(['ano','mes','estacao'])['valor'].sum().reset_index()
total_mensal.rename(columns={'valor':'total_geral'}, inplace=True)

df_bebidas = df_completo_f[df_completo_f['descricao'].str.contains('BEBIDAS', na=False)]
bebidas_mensal = df_bebidas.groupby(['ano','mes'])['valor'].sum().reset_index()
bebidas_mensal.rename(columns={'valor':'valor_bebidas'}, inplace=True)

df_peso = total_mensal.merge(bebidas_mensal, on=['ano','mes'])
df_peso['peso_pct'] = (df_peso['valor_bebidas'] / df_peso['total_geral']) * 100
df_peso['data'] = pd.to_datetime(df_peso['ano'].astype(str) + '-' + df_peso['mes'].astype(str) + '-01')
df_peso = df_peso.sort_values('data')

cor_estacao = {'Verão':'#f97316','Outono':'#a3a3a3','Inverno':'#3b82f6','Primavera':'#22c55e'}
df_peso['cor'] = df_peso['estacao'].map(cor_estacao)

fig_beb = go.Figure()
fig_beb.add_trace(go.Scatter(
    x=df_peso['data'], y=df_peso['peso_pct'],
    mode='lines', line=dict(color='lightgray', width=1.5),
    showlegend=False, hoverinfo='skip'
))
for estacao, cor in cor_estacao.items():
    mask = df_peso['estacao'] == estacao
    fig_beb.add_trace(go.Scatter(
        x=df_peso[mask]['data'], y=df_peso[mask]['peso_pct'],
        mode='markers', name=estacao,
        marker=dict(color=cor, size=8),
        hovertemplate='<b>%{x|%b/%Y}</b><br>Peso: %{y:.2f}%<extra></extra>'
    ))

if not df_peso.empty:
    media_verao   = df_peso[df_peso['estacao'] == 'Verão']['peso_pct'].mean()
    media_inverno = df_peso[df_peso['estacao'] == 'Inverno']['peso_pct'].mean()
    fig_beb.add_hline(y=media_verao, line_dash='dot', line_color='#f97316',
                      annotation_text=f'Média Verão: {media_verao:.2f}%',
                      annotation_position='top right')
    fig_beb.add_hline(y=media_inverno, line_dash='dot', line_color='#3b82f6',
                      annotation_text=f'Média Inverno: {media_inverno:.2f}%',
                      annotation_position='bottom right')

fig_beb.update_layout(
    xaxis_title='Mês/Ano', yaxis_title='% da Arrecadação Total',
    xaxis=dict(tickformat='%b/%Y', tickangle=-45, tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    height=500, hovermode='x unified', legend_title='Estação',
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=20, b=80, l=60, r=20)
)
st.plotly_chart(fig_beb, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 7 — Tributo dominante por UF 
# ─────────────────────────────────────────────
st.markdown('<div id="q8"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Dependência Tributária por UF</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 8</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Concentração de Receita por UF — Qual tributo domina cada estado?</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Quais UFs são mais dependentes de um único tributo (concentração de receita)? Linha vermelha marca o limiar de 50%.</div>', unsafe_allow_html=True)

total_por_uf   = df.groupby('sigla_uf')['valor'].sum().reset_index().rename(columns={'valor':'total_uf'})
tributo_por_uf = df.groupby(['sigla_uf','descricao'])['valor'].sum().reset_index()
tributo_por_uf = tributo_por_uf.merge(total_por_uf, on='sigla_uf')
tributo_por_uf['share_pct'] = (tributo_por_uf['valor'] / tributo_por_uf['total_uf']) * 100

dominante = (
    tributo_por_uf.sort_values('share_pct', ascending=False)
    .groupby('sigla_uf').first().reset_index()
    [['sigla_uf','descricao','share_pct']]
    .rename(columns={'descricao':'tributo_dominante'})
    .sort_values('share_pct', ascending=True)
)
dominante['cor'] = dominante['tributo_dominante'].map(CORES_TRIBUTO).fillna('#94a3b8')

fig_dom = go.Figure()
fig_dom.add_trace(go.Bar(
    x=dominante['share_pct'], y=dominante['sigla_uf'], orientation='h',
    marker_color=dominante['cor'],
    text=dominante['tributo_dominante'] + '  ' + dominante['share_pct'].round(1).astype(str) + '%',
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Tributo dominante: %{text}<extra></extra>'
))
fig_dom.add_vline(x=50, line_dash='dash', line_color='red',
                  annotation_text='50% — limiar de dependência',
                  annotation_position='top')
fig_dom.update_layout(
    xaxis_title='Share do tributo dominante na arrecadação total da UF (%)',
    yaxis_title='', height=650,
    margin=dict(t=40, b=40, l=50, r=250),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='white',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e5e7eb', range=[0, 105], tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    yaxis=dict(tickfont=dict(color='#111111'), title_font=dict(color='#111111'))
)
st.plotly_chart(fig_dom, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 8 — Evolução mensal empilhada
# ─────────────────────────────────────────────
st.markdown('<div id="q9b"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Composição Mensal Histórica</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 9</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Evolução Mensal da Arrecadação Federal por Ano (2016–2024)</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual mês do ano historicamente concentra mais arrecadação? Comparação empilhada por ano em R$ bilhões.</div>', unsafe_allow_html=True)

df_mes_ano = df[df['ano'].between(2016, 2024)].groupby(['ano','mes'])['valor_B'].sum().reset_index()
df_mes_ano['nome_mes'] = df_mes_ano['mes'].map(NOMES_MES)

fig_empilhado = go.Figure()
for ano in sorted(df_mes_ano['ano'].unique()):
    df_ano = df_mes_ano[df_mes_ano['ano'] == ano]
    fig_empilhado.add_trace(go.Bar(
        x=df_ano['nome_mes'], y=df_ano['valor_B'],
        name=str(ano), marker_color=CORES_ANO.get(ano, '#888')
    ))
fig_empilhado.update_layout(
    barmode='stack',
    xaxis_title='Mês', yaxis_title='R$ Bilhões',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')), yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=60, b=40, l=60, r=20)
)
st.plotly_chart(fig_empilhado, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)



# ─────────────────────────────────────────────
# GRÁFICO 9 — Crescimento 2022 vs 2023 (Q2)
# ─────────────────────────────────────────────
st.markdown('<div id="q2"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Crescimento Estadual 2022 → 2023</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 2</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Crescimento Percentual da Arrecadação por Estado</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Quais estados apresentaram o maior crescimento percentual de arrecadação comparando 2022 vs. 2023?</div>', unsafe_allow_html=True)

df_2022 = df_completo[df_completo['ano'] == 2022].groupby('sigla_uf')['valor'].sum()
df_2023 = df_completo[df_completo['ano'] == 2023].groupby('sigla_uf')['valor'].sum()
df_cresc = pd.DataFrame({'2022': df_2022, '2023': df_2023}).dropna()
df_cresc['crescimento_pct'] = ((df_cresc['2023'] / df_cresc['2022']) - 1) * 100
df_cresc = df_cresc.reset_index().sort_values('crescimento_pct', ascending=True)
df_cresc['cor'] = df_cresc['crescimento_pct'].apply(lambda x: '#1a5c38' if x >= 0 else '#8b1a1a')

fig_cresc = go.Figure()
fig_cresc.add_trace(go.Bar(
    x=df_cresc['crescimento_pct'],
    y=df_cresc['sigla_uf'],
    orientation='h',
    marker_color=df_cresc['cor'],
    text=df_cresc['crescimento_pct'].apply(lambda x: f"{x:+.1f}%"),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Crescimento: %{x:.1f}%<extra></extra>'
))
fig_cresc.add_vline(x=0, line_color='#333333', line_width=1)
fig_cresc.update_layout(
    xaxis_title='Variação % (2022 → 2023)', yaxis_title='',
    height=600,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=20, b=40, l=50, r=80)
)
st.plotly_chart(fig_cresc, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 10 — Participação II por região (Q3)
# ─────────────────────────────────────────────
st.markdown('<div id="q3"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Imposto de Importação por Região</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 3</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Participação Percentual do II na Arrecadação Total por Região</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual a participação percentual do Imposto de Importação (II) na arrecadação total de cada região?</div>', unsafe_allow_html=True)

df_ii      = df[df['BK_Tributo'] == 'imposto_importacao']
tot_reg    = df.groupby('regiao')['valor'].sum()
ii_reg     = df_ii.groupby('regiao')['valor'].sum()
pct_ii_reg = (ii_reg / tot_reg * 100).reset_index()
pct_ii_reg.columns = ['regiao', 'pct']
pct_ii_reg = pct_ii_reg.dropna().sort_values('pct', ascending=True)

fig_ii = px.bar(
    pct_ii_reg, x='pct', y='regiao', orientation='h',
    color='pct', color_continuous_scale='Sunset',
    labels={'pct':'% do II na arrecadação total','regiao':''},
    text=pct_ii_reg['pct'].apply(lambda x: f"{x:.1f}%")
)
fig_ii.update_traces(textposition='outside')
fig_ii.update_layout(
    coloraxis_showscale=False,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=20, b=40, l=120, r=80)
)
st.plotly_chart(fig_ii, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 11 — Volatilidade por tributo (Q10)
# ─────────────────────────────────────────────
st.markdown('<div id="q10"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Volatilidade Tributária</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">Questão 10</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Volatilidade Mensal por Tributo</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Qual tributo possui a maior volatilidade mensal? (Coeficiente de variação — intensidade e frequência das oscilações)</div>', unsafe_allow_html=True)

vol_df = (
    df.groupby('descricao')['valor'].std() /
    df.groupby('descricao')['valor'].mean() * 100
).reset_index()
vol_df.columns = ['descricao', 'cv']
vol_df = vol_df.sort_values('cv', ascending=True)

fig_vol = px.bar(
    vol_df, x='cv', y='descricao', orientation='h',
    color='cv', color_continuous_scale='Oranges',
    labels={'cv':'Coeficiente de Variação (%)','descricao':''},
    text=vol_df['cv'].apply(lambda x: f"{x:.1f}%")
)
fig_vol.update_traces(textposition='outside')
fig_vol.update_layout(
    coloraxis_showscale=False,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    yaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=20, b=40, l=180, r=80)
)
st.plotly_chart(fig_vol, width="stretch")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO 12 — Arrecadação per Capita (KPI 5 / IBGE)
# ─────────────────────────────────────────────
st.markdown('<div id="kpi5"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Cruzamento com IBGE · Arrecadação per Capita</div>', unsafe_allow_html=True)
st.markdown('<div class="question-badge">KPI 5</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Arrecadação per Capita por UF</div>', unsafe_allow_html=True)
st.markdown('<div class="question-text">Cruzamento da arrecadação federal com as estimativas populacionais do IBGE (2016–2024). Quanto cada habitante representa na arrecadação do seu estado?</div>', unsafe_allow_html=True)

# População IBGE 
df_pop = df_populacao

# Arrecadação anual por UF (total, não filtrado para manter base completa)
df_arrec_ano = df_completo[df_completo['ano'].between(ano_min, ano_max)].groupby(['ano','sigla_uf'])['valor'].sum().reset_index()
df_pc = df_arrec_ano.merge(df_pop, on=['ano','sigla_uf'], how='left')
df_pc['per_capita'] = df_pc['valor'] / df_pc['populacao']

# Ano selecionado para o ranking
ano_pc = st.select_slider("Ano de referência", options=list(range(ano_min, min(ano_max, 2024)+1)), value=2023)
df_pc_ano = df_pc[df_pc['ano'] == ano_pc].sort_values('per_capita', ascending=True)

fig_pc = px.bar(
    df_pc_ano, x='per_capita', y='sigla_uf', orientation='h',
    color='per_capita', color_continuous_scale='Sunset',
    labels={'per_capita': 'R$ per capita', 'sigla_uf': ''},
    text=df_pc_ano['per_capita'].apply(lambda x: f"R$ {x:,.0f}")
)
fig_pc.update_traces(textposition='outside')
fig_pc.update_layout(
    coloraxis_showscale=False, height=680,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Source Sans 3, sans-serif'),
    xaxis=dict(gridcolor='#e0e0e0', tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    yaxis=dict(tickfont=dict(color='#111111'), title_font=dict(color='#111111')),
    margin=dict(t=20, b=40, l=50, r=120)
)
st.plotly_chart(fig_pc, width="stretch")
st.caption("Fonte: arrecadação RFB / população IBGE — Estimativas de População por UF")
st.markdown('''<a href="#topo" style="display:inline-block;margin-top:4px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#888888;text-decoration:none;border:1px solid #e0e0e0;padding:3px 10px;border-radius:3px;">↑ voltar ao topo</a>''', unsafe_allow_html=True)


# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Data Storytelling · Síntese Analítica</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""<div class="finding">
        <div class="finding-num">01 · Principais Achados</div>
        <div class="finding-title">O Brasil arrecada de forma muito concentrada</div>
        <div class="finding-body">
        São Paulo e Rio de Janeiro sozinhos respondem por mais da metade de toda a arrecadação
        federal do país. O COFINS e o IRPJ são os tributos que mais pesam no total, presentes
        em praticamente todos os estados. Janeiro e março são historicamente os meses de pico —
        não por acaso, é quando as empresas fazem o acerto anual do imposto de renda. O IPI-Bebidas
        sobe levemente no verão, o que faz sentido dado o maior consumo na estação. E o
        CIDE-Combustíveis foi o tributo que mais oscilou ao longo dos anos, com quedas
        expressivas em 2020 e 2022.
        </div>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown("""<div class="finding">
        <div class="finding-num">02 · Interpretações</div>
        <div class="finding-title">Por que isso acontece?</div>
        <div class="finding-body">
        A concentração no Sudeste acompanha a distribuição da atividade econômica — SP e RJ
        sediam as maiores empresas e instituições financeiras do país. A queda no IPI automotivo
        em 2020 reflete o impacto da pandemia sobre o crédito ao consumidor, com recuperação
        gradual nos anos seguintes. Estados menores, especialmente no Norte e Centro-Oeste,
        dependem de um único tributo para a maior parte de sua receita, o que os deixa mais
        expostos a qualquer mudança na política fiscal federal. O crescimento entre 2022 e 2023
        foi generalizado, mas as regiões Norte e Nordeste se destacaram em termos percentuais.
        </div>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown("""<div class="finding">
        <div class="finding-num">03 · Recomendações</div>
        <div class="finding-title">O que fazer com isso?</div>
        <div class="finding-body">
        Estados com mais de 50% da arrecadação dependente de um único tributo precisam de atenção:
        qualquer isenção ou mudança de alíquota pode gerar impacto fiscal imediato e difícil de
        compensar no curto prazo. O CIDE-Combustíveis vale ser monitorado de perto — historicamente
        ele antecipa movimentos na economia real. E para o planejamento orçamentário federal,
        a sazonalidade de janeiro e março deve ser levada em conta nas projeções de caixa,
        evitando subestimar a receita do primeiro trimestre.
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="footer">
    Fonte: Receita Federal do Brasil via Base dos Dados · Projeto Mensal BI · {ano_min}–{ano_max}
</div>

""", unsafe_allow_html=True)
