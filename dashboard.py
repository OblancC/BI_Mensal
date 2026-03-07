import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

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
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; background: #faf9f7; color: #1a1a1a; }
.block-container { padding: 2.5rem 3rem 3rem 3rem; max-width: 1400px; }
.page-header { border-top: 3px solid #1a1a1a; border-bottom: 1px solid #d0cdc8; padding: 18px 0 14px 0; margin-bottom: 32px; }
.page-header .eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: #888; margin-bottom: 4px; }
.page-header h1 { font-family: 'Bitter', serif; font-size: 2rem; font-weight: 600; color: #1a1a1a; line-height: 1.15; margin: 0; }
.page-header .subtitle { font-size: 0.9rem; color: #666; margin-top: 6px; font-weight: 300; }
.kpi-wrap { border-top: 2px solid #1a1a1a; padding: 14px 0 10px 0; }
.kpi-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #999; margin-bottom: 2px; }
.kpi-number { font-family: 'Bitter', serif; font-size: 2.1rem; font-weight: 600; color: #1a1a1a; line-height: 1; }
.kpi-note { font-size: 0.75rem; color: #888; margin-top: 3px; }
.kpi-up { color: #2d6a4f; } .kpi-down { color: #9b2226; }
.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: #aaa; border-bottom: 1px solid #e5e2dd; padding-bottom: 5px; margin-bottom: 4px; margin-top: 28px; }
.chart-title { font-family: 'Bitter', serif; font-size: 1.05rem; font-weight: 600; color: #1a1a1a; margin-bottom: 2px; }
.chart-desc { font-size: 0.78rem; color: #888; margin-bottom: 10px; font-weight: 300; }
.finding { border-top: 1px solid #d0cdc8; padding: 16px 0; }
.finding-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #bbb; margin-bottom: 4px; }
.finding-title { font-family: 'Bitter', serif; font-size: 0.95rem; font-weight: 600; margin-bottom: 5px; color: #1a1a1a; }
.finding-body { font-size: 0.82rem; color: #555; line-height: 1.75; font-weight: 300; }
section[data-testid="stSidebar"] { background: #f2f0ed; border-right: 1px solid #d0cdc8; }
section[data-testid="stSidebar"] * { color: #1a1a1a !important; }
.footer { border-top: 1px solid #d0cdc8; margin-top: 48px; padding-top: 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #bbb; }
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
    'imposto_importacao':'Imposto de Importação','ipi_fumo':'IPI-Fumo',
    'ipi_bebidas':'IPI-Bebidas','ipi_automoveis':'IPI-Automóveis',
    'cide_combustiveis':'CIDE-Combustíveis','irpf':'IRPF',
    'irpj_demais_empresas':'IRPJ','cofins':'COFINS','pis_pasep':'PIS/PASEP'
}
CNAE_NOMES = {
    'A':'Agropecuária','B':'Ind. Extrativas','C':'Ind. Transformação','D':'Eletricidade',
    'E':'Água/Saneamento','F':'Construção','G':'Comércio','H':'Transporte',
    'I':'Hospedagem','J':'TI/Comunicação','K':'Financeiro','L':'Imobiliário',
    'M':'Prof./Técnico','N':'Administrativo','O':'Adm. Pública','P':'Educação',
    'Q':'Saúde','R':'Artes','S':'Outros Serviços','T':'Famílias',
    'U':'Org. Internacionais','IN':'Não Identificado','NI':'Não Informado','PF':'Pessoa Física'
}
NJ_NOMES = {
    '2062':'Soc. Emp. Ltda','2054':'S.A. Aberta','2038':'S.A. Fechada',
    '2046':'Soc. Emp. S/A','1015':'Órgão Público','2011':'Empresa Pública',
    '2135':'Soc. Simples Ltda','2305':'Empresário Individual',
    '4014':'Cooperativa','2143':'MEI','2160':'EIRELI'
}

# ─────────────────────────────────────────────
# CARREGAMENTO E ETL
# ─────────────────────────────────────────────
DATA = "data"

@st.cache_data(show_spinner="Processando dados...")
def load_data():
    # ── 1. UF — fonte principal (replica ETL do notebook) ──
    df_raw = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_uf_csv.csv"))
    df_raw['regiao']   = df_raw['sigla_uf'].map(REGIOES)
    df_raw['nome_mes'] = df_raw['mes'].map(NOMES_MES)
    df_raw['estacao']  = df_raw['mes'].map(ESTACOES)
    for col in COLS_TRIBUTOS:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').fillna(0)

    # unpivot — igual ao notebook (melt)
    df_completo = pd.melt(
        df_raw,
        id_vars=['ano','mes','nome_mes','estacao','sigla_uf','regiao'],
        value_vars=COLS_TRIBUTOS,
        var_name='BK_Tributo',
        value_name='valor'
    )
    df_completo['descricao'] = df_completo['BK_Tributo'].map(DESC_TRIBUTO)
    df_completo['valor_B']   = df_completo['valor'] / 1e9
    df_completo = df_completo[df_completo['valor'] > 0]

    # ── 2. CNAE ──
    df_cnae = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_cnae_csv.csv"))
    cols_val = [c for c in df_cnae.columns if c not in ['ano','mes','secao_sigla']]
    for col in cols_val:
        df_cnae[col] = pd.to_numeric(df_cnae[col], errors='coerce').fillna(0)
    df_cnae['total']  = df_cnae[cols_val].sum(axis=1)
    df_cnae['setor']  = df_cnae['secao_sigla'].map(CNAE_NOMES).fillna(df_cnae['secao_sigla'])
    df_cnae['valor_B'] = df_cnae['total'] / 1e9

    # ── 3. IR/IPI (bruto vs líquido) ──
    df_ir = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_ir_ipi_csv.csv"))
    for col in ['arrecadacao_bruta','arrecadacao_liquida','restituicao','compensacao']:
        df_ir[col] = pd.to_numeric(df_ir[col], errors='coerce').fillna(0)
    df_ir['bruto_B']   = df_ir['arrecadacao_bruta']   / 1e9
    df_ir['liquido_B'] = df_ir['arrecadacao_liquida']  / 1e9
    df_ir['restituicao_B'] = df_ir['restituicao'].abs() / 1e9

    # ── 4. ITR por UF ──
    df_itr = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_itr_csv.csv"))
    df_itr['valor_arrecadado'] = pd.to_numeric(df_itr['valor_arrecadado'], errors='coerce').fillna(0)
    df_itr['regiao']  = df_itr['sigla_uf'].map(REGIOES)
    df_itr['valor_B'] = df_itr['valor_arrecadado'] / 1e6  # em milhões para ITR

    # ── 5. Natureza Jurídica ──
    df_nj = pd.read_csv(os.path.join(DATA, "br_rf_arrecadacao_natureza_juridica_csv.csv"))
    cols_nj = [c for c in df_nj.columns if c not in ['ano','mes','natureza_juridica_codigo']]
    for col in cols_nj:
        df_nj[col] = pd.to_numeric(df_nj[col], errors='coerce').fillna(0)
    df_nj['total']  = df_nj[cols_nj].sum(axis=1)
    df_nj['tipo']   = df_nj['natureza_juridica_codigo'].astype(str).map(NJ_NOMES).fillna('Outros')
    df_nj['valor_B'] = df_nj['total'] / 1e9

    return df_completo, df_cnae, df_ir, df_itr, df_nj

df_completo, df_cnae, df_ir, df_itr, df_nj = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Arrecadação Federal")
    st.caption("Receita Federal do Brasil · 2000–2024")
    st.divider()

    anos_disp = sorted(df_completo['ano'].unique())
    st.markdown("**Período**")
    ano_min, ano_max = st.select_slider(
        " ", options=anos_disp, value=(2016, max(anos_disp))
    )

    st.markdown("**Região**")
    regioes_disp = ["Todas"] + sorted(df_completo['regiao'].dropna().unique().tolist())
    regiao_sel = st.selectbox(" ", regioes_disp, key="reg")

    st.markdown("**Tributo**")
    trib_disp = ["Todos"] + sorted(df_completo['descricao'].dropna().unique().tolist())
    tributo_sel = st.selectbox(" ", trib_disp, key="trib")

    st.divider()
    st.caption(f"Dados de {min(anos_disp)} a {max(anos_disp)}")

# ─────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────
df = df_completo[df_completo['ano'].between(ano_min, ano_max)].copy()
if regiao_sel  != "Todas": df = df[df['regiao']    == regiao_sel]
if tributo_sel != "Todos": df = df[df['descricao'] == tributo_sel]

df_cnae_f = df_cnae[df_cnae['ano'].between(ano_min, ano_max)]
df_ir_f   = df_ir[df_ir['ano'].between(ano_min, ano_max)]
df_itr_f  = df_itr[df_itr['ano'].between(ano_min, ano_max)]
if regiao_sel != "Todas": df_itr_f = df_itr_f[df_itr_f['regiao'] == regiao_sel]
df_nj_f   = df_nj[df_nj['ano'].between(ano_min, ano_max)]

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total    = df['valor'].sum()
anos_kpi = sorted(df['ano'].unique())
yoy = 0
if len(anos_kpi) >= 2:
    v_atual = df[df['ano'] == anos_kpi[-1]]['valor'].sum()
    v_ant   = df[df['ano'] == anos_kpi[-2]]['valor'].sum()
    yoy = ((v_atual / v_ant) - 1) * 100 if v_ant > 0 else 0

uf_shares = df.groupby('sigla_uf')['valor'].sum()
uf_lider  = uf_shares.idxmax() if not uf_shares.empty else "—"
uf_share  = uf_shares.max() / uf_shares.sum() * 100 if not uf_shares.empty else 0

vol      = df.groupby('descricao')['valor'].std() / df.groupby('descricao')['valor'].mean()
trib_vol = vol.idxmax() if not vol.empty else "—"

setor_lider = df_cnae_f.groupby('setor')['total'].sum().idxmax() if not df_cnae_f.empty else "—"

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

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-wrap">
        <div class="kpi-eyebrow">Arrecadação total</div>
        <div class="kpi-number">R$ {total/1e12:.2f}T</div>
        <div class="kpi-note">{ano_min} a {ano_max}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    cls = "kpi-up" if yoy >= 0 else "kpi-down"
    ref = f"{anos_kpi[-2]}→{anos_kpi[-1]}" if len(anos_kpi) >= 2 else "—"
    st.markdown(f"""<div class="kpi-wrap">
        <div class="kpi-eyebrow">Crescimento anual</div>
        <div class="kpi-number {cls}">{'↑' if yoy>=0 else '↓'} {abs(yoy):.1f}%</div>
        <div class="kpi-note">{ref}</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-wrap">
        <div class="kpi-eyebrow">Estado líder</div>
        <div class="kpi-number">{uf_lider}</div>
        <div class="kpi-note">{uf_share:.1f}% do total nacional</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-wrap">
        <div class="kpi-eyebrow">Maior volatilidade</div>
        <div class="kpi-number" style="font-size:1rem;padding-top:8px">{trib_vol}</div>
        <div class="kpi-note">coef. de variação mais alto</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="kpi-wrap">
        <div class="kpi-eyebrow">Setor CNAE líder</div>
        <div class="kpi-number" style="font-size:1rem;padding-top:8px">{setor_lider}</div>
        <div class="kpi-note">maior arrecadação por setor</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TEMA PLOTLY
# ─────────────────────────────────────────────
PT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#666', family='Source Sans 3, sans-serif', size=11),
    xaxis=dict(gridcolor='#ece9e4', linecolor='#d0cdc8', tickcolor='#ccc'),
    yaxis=dict(gridcolor='#ece9e4', linecolor='#d0cdc8', tickcolor='#ccc'),
    margin=dict(t=20, b=40, l=50, r=20)
)
CORES = ['#2d6a4f','#e76f51','#264653','#457b9d','#e9c46a','#f4a261','#a8dadc','#1d3557','#52b788']

# ─────────────────────────────────────────────
# SEÇÃO 1 — Análise temporal · UF
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Análise temporal · por UF</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="chart-title">Evolução mensal por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Arrecadação total em R$ bilhões — cada linha é um ano</div>', unsafe_allow_html=True)
    df_evol = df.groupby(['ano','mes'])['valor_B'].sum().reset_index()
    df_evol['nome_mes'] = df_evol['mes'].map(NOMES_MES)
    fig1 = px.line(df_evol, x='nome_mes', y='valor_B', color='ano',
                   markers=True, color_discrete_sequence=CORES,
                   labels={'valor_B':'R$ Bi','nome_mes':'','ano':'Ano'})
    fig1.update_traces(line_width=1.8, marker_size=4)
    fig1.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown('<div class="chart-title">Heatmap de sazonalidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Intensidade da arrecadação por mês e ano</div>', unsafe_allow_html=True)
    df_heat = df.groupby(['ano','mes'])['valor_B'].sum().reset_index()
    piv = df_heat.pivot(index='ano', columns='mes', values='valor_B').fillna(0)
    piv.columns = [NOMES_MES[c] for c in piv.columns]
    fig2 = px.imshow(piv, color_continuous_scale='Greens', aspect='auto', labels=dict(color='R$ Bi'))
    fig2.update_layout(**PT, margin=dict(t=20,b=20,l=50,r=20),
                       coloraxis_colorbar=dict(tickfont=dict(color='#888'), thickness=10))
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 2 — Distribuição geográfica
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Distribuição geográfica</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-title">Concentração por estado</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Participação de cada UF no total arrecadado</div>', unsafe_allow_html=True)
    dm = df.groupby('sigla_uf')['valor'].sum().sort_values(ascending=False).reset_index()
    dm['share'] = dm['valor'] / dm['valor'].sum() * 100
    dm['acum']  = dm['share'].cumsum()
    top = dm[dm['acum'].shift(1, fill_value=0) < 55]
    resto = pd.DataFrame([{
        'sigla_uf':'Demais',
        'valor': dm[~dm['sigla_uf'].isin(top['sigla_uf'])]['valor'].sum(),
        'share': dm[~dm['sigla_uf'].isin(top['sigla_uf'])]['share'].sum()
    }])
    df_pie = pd.concat([top[['sigla_uf','valor','share']], resto])
    fig3 = px.pie(df_pie, names='sigla_uf', values='valor', hole=0.38,
                  color_discrete_sequence=['#1b4332','#2d6a4f','#40916c','#52b788','#74c69d','#d8f3dc'])
    fig3.update_traces(textfont_size=11, textfont_color='white',
                       marker=dict(line=dict(color='#faf9f7', width=2)))
    fig3.update_layout(**PT, legend=dict(orientation='h', y=-0.1, font=dict(size=10)))
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown('<div class="chart-title">Crescimento 2022 → 2023 por UF</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Variação percentual entre os dois anos</div>', unsafe_allow_html=True)
    df_yy = df_completo[df_completo['ano'].isin([2022,2023])].groupby(['sigla_uf','ano'])['valor'].sum().reset_index()
    piv_yy = df_yy.pivot(index='sigla_uf', columns='ano', values='valor').dropna()
    if 2022 in piv_yy.columns and 2023 in piv_yy.columns:
        piv_yy['pct'] = ((piv_yy[2023]/piv_yy[2022])-1)*100
        piv_yy = piv_yy.reset_index().sort_values('pct', ascending=True)
        fig4 = go.Figure(go.Bar(
            x=piv_yy['pct'], y=piv_yy['sigla_uf'], orientation='h',
            marker_color=['#2d6a4f' if v >= 0 else '#9b2226' for v in piv_yy['pct']],
            marker_line_width=0,
            text=piv_yy['pct'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside', textfont=dict(color='#888', size=9)
        ))
        fig4.add_vline(x=0, line_color='#ccc', line_width=1)
        fig4.update_layout(**PT, margin=dict(t=20,b=20,l=50,r=60), xaxis_title='Variação (%)', yaxis_title='')
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Selecione um período que inclua 2022 e 2023.")

# ─────────────────────────────────────────────
# SEÇÃO 3 — Composição tributária
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Composição tributária</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="chart-title">IPI por setor — Autos, Bebidas e Fumo</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Evolução anual por categoria industrial</div>', unsafe_allow_html=True)
    df_ipi = df[df['BK_Tributo'].isin(['ipi_automoveis','ipi_bebidas','ipi_fumo'])]
    df_ipi_g = df_ipi.groupby(['ano','descricao'])['valor_B'].sum().reset_index()
    fig5 = px.line(df_ipi_g, x='ano', y='valor_B', color='descricao',
                   markers=True, color_discrete_sequence=['#2d6a4f','#e76f51','#264653'],
                   labels={'valor_B':'R$ Bi','ano':'','descricao':''})
    fig5.update_traces(line_width=2, marker_size=5)
    fig5.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.markdown('<div class="chart-title">Imposto de Importação por região</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Participação percentual do II no total de cada região</div>', unsafe_allow_html=True)
    df_ii   = df[df['BK_Tributo'] == 'imposto_importacao']
    tot_reg = df.groupby('regiao')['valor_B'].sum()
    ii_reg  = df_ii.groupby('regiao')['valor_B'].sum()
    pct_ii  = (ii_reg / tot_reg * 100).reset_index()
    pct_ii.columns = ['regiao','pct']
    pct_ii = pct_ii.sort_values('pct', ascending=True)
    fig6 = px.bar(pct_ii, x='pct', y='regiao', orientation='h',
                  color='pct', color_continuous_scale='Greens',
                  labels={'pct':'% do II','regiao':''},
                  text=pct_ii['pct'].apply(lambda x: f"{x:.1f}%"))
    fig6.update_traces(textposition='outside', textfont=dict(color='#888'))
    fig6.update_layout(**PT, coloraxis_showscale=False, margin=dict(t=20,b=20,l=90,r=60))
    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 4 — Sazonalidade e volatilidade
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
    fig7 = go.Figure(go.Bar(
        x=devs['nome_mes'], y=devs['desvio'],
        marker_color=['#2d6a4f' if v >= 0 else '#9b2226' for v in devs['desvio']],
        marker_line_width=0,
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
    fig8.update_layout(**PT, coloraxis_showscale=False, margin=dict(t=20,b=20,l=160,r=60))
    st.plotly_chart(fig8, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 5 — Setor econômico (CNAE)
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Setor econômico · CNAE</div>', unsafe_allow_html=True)
c9, c10 = st.columns(2)

with c9:
    st.markdown('<div class="chart-title">Top setores por arrecadação</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Contribuição acumulada de cada seção CNAE</div>', unsafe_allow_html=True)
    df_cnae_g = df_cnae_f.groupby('setor')['valor_B'].sum().reset_index()
    df_cnae_g = df_cnae_g.sort_values('valor_B', ascending=True).tail(12)
    fig9 = px.bar(df_cnae_g, x='valor_B', y='setor', orientation='h',
                  color='valor_B', color_continuous_scale='Greens',
                  labels={'valor_B':'R$ Bi','setor':''},
                  text=df_cnae_g['valor_B'].apply(lambda x: f"{x:.0f}"))
    fig9.update_traces(textposition='outside', textfont=dict(color='#888'))
    fig9.update_layout(**PT, coloraxis_showscale=False, margin=dict(t=20,b=20,l=160,r=60))
    st.plotly_chart(fig9, use_container_width=True)

with c10:
    st.markdown('<div class="chart-title">Evolução dos top 5 setores por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Trajetória anual dos setores com maior arrecadação</div>', unsafe_allow_html=True)
    top5_setores = df_cnae_f.groupby('setor')['valor_B'].sum().nlargest(5).index.tolist()
    df_cnae_top = df_cnae_f[df_cnae_f['setor'].isin(top5_setores)]
    df_cnae_evol = df_cnae_top.groupby(['ano','setor'])['valor_B'].sum().reset_index()
    fig10 = px.line(df_cnae_evol, x='ano', y='valor_B', color='setor',
                    markers=True, color_discrete_sequence=CORES,
                    labels={'valor_B':'R$ Bi','ano':'','setor':''})
    fig10.update_traces(line_width=2, marker_size=4)
    fig10.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig10, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 6 — IR/IPI Bruto vs Líquido
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">IR e IPI · bruto vs líquido</div>', unsafe_allow_html=True)
c11, c12 = st.columns(2)

with c11:
    st.markdown('<div class="chart-title">Arrecadação bruta vs líquida</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Impacto de restituições e compensações na receita final</div>', unsafe_allow_html=True)
    df_ir_g = df_ir_f.groupby(['ano','tributo'])[['bruto_B','liquido_B']].sum().reset_index()
    df_ir_melted = df_ir_g.melt(id_vars=['ano','tributo'], value_vars=['bruto_B','liquido_B'],
                                 var_name='tipo', value_name='valor_B')
    df_ir_melted['tipo'] = df_ir_melted['tipo'].map({'bruto_B':'Bruto','liquido_B':'Líquido'})
    fig11 = px.bar(df_ir_melted, x='ano', y='valor_B', color='tipo', barmode='group',
                   facet_col='tributo', color_discrete_sequence=['#264653','#2d6a4f'],
                   labels={'valor_B':'R$ Bi','ano':'','tipo':''})
    fig11.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig11, use_container_width=True)

with c12:
    st.markdown('<div class="chart-title">Restituições por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Volume devolvido aos contribuintes via restituição de IR e IPI</div>', unsafe_allow_html=True)
    df_rest = df_ir_f.groupby(['ano','tributo'])['restituicao_B'].sum().reset_index()
    fig12 = px.bar(df_rest, x='ano', y='restituicao_B', color='tributo', barmode='stack',
                   color_discrete_sequence=['#e76f51','#f4a261'],
                   labels={'restituicao_B':'R$ Bi','ano':'','tributo':''})
    fig12.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig12, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 7 — ITR por UF
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">ITR · Imposto Territorial Rural por UF</div>', unsafe_allow_html=True)
c13, c14 = st.columns(2)

with c13:
    st.markdown('<div class="chart-title">Top UFs em arrecadação de ITR</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Estados com maior arrecadação do imposto rural (R$ Milhões)</div>', unsafe_allow_html=True)
    df_itr_uf = df_itr_f.groupby('sigla_uf')['valor_B'].sum().reset_index()
    df_itr_uf = df_itr_uf.sort_values('valor_B', ascending=True).tail(10)
    fig13 = px.bar(df_itr_uf, x='valor_B', y='sigla_uf', orientation='h',
                   color='valor_B', color_continuous_scale='Greens',
                   labels={'valor_B':'R$ Milhões','sigla_uf':''},
                   text=df_itr_uf['valor_B'].apply(lambda x: f"{x:.0f}"))
    fig13.update_traces(textposition='outside', textfont=dict(color='#888'))
    fig13.update_layout(**PT, coloraxis_showscale=False, margin=dict(t=20,b=20,l=50,r=60))
    st.plotly_chart(fig13, use_container_width=True)

with c14:
    st.markdown('<div class="chart-title">Evolução do ITR por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Trajetória da arrecadação rural ao longo do tempo</div>', unsafe_allow_html=True)
    df_itr_ano = df_itr_f.groupby('ano')['valor_B'].sum().reset_index()
    fig14 = px.area(df_itr_ano, x='ano', y='valor_B',
                    color_discrete_sequence=['#52b788'],
                    labels={'valor_B':'R$ Milhões','ano':''})
    fig14.update_traces(line_color='#2d6a4f', fillcolor='#52b78844')
    fig14.update_layout(**PT)
    st.plotly_chart(fig14, use_container_width=True)

# ─────────────────────────────────────────────
# SEÇÃO 8 — Natureza Jurídica
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Arrecadação por natureza jurídica</div>', unsafe_allow_html=True)
c15, c16 = st.columns(2)

with c15:
    st.markdown('<div class="chart-title">Tipo de empresa · participação no total</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Como cada forma jurídica contribui para a arrecadação</div>', unsafe_allow_html=True)
    df_nj_g = df_nj_f.groupby('tipo')['valor_B'].sum().reset_index()
    df_nj_g = df_nj_g[df_nj_g['tipo'] != 'Outros'].sort_values('valor_B', ascending=False)
    fig15 = px.pie(df_nj_g, names='tipo', values='valor_B', hole=0.38,
                   color_discrete_sequence=px.colors.sequential.Greens_r)
    fig15.update_traces(textfont_size=10, textfont_color='white',
                        marker=dict(line=dict(color='#faf9f7', width=1)))
    fig15.update_layout(**PT, legend=dict(orientation='h', y=-0.15, font=dict(size=9)))
    st.plotly_chart(fig15, use_container_width=True)

with c16:
    st.markdown('<div class="chart-title">Evolução dos principais tipos por ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Trajetória dos tipos jurídicos com maior arrecadação</div>', unsafe_allow_html=True)
    top4_tipos = df_nj_f.groupby('tipo')['valor_B'].sum().nlargest(4).index.tolist()
    df_nj_top = df_nj_f[df_nj_f['tipo'].isin(top4_tipos)]
    df_nj_evol = df_nj_top.groupby(['ano','tipo'])['valor_B'].sum().reset_index()
    fig16 = px.line(df_nj_evol, x='ano', y='valor_B', color='tipo',
                    markers=True, color_discrete_sequence=CORES,
                    labels={'valor_B':'R$ Bi','ano':'','tipo':''})
    fig16.update_traces(line_width=2, marker_size=4)
    fig16.update_layout(**PT, legend=dict(orientation='h', y=-0.22, font=dict(size=10), title=None))
    st.plotly_chart(fig16, use_container_width=True)

# ─────────────────────────────────────────────
# SÍNTESE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Síntese analítica</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""<div class="finding">
        <div class="finding-num">01 · Achados</div>
        <div class="finding-title">Sudeste concentra mais da metade da receita</div>
        <div class="finding-body">SP e RJ respondem por mais de 50% da arrecadação federal.
        O IRPJ e o COFINS lideram em volume absoluto. O IPI-Combustíveis apresenta
        a maior volatilidade histórica, com quedas em 2020 e 2022.</div>
    </div>""", unsafe_allow_html=True)

with s2:
    st.markdown("""<div class="finding">
        <div class="finding-num">02 · Interpretações</div>
        <div class="finding-title">Sazonalidade consistente entre os anos</div>
        <div class="finding-body">Janeiro e março concentram os maiores volumes todos os anos,
        reflexo do ajuste anual do IRPJ. O setor Financeiro (K) e Indústria de Transformação (C)
        dominam a arrecadação por CNAE.</div>
    </div>""", unsafe_allow_html=True)

with s3:
    st.markdown("""<div class="finding">
        <div class="finding-num">03 · Recomendações</div>
        <div class="finding-title">Monitorar combustíveis como indicador antecipado</div>
        <div class="finding-body">CIDE-Combustíveis deve ser acompanhado como proxy de choques
        econômicos. O volume de restituições de IR cresce ano a ano — monitorar sua evolução
        é essencial para projeções de receita líquida.</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="footer">
    Fonte: Receita Federal do Brasil via Base dos Dados · Projeto Mensal BI · {ano_min}–{ano_max}
</div>""", unsafe_allow_html=True)
