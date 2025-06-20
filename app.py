import streamlit as st
import pandas as pd
import io
import os
import time

st.set_page_config(page_title="Processador de Palavras-chave", layout="wide")

# Estilo dark com UI/UX refinado
st.markdown("""
<style>
body {
  background-color: #0f1117;
  color: #f1f3f4;
  font-family: 'Segoe UI', sans-serif;
}
.stApp {
  background: linear-gradient(to bottom right, #0f1117, #1e2230);
}
.metric-card {
  padding: 1.5rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #1f2430, #292e3d);
  box-shadow: 0 6px 16px rgba(0,0,0,0.25);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.metric-title {
  font-weight: 600;
  font-size: 1rem;
  color: #a0aec0;
  margin-bottom: 0.25rem;
}
.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #63b3ed;
}
.stButton>button {
  background: linear-gradient(to right, #3182ce, #5a67d8);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.stButton>button:hover {
  box-shadow: 0 4px 16px rgba(90,103,216,0.4);
  transform: translateY(-2px);
}
.log-line {
  font-family: monospace;
  font-size: 13px;
  color: #cbd5e0;
  border-bottom: 1px solid #2d3748;
  padding: 2px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="text-align:center; color:#63b3ed; font-size: 2.8rem; margin-bottom: 0.2em;">🔍 Processador de Palavras-chave</h1>
<p style="text-align:center; font-size: 1.1rem; color: #cbd5e0;">
Upload arquivos CSV/XLSX com palavras-chave e TXT com termos de exclusão. O app filtra, combina e exporta com visual escuro otimizado.
</p>
""", unsafe_allow_html=True)

PRESET_DIR = "exclusoes_predefinidas"
os.makedirs(PRESET_DIR, exist_ok=True)

preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')]
selected_presets = st.multiselect("🔘 Selecionar arquivos de exclusão predefinidos", preset_files)

col_upload, col_opts = st.columns([2, 1])
with col_upload:
    keyword_files = st.file_uploader("📂 Arquivos de Palavras-chave (CSV/XLSX)", type=['csv', 'xlsx'], accept_multiple_files=True)
    exclusion_files = st.file_uploader("🗑 Arquivos de Exclusão (TXT) (opcional)", type=['txt'], accept_multiple_files=True)
with col_opts:
    mode = st.selectbox("Modo de Duplicatas", ['global', 'keep_by_source', 'merge_sources'], index=2)

start_button = st.button("🚀 Iniciar Processamento")

placeholder_metrics = st.empty()
placeholder_progress = st.empty()
placeholder_status = st.empty()
placeholder_logs = st.empty()

log_buffer = []

if start_button:
    if not keyword_files:
        st.error("⚠️ Adicione pelo menos um arquivo de palavras-chave.")
    else:
        remove_words = set()
        placeholder_status.info("🔄 Lendo arquivos de exclusão...")
        time.sleep(0.5)

        for txt in exclusion_files or []:
            lines = txt.read().decode('utf-8').splitlines()
            remove_words.update(line.strip().lower() for line in lines if line.strip())

        for fname in selected_presets:
            with open(os.path.join(PRESET_DIR, fname), 'r', encoding='utf-8') as f:
                lines = f.readlines()
                remove_words.update(line.strip().lower() for line in lines if line.strip())

        all_keywords = []
        total_files = len(keyword_files)

        for i, f in enumerate(keyword_files):
            try:
                placeholder_status.info(f"🔍 Processando {f.name}...")
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

                log_buffer.append(f"✅ {f.name}: {len(df)} palavras válidas")
            except Exception as e:
                log_buffer.append(f"❌ Erro ao processar {f.name}: {str(e)}")

            placeholder_progress.progress((i + 1) / total_files)
            placeholder_logs.markdown('<br>'.join(f'<div class="log-line">{line}</div>' for line in log_buffer), unsafe_allow_html=True)

        if all_keywords:
            placeholder_status.info("🧮 Combinando e removendo duplicatas...")
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

            total_original = sum(len(df) for df in all_keywords)
            total_combinado = len(df_all)
            total_final = len(df_final)
            volume_total = df_final['volume'].sum()
            total_removidas = total_original - total_final

            log_buffer.extend([
                "\n=== RELATÓRIO FINAL ===",
                f"Arquivos processados: {len(all_keywords)}",
                f"Total original de palavras-chave: {total_original}",
                f"Após combinação: {total_combinado}",
                f"Após remoção de duplicatas: {total_final}",
                f"Removidas: {total_removidas} entradas",
                f"Volume final total: {volume_total:,.0f}"
            ])
            placeholder_logs.markdown('<br>'.join(f'<div class="log-line">{line}</div>' for line in log_buffer), unsafe_allow_html=True)

            with placeholder_metrics:
                st.markdown("## 📊 Resultados")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card"><div class="metric-title">Total original</div><div class="metric-value">{:,.0f}</div></div>'.format(total_original), unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card"><div class="metric-title">Após deduplicação</div><div class="metric-value">{:,.0f}</div></div>'.format(total_final), unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card"><div class="metric-title">Volume total</div><div class="metric-value">{:,.0f}</div></div>'.format(volume_total), unsafe_allow_html=True)

            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar CSV Processado", csv, file_name="keywords_processadas.csv", mime='text/csv')
            st.markdown("---")
            st.dataframe(df_final.head(50))

        placeholder_status.success("✅ Processamento concluído!")
        placeholder_progress.empty()
