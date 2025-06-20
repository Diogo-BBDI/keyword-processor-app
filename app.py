import streamlit as st
import pandas as pd
import io
import os
import time

st.set_page_config(page_title="Processador de Palavras-chave", layout="wide")

# Estilo Dark Premium refinado com melhorias de layout e botões
st.markdown("""
<style>
body {
  background-color: #0f1117;
  color: #f1f3f4;
  font-family: 'Segoe UI', sans-serif;
}
.stApp {
  background: linear-gradient(135deg, #0f1117 0%, #1e2230 100%);
  padding-bottom: 2rem;
}
.metric-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 20px;
  background: linear-gradient(135deg, #1f2430, #292e3d);
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  text-align: center;
  transition: all 0.4s ease;
}
.metric-card:hover {
  transform: scale(1.02);
  box-shadow: 0 16px 32px rgba(0,0,0,0.45);
}
.metric-title {
  font-weight: 600;
  font-size: 1rem;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
}
.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #63b3ed;
}
.stButton>button, .stDownloadButton>button {
  background: linear-gradient(to right, #2563eb, #1e40af);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 0.5rem;
}
.stButton>button:hover, .stDownloadButton>button:hover {
  box-shadow: 0 4px 16px rgba(37,99,235,0.4);
  transform: translateY(-2px);
}
.log-box {
  background: #1a202c;
  border-radius: 12px;
  padding: 1rem;
  height: 300px;
  overflow-y: scroll;
  font-family: monospace;
  font-size: 13px;
  color: #e2e8f0;
  border: 1px solid #2d3748;
  margin-bottom: 1rem;
}
label, .css-1kyxreq, .css-14xtw13, .css-81oif8, .css-1aumxhk {
  color: #cbd5e0 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="text-align:center; color:#63b3ed; font-size: 2.8rem; margin-bottom: 0.2em; margin-top: 0.5rem;">🔍 Processador de Palavras-chave</h1>
<p style="text-align:center; font-size: 1.1rem; color: #e2e8f0;">
Envie arquivos com palavras-chave e termos de exclusão. Visual escuro, animações suaves e UX aprimorado.
</p>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.2rem'></div>", unsafe_allow_html=True)
metrics = st.container()
st.markdown("<div style='margin-top: 1rem'></div>", unsafe_allow_html=True)

col_uploads, col_feedback = st.columns([1.2, 1])

with col_uploads:
    st.subheader("📂 Upload de Arquivos")
    keyword_files = st.file_uploader("Palavras-chave (CSV/XLSX)", type=['csv', 'xlsx'], accept_multiple_files=True)
    exclusion_files = st.file_uploader("Exclusões (TXT) - Opcional", type=['txt'], accept_multiple_files=True)
    PRESET_DIR = "exclusoes_predefinidas"
    os.makedirs(PRESET_DIR, exist_ok=True)
    preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')]
    selected_presets = st.multiselect("Arquivos de Exclusão Predefinidos", preset_files)
    mode = st.selectbox("Modo de Duplicatas", ['global', 'keep_by_source', 'merge_sources'], index=2)

with col_feedback:
    progress_status = st.empty()
    progress_bar = st.progress(0)
    log_area = st.empty()
    log_buffer = []
    button_col1, button_col2 = st.columns(2)
    with button_col1:
        start_button = st.button("🚀 Iniciar Processamento")
    with button_col2:
        download_button_placeholder = st.empty()

def log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    log_buffer.append(f"{timestamp} {message}")
    if len(log_buffer) > 100:
        log_buffer.pop(0)
    log_area.markdown(f'<div class="log-box">' + '<br>'.join(log_buffer) + '</div>', unsafe_allow_html=True)


# Botões lado a lado após logs
col1, col2 = st.columns(2)
with col1:
    start_button = st.button("🚀 Iniciar Processamento")
with col2:
    download_button = st.button("⬇️ Baixar Resultado")

if start_button:
    if not keyword_files:
        st.error("⚠️ Nenhum arquivo de palavras-chave foi enviado.")
    else:
        remove_words = set()
        log("🔄 Lendo arquivos de exclusão...")

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
            log(f"📄 Processando {f.name}...")
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
                log(f"✅ {f.name}: {len(df)} entradas válidas")
            except Exception as e:
                log(f"❌ Erro em {f.name}: {str(e)}")

            progress_bar.progress((i + 1) / total_files)

        if all_keywords:
            log("🧮 Combinando e deduplicando...")
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

            log("📊 Processamento concluído")
            log(f"Total original: {total_original}")
            log(f"Após combinação: {total_combinado}")
            log(f"Removidas: {total_removidas} entradas")
            log(f"Volume final: {volume_total:,.0f}")

            with metrics:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card"><div class="metric-title">Total Original</div><div class="metric-value">{:,.0f}</div></div>'.format(total_original), unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card"><div class="metric-title">Após Deduplicação</div><div class="metric-value">{:,.0f}</div></div>'.format(total_final), unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card"><div class="metric-title">Volume Total</div><div class="metric-value">{:,.0f}</div></div>'.format(volume_total), unsafe_allow_html=True)

            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar CSV", csv, file_name="keywords_processadas.csv", mime='text/csv')
            st.dataframe(df_final.head(50))

        else:
            log("⚠️ Nenhum dado válido encontrado.")

        progress_bar.empty()
