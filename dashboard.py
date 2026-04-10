import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import requests
import os

# ==========================================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Mapa das Forças", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🤖 INTEGRAÇÃO COM IA (VERSÃO SEGURA PARA GITHUB)
# ==========================================
def analisar_com_ia(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "❌ Erro: Chave de API não configurada no painel do Streamlit Cloud (Settings > Secrets)."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": "Você é um consultor executivo de RH especialista nas 24 forças de caráter (VIA Institute). Sua função é explicar a leitura de gráficos para gestores. Seja extremamente didático, direto e use linguagem simples. Responda em no máximo 2 a 3 parágrafos curtos."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Erro na análise da IA: {e}"

# ==========================================
# 🎨 DICIONÁRIO DE VIRTUDES E CORES ATUALIZADO
# ==========================================
COR_VIRTUDES = {
    # Sabedoria: #314A75
    "Amor ao Aprendizado": "#314A75", "Critério": "#314A75", "Perspectiva": "#314A75", "Curiosidade": "#314A75", "Criatividade": "#314A75",
    # Coragem: #FF0000
    "Bravura": "#FF0000", "Perseverança": "#FF0000", "Vitalidade": "#FF0000", "Integridade": "#FF0000",
    # Humanidade: #FF3399
    "Amor": "#FF3399", "Inteligência Social": "#FF3399", "Generosidade": "#FF3399",
    # Justiça: #663300
    "Liderança": "#663300", "Trabalho em Equipe": "#663300", "Equidade": "#663300","Justiça": "#663300","Justiça (Imparcialidade)": "#663300",
    # Temperança: #593190
    "Humildade": "#593190", "Prudência": "#593190", "Perdão": "#593190", "Autocontrole": "#593190",
    # Transcendência: #00CC66
    "Apreciação da Beleza e Excelência": "#00CC66", "Apreciação da Beleza": "#00CC66", "Humor": "#00CC66", "Espiritualidade": "#00CC66", "Esperança": "#00CC66", "Gratidão": "#00CC66"
}

MAPA_COR_FORCA = {forca: COR_VIRTUDES.get(forca, "#A0AEC0") for forca in COR_VIRTUDES.keys()}

def get_cor(forca):
    return MAPA_COR_FORCA.get(forca, "#A0AEC0")

# ==========================================
# 🎨 INJEÇÃO DE CSS AVANÇADO
# ==========================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
.stApp { background-color: #F4F5F7 !important; font-family: 'Inter', sans-serif !important; }
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 95% !important; }
.header-container { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.header-title { font-size: 26px; font-weight: 700; color: #2D3748; margin: 0; display: flex; align-items: center; gap: 10px; }
.header-sub { font-size: 14px; color: #718096; margin-top: 4px; margin-left: 35px; }
.virtue-badge-container { display: flex; flex-wrap: wrap; gap: 10px; margin-left: 35px; margin-bottom: 25px; margin-top: 10px;}
.virtue-badge { padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.5px;}
.kpi-row { display: flex; gap: 15px; margin-bottom: 20px; }
.kpi-card { background: #FFFFFF; border-radius: 12px; padding: 15px 20px; flex: 1; box-shadow: 0px 2px 5px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; display: flex; flex-direction: column; justify-content: space-between; position: relative;}
.kpi-header { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #4A5568; margin-bottom: 10px; }
.kpi-value { font-size: 36px; font-weight: 700; color: #1A202C; line-height: 1.1; }
.kpi-value-small { font-size: 24px; font-weight: 700; color: #1A202C; line-height: 1.1; margin-top: 10px; }
.kpi-text-label { font-size: 18px; font-weight: 700; margin-top: 10px; }
div[data-testid="stPlotlyChart"] > div { background-color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #E2E8F0 !important; box-shadow: 0px 2px 5px rgba(0,0,0,0.02) !important; padding-top: 5px;}
.stButton > button { border-radius: 8px; border: 1px solid #3182CE; color: #3182CE; font-weight: 600; }
.stButton > button:hover { background-color: #EBF8FF; border-color: #3182CE; color: #3182CE;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================
@st.cache_data(ttl=60)
def carregar_dados():
    nome_arquivo = "TREINAMENTO_ FORCAS_QUIPES_BD.xlsx"
    caminho_local = r"C:\Users\ELYOMIDSON.BRANDAO\OneDrive - Canel Grauna Lavoro\Documentos\python-projetos\TREINAMENTO FORCA EQUIPE\\" + nome_arquivo
    
    caminho_final = caminho_local if os.path.exists(caminho_local) else nome_arquivo
    
    try:
        df = pd.read_excel(caminho_final)
        df.columns = [str(c).strip() for c in df.columns]
        
        if 'TURMA' in df.columns: df.rename(columns={'TURMA': 'Turma'}, inplace=True)
        if 'Top 1' in df.columns: df.rename(columns={'Top 1': 'Força_Top1'}, inplace=True)
        
        for col in ['Setor', 'Cargo', 'Gestor', 'Turma']:
            if col in df.columns:
                df[col] = df[col].fillna("Não Informado")
            else:
                df[col] = "Não Informado"
        
        df = df.dropna(subset=['Força_Top1']) 
        
        substituicoes = {
            'Criativadade': 'Criatividade', 'Perdão ': 'Perdão', 
            'Lierança': 'Liderança', 'Amor ': 'Amor', 
            'Apreciação da Beleza ': 'Apreciação da Beleza', 'Critério ': 'Critério'
        }
        
        for col in df.columns:
            if 'Top ' in col or col == 'Força_Top1':
                df[col] = df[col].astype(str).str.strip().replace(substituicoes)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao ler a planilha: {e}")
        return pd.DataFrame()

@st.cache_data
def preparar_dados_dispersao(df):
    colunas_top = [c for c in df.columns if 'Top ' in c or c == 'Força_Top1']
    id_vars = [c for c in ['Colaborador', 'Turma', 'Setor', 'Cargo', 'Gestor'] if c in df.columns]
    df_melt = df.melt(id_vars=id_vars, value_vars=colunas_top, var_name='Posicao', value_name='Força')
    df_melt = df_melt.dropna(subset=['Força'])
    df_melt = df_melt[df_melt['Força'] != 'nan']
    df_melt['Posicao_Rank'] = df_melt['Posicao'].replace('Força_Top1', 'Top 1').str.extract(r'(\d+)').astype(float)
    return df_melt

df_completo = carregar_dados()

if df_completo.empty:
    st.stop()

# ==========================================
# 📐 CABEÇALHO COM CORES ATUALIZADAS
# ==========================================
st.markdown("""
<div class="header-container">
    <div>
        <h1 class="header-title"><i class="fa-solid fa-layer-group" style="color: #A0AEC0;"></i> Mapa das Forças Pessoais</h1>
        <div class="header-sub">Análise baseada na estrutura de 6 Virtudes Universais do VIA Institute</div>
        <div class="virtue-badge-container">
            <span class="virtue-badge" style="background-color: #314A75;">SABEDORIA</span>
            <span class="virtue-badge" style="background-color: #FF0000;">CORAGEM</span>
            <span class="virtue-badge" style="background-color: #FF3399;">HUMANIDADE</span>
            <span class="virtue-badge" style="background-color: #663300;">JUSTIÇA</span>
            <span class="virtue-badge" style="background-color: #593190;">TEMPERANÇA</span>
            <span class="virtue-badge" style="background-color: #00CC66;">TRANSCENDÊNCIA</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 🎛️ FILTROS MULTIPLOS NA TELA PRINCIPAL
# ==========================================
st.markdown('<h4><i class="fa-solid fa-filter" style="color:#3182CE;"></i> Filtros de Análise</h4>', unsafe_allow_html=True)

turmas_unicas = sorted([str(x) for x in df_completo["Turma"].unique()])
setores_unicos = sorted([str(x) for x in df_completo["Setor"].unique()])
cargos_unicos = sorted([str(x) for x in df_completo["Cargo"].unique()])
gestores_unicos = sorted([str(x) for x in df_completo["Gestor"].unique()])

col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    filtro_turma = st.multiselect("🎓 Turma", turmas_unicas, placeholder="Filtrar Turmas...")
with col_f2:
    filtro_setor = st.multiselect("🏢 Setor", setores_unicos, placeholder="Filtrar Setores...")
with col_f3:
    filtro_gestor = st.multiselect("👤 Gestor", gestores_unicos, placeholder="Filtrar Gestores...")
with col_f4:
    filtro_cargo = st.multiselect("💼 Cargo", cargos_unicos, placeholder="Filtrar Cargos...")

st.markdown("<br>", unsafe_allow_html=True) 

df_filtrado = df_completo.copy()
if filtro_turma: df_filtrado = df_filtrado[df_filtrado["Turma"].astype(str).isin(filtro_turma)]
if filtro_setor: df_filtrado = df_filtrado[df_filtrado["Setor"].astype(str).isin(filtro_setor)]
if filtro_gestor: df_filtrado = df_filtrado[df_filtrado["Gestor"].astype(str).isin(filtro_gestor)]
if filtro_cargo: df_filtrado = df_filtrado[df_filtrado["Cargo"].astype(str).isin(filtro_cargo)]

# ==========================================
# 📊 PROCESSAMENTO INTELIGENTE: VISÃO TOP 5
# ==========================================
colunas_top5 = ['Força_Top1', 'Top 2', 'Top 3', 'Top 4', 'Top 5']
colunas_presentes = [c for c in colunas_top5 if c in df_filtrado.columns]
id_vars_melt = [c for c in ['Turma', 'Setor', 'Cargo', 'Gestor', 'Colaborador'] if c in df_filtrado.columns]

df_top5_melted = df_filtrado.melt(
    id_vars=id_vars_melt, 
    value_vars=colunas_presentes, 
    value_name='Forca_Ativa'
)
df_top5_melted = df_top5_melted.dropna(subset=['Forca_Ativa'])
df_top5_melted = df_top5_melted[df_top5_melted['Forca_Ativa'].str.strip() != '']

# ==========================================
# 📊 CÁLCULO DE KPIs
# ==========================================
total_pessoas = len(df_filtrado)

if total_pessoas == 0:
    st.warning("Nenhum colaborador atende aos filtros selecionados.")
    st.stop()

forcas_distintas = df_top5_melted["Forca_Ativa"].nunique()
top_forca = df_filtrado["Força_Top1"].mode()[0] if not df_filtrado.empty else "N/A"
cor_kpi = get_cor(top_forca) 

ratio = forcas_distintas / 24
if ratio >= 0.9: label_eq, cor_eq, angulo = "Excelente", "#38A169", 160
elif ratio >= 0.7: label_eq, cor_eq, angulo = "Médio-Alto", "#48BB78", 120
elif ratio >= 0.4: label_eq, cor_eq, angulo = "Médio", "#ECC94B", 80
else: label_eq, cor_eq, angulo = "Baixo", "#E53E3E", 30

rad = np.deg2rad(angulo)
x_ponta = 50 + 35 * np.cos(np.pi - rad)
y_ponta = 45 - 35 * np.sin(np.pi - rad)

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card"><div class="kpi-header"><i class="fa-solid fa-user-group" style="color:#3182CE;"></i> Pessoas (Amostra)</div><div class="kpi-value">{total_pessoas}</div></div>
    <div class="kpi-card"><div class="kpi-header"><i class="fa-solid fa-users" style="color:#E53E3E;"></i> Forças (Top 5) Distintas</div><div class="kpi-value">{forcas_distintas} <span style="font-size:20px; color:#A0AEC0;">/ 24</span></div></div>
    <div class="kpi-card"><div class="kpi-header"><i class="fa-solid fa-trophy" style="color:{cor_kpi};"></i> Força Dominante (Top 1)</div><div class="kpi-value-small" style="color:{cor_kpi};">{top_forca}</div></div>
    <div class="kpi-card" style="flex-direction:row; align-items:center;">
        <div><div class="kpi-header"><i class="fa-solid fa-scale-balanced" style="color:#DD6B20;"></i> Equilíbrio Global</div><div class="kpi-text-label" style="color:{cor_eq};">{label_eq}</div></div>
        <svg width="80" height="50" viewBox="0 0 100 50">
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#E2E8F0" stroke-width="12" />
            <path d="M 10 50 A 40 40 0 0 1 30 20" fill="none" stroke="#E53E3E" stroke-width="12" opacity="0.3" />
            <path d="M 30 20 A 40 40 0 0 1 70 20" fill="none" stroke="#ECC94B" stroke-width="12" opacity="0.3" />
            <path d="M 70 20 A 40 40 0 0 1 90 50" fill="none" stroke="#38A169" stroke-width="12" opacity="0.3" />
            <line x1="50" y1="45" x2="{x_ponta}" y2="{y_ponta}" stroke="#2D3748" stroke-width="3" stroke-linecap="round" />
            <circle cx="50" cy="45" r="4" fill="#2D3748" />
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📈 LINHA 1: RANKING E DISTRIBUIÇÃO (TOP 5)
# ==========================================
col1, col2 = st.columns([1.2, 1], gap="medium")

with col1:
    ranking = df_top5_melted["Forca_Ativa"].value_counts().head(10).reset_index()
    ranking.columns = ["Força", "Quantidade"]
    ranking_inv = ranking.iloc[::-1] 
    
    fig_bar = go.Figure()
    for _, row in ranking_inv.iterrows():
        cor_barra = get_cor(row["Força"]) 
        fig_bar.add_trace(go.Bar(
            y=[row["Força"]], x=[row["Quantidade"]], orientation='h', marker_color=cor_barra,
            text=f"<b>{row['Quantidade']}</b>", textposition='inside', insidetextanchor='end', textfont=dict(color='white', size=13), showlegend=False, width=0.6 
        ))
        fig_bar.add_annotation(y=row["Força"], x=row["Quantidade"] + (total_pessoas*0.05), text=str(row["Quantidade"]), showarrow=False, font=dict(color="#A0AEC0", size=13), xanchor="left")

    fig_bar.update_layout(
        title=dict(text='<b>📊 Top Forças por Frequência (Análise do Top 5)</b>', font=dict(size=16, color='#2D3748'), x=0.05, y=0.95),
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', height=400, margin=dict(l=150, r=40, t=60, b=10), 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, tickfont=dict(color="#4A5568", size=12), automargin=True)
    )
    st.plotly_chart(fig_bar, use_container_width=True, theme=None, config={'displayModeBar': False})
    
    with st.expander("🤖 IA: Explicar o gráfico Top Forças"):
        if st.button("Gerar Análise das Forças", key="btn_ia_bar"):
            top_3 = ", ".join(ranking["Força"].head(3).tolist())
            prompt = f"O gráfico mostra as forças predominantes considerando o Top 5 de {total_pessoas} pessoas. As 3 principais são: {top_3}. O que isso revela sobre o potencial do time?"
            with st.spinner("Analisando perfil..."):
                st.write(analisar_com_ia(prompt))

with col2:
    donut_data = df_top5_melted["Forca_Ativa"].value_counts().head(6)
    cores_donut = [get_cor(f) for f in donut_data.index]
    total_total_forcas = len(df_top5_melted)
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=donut_data.index, values=donut_data.values, hole=0.65, textinfo='none', 
        marker=dict(colors=cores_donut, line=dict(color='#FFFFFF', width=2))
    )])

    fig_pie.add_annotation(x=0.5, y=0.5, text=str(total_pessoas), font=dict(size=42, color='#1A202C', weight="bold"), showarrow=False, xanchor="center")
    fig_pie.add_annotation(x=0.5, y=0.38, text="Pessoas", font=dict(size=14, color='#718096'), showarrow=False, xanchor="center")

    fig_pie.update_layout(
        title=dict(text='<b>🔍 Distribuição Principal (Análise do Top 5)</b>', font=dict(size=16, color='#2D3748'), x=0.05, y=0.95),
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', height=400, margin=dict(l=10, r=30, t=60, b=20), 
        showlegend=True, legend=dict(orientation="v", x=0.85, y=0.5, font=dict(size=12, color='#4A5568'))
    )
    st.plotly_chart(fig_pie, use_container_width=True, theme=None, config={'displayModeBar': False})

# ==========================================
# 🧠 LINHA 2: RADAR E PONTOS CEGOS
# ==========================================
st.write("") 
col3, col4 = st.columns([1, 1.2], gap="medium")

with col3:
    categorias = df_top5_melted["Forca_Ativa"].value_counts().head(6).index.tolist()
    valores_equipe = df_top5_melted["Forca_Ativa"].value_counts().head(6).values.tolist()
    if len(categorias) > 2:
        valores_media = [np.mean(valores_equipe) * 0.9 for _ in categorias] 
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=valores_equipe + [valores_equipe[0]], theta=categorias + [categorias[0]], fill='toself', name='Sua Equipe', line_color='#3182CE'))
        fig_radar.add_trace(go.Scatterpolar(r=valores_media + [valores_media[0]], theta=categorias + [categorias[0]], fill='toself', name='Média Global', line_color='#A0AEC0', opacity=0.5))
        fig_radar.update_layout(
            title=dict(text='<b>🕸️ Perfil Sinergético (Radar do Top 5)</b>', font=dict(size=16, color='#2D3748'), x=0.05, y=0.95),
            polar=dict(radialaxis=dict(visible=False, range=[0, max(valores_equipe)*1.2])),
            paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', height=380, margin=dict(l=40, r=40, t=70, b=30),
            showlegend=True, legend=dict(orientation="h", y=-0.1, x=0.1)
        )
        st.plotly_chart(fig_radar, use_container_width=True, theme=None, config={'displayModeBar': False})
    else:
        st.info("💡 Poucas forças para gerar o Radar de Sinergia.")

with col4:
    df_melted_all = preparar_dados_dispersao(df_filtrado)
    if not df_melted_all.empty:
        df_bottom = df_melted_all[df_melted_all['Posicao_Rank'] >= 20]
        if not df_bottom.empty:
            bottom_counts = df_bottom['Força'].value_counts().head(6).reset_index()
            bottom_counts.columns = ["Força", "Quantidade"]
            bottom_counts_inv = bottom_counts.iloc[::-1] 
            
            fig_bottom = go.Figure()
            for _, row in bottom_counts_inv.iterrows():
                cor_barra = get_cor(row["Força"])
                fig_bottom.add_trace(go.Bar(
                    y=[row["Força"]], x=[row["Quantidade"]], orientation='h', marker_color=cor_barra,
                    text=f"<b>{row['Quantidade']}</b>", textposition='inside', insidetextanchor='end', textfont=dict(color='white', size=13), showlegend=False, width=0.6 
                ))
                fig_bottom.add_annotation(y=row["Força"], x=row["Quantidade"] + (total_pessoas*0.02), text=str(row["Quantidade"]), showarrow=False, font=dict(color="#A0AEC0", size=13), xanchor="left")
            fig_bottom.update_layout(
                title=dict(text='<b>Forças Bottom da Equipe</b>', font=dict(size=16, color='#2D3748'), x=0.05, y=0.95),
                paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', height=380, margin=dict(l=150, r=40, t=80, b=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, tickfont=dict(size=12), automargin=True)
            )
            st.plotly_chart(fig_bottom, use_container_width=True, theme=None, config={'displayModeBar': False})

# ==========================================
# 🔥 LINHA 3: MAPA DE CALOR
# ==========================================
st.write("---") 
st.markdown("### 🔥 Mapa de Calor: Forças (Top 5) vs. Turmas")
if not df_top5_melted.empty:
    top_forcas_heat = df_top5_melted["Forca_Ativa"].value_counts().head(8).index.tolist()
    df_heat = df_top5_melted[df_top5_melted["Forca_Ativa"].isin(top_forcas_heat)]
    tabela_cruzada = pd.crosstab(df_heat["Forca_Ativa"], df_heat["Turma"])
    tabela_cruzada = tabela_cruzada.reindex(top_forcas_heat)
    if not tabela_cruzada.empty:
        fig_heat = go.Figure(data=go.Heatmap(
            z=tabela_cruzada.values, x=tabela_cruzada.columns, y=tabela_cruzada.index,
            colorscale=[[0, '#F7FAFC'], [0.5, '#90CDF4'], [1, '#3182CE']],
            text=tabela_cruzada.values, texttemplate="<b>%{text}</b>",
            textfont={"size":14, "color":"#1A202C"}, showscale=False, xgap=3, ygap=3
        ))
        fig_heat.update_layout(
            paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', height=350, margin=dict(l=150, r=40, t=20, b=40),
            yaxis=dict(autorange="reversed", tickfont=dict(size=13)), xaxis=dict(tickfont=dict(size=13), side="bottom")
        )
        st.plotly_chart(fig_heat, use_container_width=True, theme=None, config={'displayModeBar': False})

# ==========================================
# 📋 TABELA DE DADOS (VISÃO DETALHADA)
# ==========================================
st.write("---") 
st.markdown("### 📋 Visão Detalhada dos Colaboradores")
colunas_tabela = ['Turma', 'Colaborador', 'Gestor', 'Setor', 'Cargo', 'Força_Top1', 'Top 2', 'Top 3', 'Top 4', 'Top 5']
colunas_disponiveis = [col for col in colunas_tabela if col in df_filtrado.columns]
df_tabela = df_filtrado[colunas_disponiveis].copy()
if 'Força_Top1' in df_tabela.columns: df_tabela = df_tabela.rename(columns={'Força_Top1': 'Top 1'})
df_tabela = df_tabela.reset_index(drop=True)
df_tabela.index += 1 
st.dataframe(df_tabela, use_container_width=True)
