# 📊 Processador de Palavras-chave (Streamlit)

Aplicativo interativo em Python desenvolvido com **Streamlit** para processar arquivos de palavras-chave e aplicar filtros de exclusão de forma flexível e eficiente.

Ideal para profissionais de SEO, mídia paga, e-commerce e análise de mercado que trabalham com grandes volumes de termos e precisam de limpeza, organização e exportação de dados de maneira prática.

---

## 🚀 Funcionalidades

- ✅ Upload de múltiplos arquivos `.csv` ou `.xlsx` com palavras-chave
- 🧹 Upload de arquivos `.txt` com termos a serem excluídos
- 📂 Suporte a **exclusões predefinidas** através da pasta `exclusoes_predefinidas/`
- 🔁 Modos de tratamento de duplicatas:
  - `global`: remove duplicatas independentemente da origem
  - `keep_by_source`: mantém duplicatas se vierem de fontes diferentes
  - `merge_sources`: soma volumes e agrupa as fontes
- 📥 Exportação em `.csv` com colunas `keyword`, `volume`, `source`
- 📈 Estatísticas de resumo (volume total, total original e final de termos)

---

## 🛠️ Como usar localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/keyword-processor-app.git
cd keyword-processor-app

# Instale as dependências
pip install -r requirements.txt

# Rode o app
streamlit run app.py
