import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from branca.colormap import LinearColormap

# ─────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Mapa de Violência no Brasil",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .stMetric { background-color: #f8f9fa; border-radius: 8px; padding: 10px; }
    h1 { color: #1a1a2e; }
    .fonte-nota { font-size: 0.75rem; color: #888; margin-top: 5px; }
    .badge-ano {
        background: #e74c3c; color: white; padding: 2px 10px;
        border-radius: 12px; font-size: 0.8rem; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DADOS
# ─────────────────────────────────────────
@st.cache_data
def carregar_dados():
    dados = {
        'estado': [
            'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia',
            'Ceará', 'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
            'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará', 'Paraíba',
            'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro', 'Rio Grande do Norte',
            'Rio Grande do Sul', 'Rondônia', 'Roraima', 'Santa Catarina', 'São Paulo',
            'Sergipe', 'Tocantins'
        ],
        'sigla': [
            'AC', 'AL', 'AP', 'AM', 'BA',
            'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB',
            'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP',
            'SE', 'TO'
        ],
        'regiao': [
            'Norte', 'Nordeste', 'Norte', 'Norte', 'Nordeste',
            'Nordeste', 'Centro-Oeste', 'Sudeste', 'Centro-Oeste', 'Nordeste',
            'Centro-Oeste', 'Centro-Oeste', 'Sudeste', 'Norte', 'Nordeste',
            'Sul', 'Nordeste', 'Nordeste', 'Sudeste', 'Nordeste',
            'Sul', 'Norte', 'Norte', 'Sul', 'Sudeste',
            'Nordeste', 'Norte'
        ],
        'taxa_homicidios': [
            31.2, 38.4, 39.7, 25.1, 24.3,
            29.8, 19.4, 23.7, 24.1, 27.6,
            28.9, 25.4, 12.8, 31.4, 26.7,
            16.2, 28.3, 17.9, 24.5, 38.9,
            14.7, 29.8, 41.2, 9.1, 8.4,
            37.1, 25.8
        ],
        'taxa_homicidios_mulheres': [
            8.2, 9.1, 10.3, 5.8, 5.4,
            6.9, 4.2, 5.6, 5.9, 7.1,
            7.4, 6.1, 2.9, 7.8, 6.3,
            3.8, 6.7, 4.1, 5.2, 9.4,
            3.4, 7.2, 11.1, 2.1, 1.9,
            9.8, 6.1
        ],
        'taxa_roubos': [
            412, 891, 623, 756, 534,
            489, 1243, 867, 678, 312,
            445, 567, 723, 589, 423,
            634, 712, 234, 1876, 567,
            812, 389, 478, 543, 1123,
            678, 356
        ],
        'perc_vitimas_negras': [
            71, 88, 74, 69, 82,
            79, 62, 71, 65, 80,
            63, 59, 72, 75, 78,
            48, 76, 81, 67, 77,
            34, 62, 68, 31, 55,
            84, 70
        ]
    }
    return pd.DataFrame(dados)

@st.cache_data
def carregar_geojson():
    import requests
    url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    r = requests.get(url, timeout=10)
    return r.json()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Mapa de Violência")
    st.markdown("**Brasil · Dados 2023**")
    st.markdown("---")

    camada = st.radio(
        "📊 Indicador",
        options=["🔴 Homicídios Gerais", "🟣 Violência contra Mulheres", "🟡 Roubos"],
        index=0
    )

    st.markdown("---")
    st.markdown("**🔍 Filtrar por Região**")
    regioes = ["Todas", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
    regiao_filtro = st.selectbox("Região", regioes)

    st.markdown("---")
    st.markdown("**📋 Sobre os dados**")
    st.markdown("""
    <div class='fonte-nota'>
    🔴 Homicídios: Atlas da Violência 2025 (IPEA/FBSP)<br>
    🟣 Feminicídio: Atlas da Violência 2025 (IPEA/FBSP)<br>
    🟡 Roubos: Anuário Seg. Pública 2024 (FBSP)<br><br>
    ⚠️ Ano base dos dados: <b>2023</b><br>
    Dados com defasagem de ~2 anos é padrão nacional — mesmo utilizado pelo IPEA.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class='fonte-nota'>
    Projeto open source · <a href='https://github.com' target='_blank'>Ver no GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────
col_titulo, col_badge = st.columns([6, 1])
with col_titulo:
    st.markdown("# 🗺️ Mapa de Violência no Brasil")
    st.markdown("Visualização interativa de indicadores de segurança pública por estado")
with col_badge:
    st.markdown("<br><span class='badge-ano'>Dados 2023</span>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────
# CARREGAR DADOS
# ─────────────────────────────────────────
df = carregar_dados()

if regiao_filtro != "Todas":
    df_filtrado = df[df['regiao'] == regiao_filtro]
else:
    df_filtrado = df.copy()

# ─────────────────────────────────────────
# MÉTRICAS NO TOPO
# ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

estados_exibidos = len(df_filtrado)
with col1:
    st.metric("Estados analisados", f"{estados_exibidos} / 27")
with col2:
    media_hom = df_filtrado['taxa_homicidios'].mean()
    pior_hom = df_filtrado.loc[df_filtrado['taxa_homicidios'].idxmax(), 'sigla']
    st.metric("Média homicídios (seleção)", f"{media_hom:.1f} / 100 mil", f"Maior: {pior_hom}")
with col3:
    media_mul = df_filtrado['taxa_homicidios_mulheres'].mean()
    st.metric("Média homicídios femininos", f"{media_mul:.1f} / 100 mil mulheres")
with col4:
    media_rob = df_filtrado['taxa_roubos'].mean()
    st.metric("Média roubos (seleção)", f"{media_rob:.0f} / 100 mil")

st.markdown("---")

# ─────────────────────────────────────────
# MAPA + TABELA LADO A LADO
# ─────────────────────────────────────────
col_mapa, col_tabela = st.columns([3, 1])

with col_mapa:
    # Definir coluna e cores por camada selecionada
    config_camadas = {
        "🔴 Homicídios Gerais": {
            "col": "taxa_homicidios",
            "label": "Taxa de Homicídios por 100 mil hab.",
            "colors": ['#FFEDA0', '#FEB24C', '#F03B20', '#BD0026'],
            "unidade": "por 100 mil hab."
        },
        "🟣 Violência contra Mulheres": {
            "col": "taxa_homicidios_mulheres",
            "label": "Taxa de Homicídios Femininos por 100 mil mulheres",
            "colors": ['#EDE7F6', '#B39DDB', '#7B1FA2', '#4A148C'],
            "unidade": "por 100 mil mulheres"
        },
        "🟡 Roubos": {
            "col": "taxa_roubos",
            "label": "Taxa de Roubos por 100 mil hab.",
            "colors": ['#FFFDE7', '#FFF176', '#F9A825', '#E65100'],
            "unidade": "por 100 mil hab."
        }
    }

    cfg = config_camadas[camada]
    col_dados = cfg["col"]

    try:
        geojson = carregar_geojson()

        mapa = folium.Map(
            location=[-15.0, -52.0],
            zoom_start=4,
            tiles='CartoDB positron',
            prefer_canvas=True
        )

        colormap = LinearColormap(
            colors=cfg["colors"],
            vmin=df[col_dados].min(),
            vmax=df[col_dados].max(),
            caption=cfg["label"]
        )
        colormap.add_to(mapa)

        df_dict = df.set_index('sigla').to_dict('index')

        for feature in geojson['features']:
            sigla = feature['properties'].get('sigla', '')
            if sigla in df_dict:
                info = df_dict[sigla]
                valor = info[col_dados]
                cor = colormap(valor)

                # Destaque se fora do filtro de região
                opacity = 0.75 if (regiao_filtro == "Todas" or info['regiao'] == regiao_filtro) else 0.15

                popup_html = f"""
                <div style='font-family: Arial; font-size: 13px; min-width: 210px; padding: 10px;'>
                    <b style='font-size:15px'>📍 {info['estado']} ({sigla})</b>
                    <hr style='margin:6px 0; border-color:#eee'>
                    🔴 Homicídios gerais: <b>{info['taxa_homicidios']}</b>/100mil<br>
                    🟣 Homicídios femininos: <b>{info['taxa_homicidios_mulheres']}</b>/100mil<br>
                    🟡 Roubos: <b>{info['taxa_roubos']}</b>/100mil<br>
                    ⚫ Vítimas negras: <b>{info['perc_vitimas_negras']}%</b><br>
                    <hr style='margin:6px 0; border-color:#eee'>
                    <small style='color:#999'>
                        Fontes: Atlas Violência 2025 (IPEA/FBSP)<br>
                        Anuário Seg. Pública 2024 · Ano base: 2023
                    </small>
                </div>
                """

                folium.GeoJson(
                    feature,
                    style_function=lambda x, cor=cor, op=opacity: {
                        'fillColor': cor,
                        'color': '#666',
                        'weight': 1,
                        'fillOpacity': op
                    },
                    highlight_function=lambda x: {
                        'weight': 3,
                        'color': '#222',
                        'fillOpacity': 0.95
                    },
                    tooltip=folium.Tooltip(popup_html)
                ).add_to(mapa)

        st_folium(mapa, width=None, height=520, returned_objects=[])

    except Exception as e:
        st.error(f"Erro ao carregar o mapa: {e}. Verifique sua conexão com a internet.")

with col_tabela:
    st.markdown(f"**📊 Ranking — {camada}**")

    df_rank = df_filtrado[['estado', 'sigla', col_dados]].sort_values(col_dados, ascending=False).reset_index(drop=True)
    df_rank.index += 1
    df_rank.columns = ['Estado', 'UF', cfg["unidade"]]

    # Colorir células
    def colorir(val):
        maximo = df_rank[cfg["unidade"]].max()
        minimo = df_rank[cfg["unidade"]].min()
        ratio = (val - minimo) / (maximo - minimo) if maximo != minimo else 0
        r = int(255 * ratio)
        g = int(255 * (1 - ratio))
        return f'background-color: rgba({r},{g},80,0.3)'

    st.dataframe(
        df_rank[['UF', cfg["unidade"]]].style.applymap(colorir, subset=[cfg["unidade"]]),
        height=500,
        use_container_width=True
    )

# ─────────────────────────────────────────
# ANÁLISE DE INTERSECCIONALIDADE
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔬 Análise de Interseccionalidade")
st.caption("Relação entre homicídios femininos, % de vítimas negras e taxa geral de homicídios")

import plotly.express as px

fig = px.scatter(
    df_filtrado,
    x='taxa_homicidios_mulheres',
    y='perc_vitimas_negras',
    size='taxa_homicidios',
    color='taxa_homicidios',
    text='sigla',
    color_continuous_scale='RdYlGn_r',
    labels={
        'taxa_homicidios_mulheres': 'Homicídios femininos (por 100 mil mulheres)',
        'perc_vitimas_negras': '% de vítimas negras nos homicídios',
        'taxa_homicidios': 'Taxa geral de homicídios'
    },
    title='',
    hover_data={'estado': True, 'sigla': False}
)

fig.update_traces(textposition='top center', textfont_size=10)
fig.update_layout(
    height=420,
    plot_bgcolor='#fafafa',
    coloraxis_colorbar_title="Taxa<br>homicídios",
    margin=dict(l=20, r=20, t=20, b=40)
)

# Linhas de média
fig.add_hline(y=df_filtrado['perc_vitimas_negras'].mean(),
              line_dash="dash", line_color="gray", opacity=0.5,
              annotation_text="Média % vítimas negras")
fig.add_vline(x=df_filtrado['taxa_homicidios_mulheres'].mean(),
              line_dash="dash", line_color="purple", opacity=0.5,
              annotation_text="Média feminicídio")

st.plotly_chart(fig, use_container_width=True)
st.caption("💡 **Como ler:** Estados no canto superior direito têm alta violência contra mulheres E alta proporção de vítimas negras. Bolhas maiores = maior taxa geral de homicídios.")

# ─────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #aaa; font-size: 0.78rem; padding: 10px 0'>
    🗺️ Mapa de Violência no Brasil · Projeto open source<br>
    Dados: Atlas da Violência 2025 (IPEA/FBSP) · Anuário Brasileiro de Segurança Pública 2024 · Ano base: 2023<br>
    <a href='https://github.com' target='_blank'>GitHub</a> · Contribuições são bem-vindas
</div>
""", unsafe_allow_html=True)
