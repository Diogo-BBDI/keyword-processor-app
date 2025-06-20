import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Processador de Palavras-chave", layout="wide")

st.title("🔍 Processador de Palavras-chave")
st.markdown("Faça upload de arquivos CSV ou XLSX com palavras-chave e arquivos TXT com termos a excluir. O sistema limpa, combina e exporta os dados.")

# Diretório com arquivos de exclusão opcionais
PRESET_DIR = "exclusoes_predefinidas"
os.makedirs(PRESET_DIR, exist_ok=True)

preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')]
selected_presets = st.multiselect("🔘 Selecionar arquivos de exclusão predefinidos", preset_files)

keyword_files = st.file_uploader("Arquivos de Palavras-chave (CSV/XLSX)", type=['csv', 'xlsx'], accept_multiple_files=True)
exclusion_files = st.file_uploader("Arquivos de Exclusão (TXT) (opcional)", type=['txt'], accept_multiple_files=True)
mode = st.selectbox("Modo de Duplicatas", [
    'global',
    'keep_by_source',
    'merge_sources'
], index=2)

if st.button("🚀 Iniciar Processamento"):
    if not keyword_files:
        st.error("⚠️ Adicione pelo menos um arquivo de palavras-chave.")
    else:
        remove_words = set()

        # Palavras dos arquivos TXT enviados pelo usuário
        for txt in exclusion_files or []:
            lines = txt.read().decode('utf-8').splitlines()
            remove_words.update(line.strip().lower() for line in lines if line.strip())

        # Palavras dos arquivos de exclusão predefinidos
        for fname in selected_presets:
            with open(os.path.join(PRESET_DIR, fname), 'r', encoding='utf-8') as f:
                lines = f.readlines()
                remove_words.update(line.strip().lower() for line in lines if line.strip())

        all_keywords = []

        for f in keyword_files:
            try:
                if f.name.endswith('.csv'):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)

                cols = [c.lower() for c in df.columns]
                kw_col = next((c for c in cols if 'keyword' in c or 'termo' in c), None)
                vol_col = next((c for c in cols if 'volume' in c or 'search' in c), None) or kw_col
                df.columns = cols

                df = df[df[kw_col].notnull()]
                df['keyword_cleaned'] = df[kw_col].astype(str).str.lower().apply(
                    lambda x: ' '.join(w for w in x.split() if w not in remove_words)
                )
                df = df[df['keyword_cleaned'] != '']
                df['volume'] = pd.to_numeric(df[vol_col], errors='coerce').fillna(0).astype(int)
                df['source'] = f.name
                all_keywords.append(df[['keyword_cleaned', 'volume', 'source']])

                st.success(f"{f.name}: {len(df)} palavras válidas")
            except Exception as e:
                st.error(f"Erro ao processar {f.name}: {str(e)}")

        if all_keywords:
            df_all = pd.concat(all_keywords)
            if mode == 'global':
                df_final = df_all.drop_duplicates(subset='keyword_cleaned')
            elif mode == 'keep_by_source':
                df_final = df_all.drop_duplicates(subset=['keyword_cleaned', 'source'])
            else:
                df_final = df_all.groupby('keyword_cleaned').agg({
                    'volume': 'sum',
                    'source': lambda x: ', '.join(sorted(set(x)))
                }).reset_index()

            st.subheader("📊 Resultados")
            st.markdown(f"**Total original:** {sum(len(df) for df in all_keywords)}")
            st.markdown(f"**Total final:** {len(df_final)} palavras-chave únicas")
            st.markdown(f"**Volume total:** {df_final['volume'].sum():,}")

            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar CSV Processado", csv, file_name="keywords_processadas.csv", mime='text/csv')

            st.markdown("---")
            st.dataframe(df_final.head(50))