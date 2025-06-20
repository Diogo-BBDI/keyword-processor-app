import streamlit as st
import pandas as pd
import io
import os
import time

st.set_page_config(page_title="Processador de Palavras-chave", layout="wide")

# Estilo aprimorado com UI/UX animado
st.markdown("""
<style>
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}
body {
  background: linear-gradient(to bottom right, #eaf4ff, #f2f7ff);
}
.block-animado div {
  animation: fadeIn 0.6s ease-in-out;
}
.metric-card {
  padding: 1.5rem;
  border-radius: 20px;
  background: linear-gradient(135deg, #ffffff, #f4f8ff);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.12);
}
.metric-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2a2a2a;
  margin-bottom: 0.25rem;
}
.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1f4e79;
}
.stButton>button {
  background: linear-gradient(to right, #3b82f6, #6366f1);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.stButton>button:hover {
  box-shadow: 0 4px 12px rgba(99,102,241,0.4);
  transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="block-animado">
<h1 style="text-align:center; color:#1f4e79; font-size: 2.8rem; margin-bottom: 0.2em;">🔍 Processador de Palavras-chave</h1>
<p style="text-align:center; font-size: 1.1rem; color: #444;">
Faça upload de arquivos CSV/XLSX com palavras-chave e TXT com termos para exclusão. O app limpará, combinará e exportará tudo automaticamente.
</p>
</div>
""", unsafe_allow_html=True)

PRESET_DIR = "exclusoes_predefinidas"
os.makedirs(PRESET_DIR, exist_ok=True)

preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')]
selected_presets = st.multiselect("🔘 Selecionar arquivos de exclusão predefinidos", preset_files)

with st.expander("📁 Upload de Arquivos", expanded=True):
    keyword_files = st.file_uploader("Arquivos de Palavras-chave (CSV/XLSX)", type=['csv', 'xlsx'], accept_multiple_files=True)
    exclusion_files = st.file_uploader("Arquivos de Exclusão (TXT) (opcional)", type=['txt'], accept_multiple_files=True)
    mode = st.selectbox("Modo de Duplicatas", ['global', 'keep_by_source', 'merge_sources'], index=2)

progress_bar = st.empty()
status_text = st.empty()
logs = st.container()

if st.button("🚀 Iniciar Processamento"):
    if not keyword_files:
        st.error("⚠️ Adicione pelo menos um arquivo de palavras-chave.")
    else:
        remove_words = set()
        status_text.info("🔄 Lendo arquivos de exclusão...")
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
                status_text.info(f"🔍 Processando {f.name}...")
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

                logs.success(f"✅ {f.name}: {len(df)} palavras válidas")
            except Exception as e:
                logs.error(f"❌ Erro ao processar {f.name}: {str(e)}")

            progress_bar.progress((i+1)/total_files)

        if all_keywords:
            status_text.info("🧮 Combinando e removendo duplicatas...")
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

            logs.info("\n=== RELATÓRIO FINAL ===")
            logs.info(f"Arquivos processados: {len(all_keywords)}")
            logs.info(f"Total original de palavras-chave: {total_original}")
            logs.info(f"Após combinação: {total_combinado}")
            logs.info(f"Após remoção de duplicatas: {total_final}")
            logs.info(f"Removidas: {total_removidas} entradas")
            logs.info(f"Volume final total: {volume_total:,.0f}")

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

        status_text.success("✅ Processamento concluído!")
        progress_bar.empty()
