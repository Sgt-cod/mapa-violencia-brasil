# 🔴 Mapa de Violência — Maceió / AL
### CVLI por Bairro · 2020–2023

> O único mapa público interativo de Crimes Violentos Letais Intencionais por bairro de Maceió.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Licença](https://img.shields.io/badge/Licença-MIT-green)
![Fonte](https://img.shields.io/badge/Fonte-SSP%2FAL%20NEAC-orange)

---

## 🌐 Acesse o app

👉 **[Link do app]** ← *(atualizar após publicar no Streamlit Cloud)*

---

## 📊 O que este projeto mostra

- 🗺️ Mapa interativo de CVLI (Crimes Violentos Letais Intencionais) por bairro de Maceió
- 📅 Filtro por ano: 2020, 2021, 2022, 2023
- 🧭 Filtro por zona da cidade (Norte, Sul, Leste, Oeste, Centro)
- 📈 Evolução temporal dos 6 bairros mais afetados
- 🏆 Ranking dinâmico com variação percentual
- ⬇️ Exportação dos dados em CSV

**CVLI inclui:** homicídio doloso, roubo seguido de morte (latrocínio), lesão corporal seguida de morte.

---

## 🗂️ Fontes dos dados

| Dado | Fonte | URL |
|---|---|---|
| Microdados CVLI | SSP/AL NEAC | [dados.al.gov.br](https://dados.al.gov.br/catalogo/dataset/cvli-2012-a-2023-base-microdados) |
| GeoJSON bairros | IBGE via dados.al.gov.br | [Link direto](https://dados.al.gov.br/catalogo/dataset/bairros-de-alagoas/resource/dea6577b-8aa8-460e-89bb-30d6a1242fb6) |
| Boletins mensais 2025 | SSP/AL NEAC | [dados.al.gov.br](https://dados.al.gov.br/catalogo/dataset/boletins-mensais-de-estatisticas-criminais-2024) |

> ⚠️ **Nota metodológica:** Os dados CVLI têm defasagem padrão de ~2 anos — o mesmo critério adotado pelo IPEA, FBSP e todas as SSPs estaduais. O ano mais recente disponível publicamente é 2023.

---

## 🚀 Como usar com os dados reais

### 1. Baixar os microdados da SSP/AL

```bash
# Acesse o portal e baixe o CSV:
# https://dados.al.gov.br/catalogo/dataset/cvli-2012-a-2023-base-microdados
```

### 2. Substituir os dados no app

No `app.py`, a função `carregar_dados_maceio()` contém dados pré-agregados.
Para usar o CSV real da SSP/AL, substitua por:

```python
@st.cache_data
def carregar_dados_maceio():
    df_raw = pd.read_csv('cvli_microdados.csv')

    # Filtrar apenas Maceió
    df_maceio = df_raw[df_raw['municipio'].str.upper() == 'MACEIÓ'].copy()

    # Agregar por bairro e ano
    df_agg = df_maceio.groupby(['bairro', 'ano']).size().reset_index(name='cvli')
    df_pivot = df_agg.pivot(index='bairro', columns='ano', values='cvli').fillna(0)

    return df_pivot
```

> **Atenção:** O CSV da SSP/AL pode ter variações nos nomes das colunas. Inspecione com `df.columns` antes de usar.

### 3. Rodar localmente

```bash
git clone https://github.com/SEU_USUARIO/maceio-violencia
cd maceio-violencia
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Publicar no Streamlit Cloud (grátis)

1. Crie conta em [streamlit.io/cloud](https://streamlit.io/cloud)
2. Conecte sua conta GitHub
3. Clique em **"New app"**
4. Selecione este repositório → Main file: `app.py`
5. Clique **Deploy**

---

## 🗂️ Estrutura

```
maceio-violencia/
├── app.py              ← App Streamlit principal
├── requirements.txt    ← Dependências Python
└── README.md           ← Este arquivo
```

## 🔮 Roadmap

- [ ] Integrar CSV real dos microdados SSP/AL via download automático
- [ ] Adicionar camada de delegacias (GeoJSON disponível no portal AL)
- [ ] Adicionar camada de grotas/áreas de vulnerabilidade (ONU-Habitat)
- [ ] Correlação CVLI × IDH por bairro (IBGE Censo 2022)
- [ ] Série temporal completa 2012–2023
- [ ] Notificações automáticas quando novos boletins mensais forem publicados

## 📄 Licença

MIT — use, modifique e redistribua livremente, mantendo a atribuição.

---

*Dados: SSP/AL NEAC · IBGE · dados.al.gov.br*
*Projeto desenvolvido com Python + Streamlit + Folium*
