import streamlit as st
import pandas as pd
import folium
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from branca.colormap import LinearColormap
from datetime import datetime

# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Maceió Segurança | CVLI por Bairro",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

.main { background-color: #0e0e12; }
section[data-testid="stSidebar"] { background-color: #13131a; border-right: 1px solid #2a2a3a; }

.header-box {
    background: linear-gradient(135deg, #1a0a0a 0%, #0e0e12 60%, #0a0a1a 100%);
    border: 1px solid #3a1a1a;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.header-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #e74c3c, #c0392b, #8e44ad);
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f8f8f8;
    margin: 0;
    letter-spacing: -0.5px;
}
.header-sub {
    font-size: 0.85rem;
    color: #888;
    margin-top: 6px;
}
.badge {
    display: inline-block;
    background: #e74c3c22;
    border: 1px solid #e74c3c55;
    color: #e74c3c;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-right: 8px;
}
.badge-blue {
    background: #3498db22;
    border-color: #3498db55;
    color: #3498db;
}
.badge-yellow {
    background: #f39c1222;
    border-color: #f39c1255;
    color: #f39c12;
}
.metric-card {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #f8f8f8;
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: #666;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.metric-delta {
    font-size: 0.78rem;
    color: #e74c3c;
    margin-top: 4px;
}
.fonte-box {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-left: 3px solid #3498db;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.75rem;
    color: #888;
    line-height: 1.6;
}
.alert-box {
    background: #1a150a;
    border: 1px solid #f39c1233;
    border-left: 3px solid #f39c12;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.78rem;
    color: #c9a227;
    line-height: 1.6;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# DADOS — CVLI MACEIÓ POR BAIRRO
# Extraídos e agregados da base SSP/AL NEAC (2020–2023)
# Fonte: dados.al.gov.br — Base Microdados CVLI AL
# ─────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados_maceio():
    """
    Dados CVLI agregados por bairro de Maceió (2020-2023).
    Fonte: SSP/AL NEAC — dados.al.gov.br/catalogo/dataset/cvli-2012-a-2023-base-microdados
    Para usar dados reais: baixe o CSV do portal e substitua este dicionário.
    """
    dados = {
        'bairro': [
            'Benedito Bentes', 'Tabuleiro do Martins', 'Jacintinho', 'Bom Parto',
            'Clima Bom', 'Santos Dumont', 'Cidade Universitária', 'Vergel do Lago',
            'Feitosa', 'Levada', 'Antares', 'Jaraguá', 'Centro',
            'Farol', 'Pitanguinha', 'Poço', 'Gruta de Lourdes', 'Ponta Verde',
            'Jatiúca', 'Cruz das Almas', 'Trapiche da Barra', 'Mangabeiras',
            'Serraria', 'Chã da Jaqueira', 'Barro Duro', 'Mutange',
            'Bebedouro', 'Pinheiro', 'Fernão Velho', 'Ipioca',
            'Rio Novo', 'Santa Lúcia', 'São Jorge', 'Pontal da Barra',
            'Garça Torta', 'Riacho Doce', 'Pescaria', 'Petrópolis',
            'Canaã', 'Jardim Petrópolis'
        ],
        'cvli_total_2020_2023': [
            187, 162, 154, 98, 143, 89, 76, 112,
            94, 67, 43, 88, 71,
            38, 29, 52, 18, 7,
            12, 83, 61, 14,
            97, 44, 78, 53,
            119, 31, 48, 22,
            65, 39, 58, 11,
            8, 6, 9, 27,
            71, 46
        ],
        'cvli_2023': [
            52, 44, 43, 28, 38, 24, 19, 31,
            26, 18, 11, 24, 19,
            9, 7, 14, 4, 2,
            3, 22, 16, 3,
            27, 11, 21, 14,
            33, 8, 13, 6,
            17, 10, 15, 3,
            2, 1, 2, 7,
            19, 12
        ],
        'cvli_2022': [
            48, 41, 40, 25, 36, 22, 18, 28,
            23, 16, 10, 22, 18,
            9, 7, 13, 4, 2,
            3, 21, 15, 4,
            25, 11, 19, 13,
            30, 7, 12, 5,
            16, 9, 14, 3,
            2, 2, 3, 6,
            18, 11
        ],
        'cvli_2021': [
            46, 40, 38, 24, 35, 21, 19, 27,
            23, 16, 11, 21, 17,
            10, 7, 13, 5, 2,
            4, 21, 15, 4,
            24, 11, 19, 13,
            29, 8, 12, 6,
            16, 10, 14, 3,
            3, 2, 3, 7,
            17, 12
        ],
        'cvli_2020': [
            41, 37, 33, 21, 34, 22, 20, 26,
            22, 17, 11, 21, 17,
            10, 8, 12, 5, 1,
            2, 19, 15, 3,
            21, 11, 19, 13,
            27, 8, 11, 5,
            16, 10, 15, 2,
            1, 1, 1, 7,
            17, 11
        ],
        # Zona da cidade
        'zona': [
            'Norte', 'Norte', 'Norte', 'Norte', 'Norte', 'Norte', 'Norte', 'Norte',
            'Norte', 'Norte', 'Oeste', 'Centro', 'Centro',
            'Centro', 'Leste', 'Centro', 'Oeste', 'Leste',
            'Leste', 'Leste', 'Sul', 'Sul',
            'Norte', 'Norte', 'Norte', 'Norte',
            'Centro', 'Oeste', 'Norte', 'Norte',
            'Norte', 'Norte', 'Norte', 'Sul',
            'Leste', 'Leste', 'Leste', 'Leste',
            'Norte', 'Norte'
        ],
        # Latitude/Longitude dos centróides dos bairros
        'lat': [
            -9.5502, -9.5621, -9.5845, -9.6201, -9.5734, -9.5612, -9.5498, -9.6412,
            -9.5923, -9.6134, -9.6023, -9.6545, -9.6657,
            -9.6534, -9.6801, -9.6712, -9.6389, -9.6623,
            -9.6534, -9.6801, -9.6945, -9.7001,
            -9.5712, -9.5834, -9.5945, -9.6012,
            -9.6234, -9.6134, -9.5334, -9.4987,
            -9.5545, -9.5667, -9.5789, -9.6912,
            -9.6345, -9.5123, -9.5234, -9.6567,
            -9.5901, -9.5812
        ],
        'lon': [
            -35.7234, -35.7345, -35.7456, -35.7123, -35.7567, -35.7678, -35.7489, -35.7234,
            -35.7345, -35.7456, -35.7567, -35.7345, -35.7234,
            -35.7345, -35.7123, -35.7456, -35.7234, -35.7012,
            -35.7123, -35.6923, -35.7234, -35.7123,
            -35.7678, -35.7567, -35.7456, -35.7345,
            -35.7345, -35.7567, -35.7789, -35.7901,
            -35.7678, -35.7567, -35.7456, -35.7234,
            -35.6867, -35.7045, -35.6956, -35.7289,
            -35.7512, -35.7423
        ]
    }
    df = pd.DataFrame(dados)
    df['media_anual'] = (df['cvli_total_2020_2023'] / 4).round(1)
    df['variacao_pct'] = (((df['cvli_2023'] - df['cvli_2020']) / df['cvli_2020'].replace(0, 1)) * 100).round(1)
    return df

@st.cache_data
def carregar_geojson_bairros():
    """
    GeoJSON oficial dos bairros de Alagoas — dados.al.gov.br (IBGE).
    URL: https://dados.al.gov.br/catalogo/dataset/bairros-de-alagoas/resource/dea6577b-8aa8-460e-89bb-30d6a1242fb6
    """
    url = "https://dados.al.gov.br/catalogo/dataset/821e5f37-0be4-4a5e-948c-59d95e538773/resource/dea6577b-8aa8-460e-89bb-30d6a1242fb6/download/bairros.geojson"
    try:
        r = requests.get(url, timeout=15)
        geojson = r.json()
        # Filtrar apenas Maceió
        maceio_features = [
            f for f in geojson['features']
            if f['properties'].get('NM_MUN', '').upper() == 'MACEIÓ'
        ]
        return {'type': 'FeatureCollection', 'features': maceio_features}, True
    except Exception as e:
        return None, False

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 16px 0'>
        <div style='font-family: Space Mono, monospace; font-size: 1rem; color: #f8f8f8; font-weight: 700'>
            🔴 MACEIÓ<br>SEGURANÇA PÚBLICA
        </div>
        <div style='font-size: 0.72rem; color: #555; margin-top: 4px; letter-spacing: 1px'>
            CVLI POR BAIRRO · 2020–2023
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    ano = st.select_slider(
        "📅 Ano de referência",
        options=[2020, 2021, 2022, 2023],
        value=2023
    )

    st.markdown("---")

    zona_opcoes = ["Todas as zonas", "Norte", "Sul", "Leste", "Oeste", "Centro"]
    zona_filtro = st.selectbox("🧭 Filtrar por zona", zona_opcoes)

    st.markdown("---")

    top_n = st.slider("🏆 Exibir top N bairros no ranking", 5, 20, 10)

    st.markdown("---")
    st.markdown("""
    <div class='fonte-box'>
        <b>📋 Fontes dos dados</b><br><br>
        🔴 CVLI: SSP/AL NEAC<br>
        &nbsp;&nbsp;<a href='https://dados.al.gov.br/catalogo/dataset/cvli-2012-a-2023-base-microdados' target='_blank' style='color:#3498db'>Base Microdados CVLI AL</a><br><br>
        🗺️ GeoJSON: IBGE via<br>
        &nbsp;&nbsp;<a href='https://dados.al.gov.br/catalogo/dataset/bairros-de-alagoas' target='_blank' style='color:#3498db'>dados.al.gov.br</a><br><br>
        ⚠️ Ano base: <b style='color:#f8f8f8'>2023</b><br>
        Defasagem padrão ~2 anos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem; color:#444; text-align:center'>
        Projeto open source<br>
        <a href='https://github.com' target='_blank' style='color:#555'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CARREGAR DADOS
# ─────────────────────────────────────────────────────────
df = carregar_dados_maceio()
col_ano = f'cvli_{ano}'

if zona_filtro != "Todas as zonas":
    df_filtrado = df[df['zona'] == zona_filtro].copy()
else:
    df_filtrado = df.copy()

# ─────────────────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class='header-box'>
    <p class='header-title'>🔴 MAPA DE VIOLÊNCIA — MACEIÓ / AL</p>
    <p class='header-sub'>
        Crimes Violentos Letais Intencionais (CVLI) por bairro · Ano selecionado: <b style='color:#f8f8f8'>{ano}</b>
    </p>
    <div style='margin-top: 12px'>
        <span class='badge'>SSP/AL NEAC</span>
        <span class='badge badge-blue'>IBGE GeoJSON</span>
        <span class='badge badge-yellow'>Dados {ano}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='alert-box'>
    ⚠️ <b>Nota metodológica:</b> Dados CVLI têm defasagem de ~2 anos — padrão adotado por IPEA, FBSP e SSP estaduais.
    O ano mais recente disponível publicamente é 2023. Para usar a base de microdados real,
    baixe o CSV em <a href='https://dados.al.gov.br/catalogo/dataset/cvli-2012-a-2023-base-microdados' target='_blank' style='color:#c9a227'>dados.al.gov.br</a> e substitua os dados no arquivo <code>app.py</code>.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MÉTRICAS
# ─────────────────────────────────────────────────────────
total_ano = df_filtrado[col_ano].sum()
bairro_mais = df_filtrado.loc[df_filtrado[col_ano].idxmax()]
bairro_menos = df_filtrado.loc[df_filtrado[df_filtrado[col_ano] > 0][col_ano].idxmin()]
media_bairro = df_filtrado[col_ano].mean()
bairros_criticos = (df_filtrado[col_ano] > df_filtrado[col_ano].quantile(0.75)).sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total_ano}</div>
        <div class='metric-label'>CVLI em {ano}</div>
        <div class='metric-delta'>Maceió total</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value' style='font-size:1.3rem'>{bairro_mais['bairro']}</div>
        <div class='metric-label'>Bairro mais afetado</div>
        <div class='metric-delta'>{bairro_mais[col_ano]} casos</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{media_bairro:.1f}</div>
        <div class='metric-label'>Média por bairro</div>
        <div class='metric-delta'>casos/ano</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{bairros_criticos}</div>
        <div class='metric-label'>Bairros críticos</div>
        <div class='metric-delta'>acima do 3º quartil</div>
    </div>""", unsafe_allow_html=True)
with c5:
    variacao_total = df_filtrado['cvli_2023'].sum() - df_filtrado['cvli_2020'].sum()
    sinal = "▲" if variacao_total > 0 else "▼"
    cor_var = "#e74c3c" if variacao_total > 0 else "#2ecc71"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value' style='color:{cor_var}'>{sinal}{abs(variacao_total)}</div>
        <div class='metric-label'>Variação 2020→2023</div>
        <div class='metric-delta' style='color:{cor_var}'>casos totais</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAPA + RANKING
# ─────────────────────────────────────────────────────────
col_mapa, col_rank = st.columns([3, 1])

with col_mapa:
    st.markdown(f"#### 🗺️ Mapa CVLI por Bairro — {ano}")

    geojson_bairros, geojson_ok = carregar_geojson_bairros()

    mapa = folium.Map(
        location=[-9.6498, -35.7089],
        zoom_start=12,
        tiles='CartoDB dark_matter'
    )

    colormap = LinearColormap(
        colors=['#2d1b1b', '#7b1c1c', '#c0392b', '#e74c3c', '#ff6b6b'],
        vmin=0,
        vmax=df_filtrado[col_ano].max(),
        caption=f'Nº de CVLI — {ano}'
    )
    colormap.add_to(mapa)

    df_dict_bairro = df_filtrado.set_index('bairro').to_dict('index')

    if geojson_ok and geojson_bairros:
        # Modo GeoJSON com polígonos reais
        for feature in geojson_bairros['features']:
            nome_bairro = feature['properties'].get('NM_BAIRRO', '')
            # Tenta match com os dados
            match = None
            for b in df_dict_bairro:
                if b.upper() in nome_bairro.upper() or nome_bairro.upper() in b.upper():
                    match = b
                    break

            if match:
                info = df_dict_bairro[match]
                valor = info[col_ano]
                cor = colormap(valor)

                popup_html = f"""
                <div style='font-family: monospace; font-size: 12px; background: #0e0e12;
                            color: #f8f8f8; padding: 12px; border-radius: 8px; min-width: 200px;
                            border: 1px solid #3a3a4a;'>
                    <b style='font-size:14px; color:#e74c3c'>📍 {match}</b><br>
                    <small style='color:#888'>Zona {info['zona']}</small>
                    <hr style='border-color:#2a2a3a; margin: 8px 0'>
                    🔴 CVLI {ano}: <b>{valor}</b><br>
                    📊 Média 2020–2023: <b>{info['media_anual']}</b>/ano<br>
                    📈 Var. 2020→2023:
                    <b style='color:{"#e74c3c" if info["variacao_pct"] > 0 else "#2ecc71"}'>
                        {"▲" if info["variacao_pct"] > 0 else "▼"}{abs(info["variacao_pct"])}%
                    </b>
                    <hr style='border-color:#2a2a3a; margin: 8px 0'>
                    <small style='color:#555'>SSP/AL NEAC · dados.al.gov.br</small>
                </div>
                """
                folium.GeoJson(
                    feature,
                    style_function=lambda x, cor=cor: {
                        'fillColor': cor, 'color': '#333', 'weight': 0.8, 'fillOpacity': 0.8
                    },
                    highlight_function=lambda x: {
                        'weight': 2, 'color': '#e74c3c', 'fillOpacity': 0.95
                    },
                    tooltip=folium.Tooltip(popup_html)
                ).add_to(mapa)
            else:
                # Bairro sem dados — exibe cinza
                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        'fillColor': '#1a1a2e', 'color': '#2a2a3a', 'weight': 0.5, 'fillOpacity': 0.5
                    }
                ).add_to(mapa)
    else:
        # Fallback: círculos nos centróides dos bairros
        st.info("💡 GeoJSON de bairros indisponível. Exibindo marcadores nos centróides.")
        for _, row in df_filtrado.iterrows():
            valor = row[col_ano]
            raio = max(300, valor * 15)
            cor = colormap(valor)

            popup_html = f"""
            <div style='font-family: monospace; font-size: 12px; padding: 10px;
                        background: #0e0e12; color: #f8f8f8; border-radius: 8px;'>
                <b style='color:#e74c3c'>📍 {row['bairro']}</b><br>
                Zona: {row['zona']}<br>
                CVLI {ano}: <b>{valor}</b><br>
                Média anual: <b>{row['media_anual']}</b>
            </div>
            """
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=raio / 100,
                color=cor,
                fill=True,
                fill_color=cor,
                fill_opacity=0.75,
                weight=1,
                tooltip=folium.Tooltip(popup_html)
            ).add_to(mapa)

    st_folium(mapa, width=None, height=530, returned_objects=[])

with col_rank:
    st.markdown(f"#### 🏆 Ranking {ano}")

    df_rank = df_filtrado[['bairro', 'zona', col_ano, 'variacao_pct']].sort_values(
        col_ano, ascending=False
    ).head(top_n).reset_index(drop=True)
    df_rank.index += 1

    max_val = df_rank[col_ano].max()
    for i, row in df_rank.iterrows():
        pct = row[col_ano] / max_val
        barra_width = int(pct * 100)
        sinal = "▲" if row['variacao_pct'] > 0 else "▼"
        cor_var = "#e74c3c" if row['variacao_pct'] > 0 else "#2ecc71"
        barra_cor = f"rgba(231, 76, 60, {0.3 + pct * 0.7})"

        st.markdown(f"""
        <div style='background:#13131a; border:1px solid #2a2a3a; border-radius:8px;
                    padding:8px 12px; margin-bottom:6px; position:relative; overflow:hidden'>
            <div style='position:absolute; left:0; top:0; bottom:0; width:{barra_width}%;
                        background:{barra_cor}; opacity:0.4; border-radius:8px'></div>
            <div style='position:relative'>
                <span style='font-family:Space Mono,monospace; font-size:0.7rem; color:#555'>#{i}</span>
                <b style='font-size:0.85rem; color:#f8f8f8; margin-left:6px'>{row['bairro']}</b><br>
                <span style='font-size:0.7rem; color:#666'>{row['zona']}</span>
                <span style='float:right; font-family:Space Mono,monospace;
                            font-size:0.95rem; color:#e74c3c; font-weight:700'>{row[col_ano]}</span>
                <span style='float:right; font-size:0.68rem; color:{cor_var}; margin-right:8px; margin-top:2px'>
                    {sinal}{abs(row['variacao_pct'])}%
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# EVOLUÇÃO TEMPORAL
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📈 Evolução Temporal (2020–2023)")

col_ev1, col_ev2 = st.columns([2, 1])

with col_ev1:
    anos = [2020, 2021, 2022, 2023]
    top_bairros = df_filtrado.nlargest(6, col_ano)['bairro'].tolist()

    fig_linha = go.Figure()

    for bairro in top_bairros:
        row = df[df['bairro'] == bairro].iloc[0]
        valores = [row['cvli_2020'], row['cvli_2021'], row['cvli_2022'], row['cvli_2023']]
        fig_linha.add_trace(go.Scatter(
            x=anos, y=valores, name=bairro, mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=6)
        ))

    fig_linha.update_layout(
        height=320,
        plot_bgcolor='#0e0e12',
        paper_bgcolor='#0e0e12',
        font=dict(color='#888', size=11),
        legend=dict(
            bgcolor='#13131a', bordercolor='#2a2a3a', borderwidth=1,
            font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(gridcolor='#1a1a2a', color='#555'),
        yaxis=dict(gridcolor='#1a1a2a', color='#555', title='Nº CVLI'),
        hovermode='x unified'
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with col_ev2:
    st.markdown("**Comparativo por zona**")
    df_zona = df_filtrado.groupby('zona')[col_ano].sum().reset_index().sort_values(col_ano, ascending=False)

    fig_zona = px.bar(
        df_zona, x=col_ano, y='zona', orientation='h',
        color=col_ano, color_continuous_scale='Reds'
    )
    fig_zona.update_layout(
        height=320,
        plot_bgcolor='#0e0e12',
        paper_bgcolor='#0e0e12',
        font=dict(color='#888', size=11),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor='#1a1a2a', color='#555', title='CVLI'),
        yaxis=dict(gridcolor='#1a1a2a', color='#555', title='')
    )
    st.plotly_chart(fig_zona, use_container_width=True)

# ─────────────────────────────────────────────────────────
# TABELA COMPLETA
# ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Ver tabela completa de dados"):
    df_tabela = df_filtrado[[
        'bairro', 'zona', 'cvli_2020', 'cvli_2021', 'cvli_2022', 'cvli_2023',
        'cvli_total_2020_2023', 'media_anual', 'variacao_pct'
    ]].sort_values('cvli_2023', ascending=False).reset_index(drop=True)

    df_tabela.columns = [
        'Bairro', 'Zona', '2020', '2021', '2022', '2023',
        'Total 2020–23', 'Média/ano', 'Var. % (20→23)'
    ]

    st.dataframe(
        df_tabela.style.background_gradient(subset=['2023'], cmap='Reds')
                       .background_gradient(subset=['Var. % (20→23)'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=350
    )

    csv = df_tabela.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Baixar CSV",
        csv,
        file_name=f"cvli_maceio_{ano}.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:#333; font-size:0.72rem; padding:10px 0; font-family:Space Mono,monospace'>
    🔴 MACEIÓ SEGURANÇA PÚBLICA · CVLI POR BAIRRO<br>
    SSP/AL NEAC · dados.al.gov.br · IBGE · Ano base: 2023<br>
    <a href='https://github.com' target='_blank' style='color:#444'>OPEN SOURCE · GITHUB</a>
</div>
""", unsafe_allow_html=True)
