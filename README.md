# 🗺️ Mapa de Violência no Brasil

> Visualização interativa de indicadores de segurança pública por estado brasileiro.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Licença](https://img.shields.io/badge/Licença-MIT-green)
![Dados](https://img.shields.io/badge/Dados-2023-orange)

---

## 📊 O que este projeto mostra

- 🔴 **Homicídios gerais** — taxa por 100 mil habitantes por estado
- 🟣 **Violência contra mulheres** — taxa de homicídios femininos por 100 mil mulheres
- 🟡 **Roubos** — taxa por 100 mil habitantes por estado
- ⚫ **Interseccionalidade** — relação entre raça, gênero e violência

## 🌐 Acesse o app

👉 **[Link do app no Streamlit Cloud]** ← *(atualizar após publicar)*

## 🗂️ Fontes dos dados

| Indicador | Fonte | Ano base |
|---|---|---|
| Homicídios gerais | Atlas da Violência 2025 — IPEA/FBSP | 2023 |
| Homicídios femininos | Atlas da Violência 2025 — IPEA/FBSP | 2023 |
| Roubos | Anuário Brasileiro de Segurança Pública 2024 — FBSP | 2023 |

> ⚠️ **Nota metodológica:** Dados de violência no Brasil têm defasagem de ~2 anos. O Atlas da Violência 2025 usa ano base 2023. Esse padrão é adotado pelo IPEA, FBSP e todos os projetos sérios desta área.

## 🚀 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/mapa-violencia-brasil
cd mapa-violencia-brasil

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode o app
streamlit run app.py
```

O app abrirá em `http://localhost:8501`

## ☁️ Como publicar no Streamlit Cloud (grátis)

1. Crie conta em [streamlit.io/cloud](https://streamlit.io/cloud)
2. Conecte sua conta GitHub
3. Clique em **"New app"**
4. Selecione este repositório
5. Main file: `app.py`
6. Clique **Deploy** — o app fica no ar em ~2 minutos

## 🗺️ Estrutura do projeto

```
mapa-violencia-brasil/
├── app.py              ← App principal Streamlit
├── requirements.txt    ← Dependências Python
└── README.md           ← Este arquivo
```

## 🔮 Roadmap

- [ ] Nível município (5.570 municípios com filtro por estado)
- [ ] Série temporal com slider de anos (2010–2023)
- [ ] Busca por cidade com zoom automático
- [ ] Scraper automático para novos dados do IPEA
- [ ] API pública com os dados limpos (BRGov Graph API)

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Especialmente:
- Atualização de dados quando o IPEA publicar novas edições
- Adição de novas camadas (tráfico, violência no campo, etc.)
- Melhoria da performance no nível município

## 📄 Licença

MIT — use, modifique e redistribua livremente, mantendo a atribuição.

---

*Projeto open source desenvolvido com dados públicos brasileiros.*  
*Dados: IPEA · FBSP · Ministério da Saúde/SIM*
