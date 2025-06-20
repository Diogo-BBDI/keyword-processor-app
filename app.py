import streamlit as st
import pandas as pd
import io
import os
import time
import uuid

st.set_page_config(page_title="Processador de Palavras-chave", layout="wide")

# Updated CSS for improved UI/UX with clearer text colors
st.markdown("""
<style>
body {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(145deg, #121212 0%, #1a1a1a 100%);
    padding: 2rem;
}
.header-container {
    text-align: center;
    margin-bottom: 2rem;
}
.header-title {
    color: #4dabf7;
    font-size: 2.5rem;
    font-weight: 700;
}
.header-subtitle {
    color: #b0b0b0;
    font-size: 1rem;
}
.section-container {
    background: #1e1e1e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.metric-card {
    padding: 1.5rem;
    margin: 0.5rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #252525, #2d2d2d);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.metric-title {
    font-weight: 500;
    font-size: 0.9rem;
    color: #e0e0e0;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #4dabf7;
}
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(90deg, #4dabf7, #3b82f6);
    color: white;
    padding: 0.8rem 1.6rem;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    width: 100%;
    margin-top: 1rem;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    background: linear-gradient(90deg, #60a5fa, #4f46e5);
    transform: translateY(-2px);
}
.log-box {
    background: #181818;
    border-radius: 8px;
    padding: 1rem;
    height: 250px;
    overflow-y: auto;
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #e0e0e0;
    border: 1px solid #2a2a2a;
    margin-bottom: 1rem;
}
.stSpinner {
    color: #4dabf7;
}
label, .css-1kyxreq, .css-14xtw13, .css-81oif8, .css-1aumxhk {
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🔍 Processador de Palavras-chave</h1>
    <p class="header-subtitle">Envie arquivos CSV/XLSX para palavras-chave e TXT para exclusões</p>
</div>
""", unsafe_allow_html=True)

# Metrics container (at the top)
metrics = st.container()
with metrics:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-title">Total Original</div><div class="metric-value" id="total_original">0</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-title">Após Deduplicação</div><div class="metric-value" id="total_final">0</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-title">Volume Total</div><div class="metric-value" id="volume_total">0</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Layout with containers for uploads and feedback
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    col_uploads, col_feedback = st.columns([1.3, 1])

    with col_uploads:
        st.subheader("📂 Upload de Arquivos")
        keyword_files = st.file_uploader("Palavras-chave (CSV/XLSX)", type=['csv', 'xlsx'], accept_multiple_files=True)
        exclusion_files = st.file_uploader("Exclusões (TXT) - Opcional", type=['txt'], accept_multiple_files=True)
        PRESET_DIR = "exclusoes_predefinidas"
        os.makedirs(PRESET_DIR, exist_ok=True)
        preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')] if os.path.exists(PRESET_DIR) else []
        selected_presets = st.multiselect("Exclusões Predefinidas", preset_files)
        mode = st.selectbox("Modo de Duplicatas", [
            'Global - Remove Todas as Duplicatas',
            'Por Arquivo - Mantém se vierem de arquivos diferentes',
            'Mesclar - Remove Duplicatas e Soma os Volumes'
        ], index=2)

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

    st.markdown('</div>', unsafe_allow_html=True)

# Cache file loading
@st.cache_data
def load_file(file, file_type):
    if file_type == 'csv':
        return pd.read_csv(file, chunksize=10000)
    return pd.read_excel(file)

# Cache exclusion file reading
@st.cache_data
def load_exclusion_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

def log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    log_buffer.append(f"{timestamp} {message}")
    if len(log_buffer) > 100:
        log_buffer.pop(0)
    log_area.markdown(f'<div class="log-box">' + '<br>'.join(log_buffer) + '</div>', unsafe_allow_html=True)

if start_button:
    if not keyword_files:
        st.error("⚠️ Por favor, envie pelo menos um arquivo de palavras-chave.")
    else:
        with st.spinner("Processando..."):
            remove_words = set()
            log("🔄 Lendo arquivos de exclusão...")

            # Process exclusion files
            for txt in exclusion_files or []:
                try:
                    lines = txt.read().decode('utf-8', errors='ignore').splitlines()
                    remove_words.update(line.strip().lower() for line in lines if line.strip())
                except Exception as e:
                    log(f"❌ Erro ao ler arquivo de exclusão {txt.name}: {str(e)}")

            for fname in selected_presets:
                try:
                    remove_words.update(load_exclusion_file(os.path.join(PRESET_DIR, fname)))
                except Exception as e:
                    log(f"❌ Erro ao ler exclusão predefinida {fname}: {str(e)}")

            all_keywords = []
            total_files = len(keyword_files)

            for i, f in enumerate(keyword_files):
                log(f"📄 Processando {f.name}...")
                try:
                    file_type = 'csv' if f.name.endswith('.csv') else 'xlsx'
                    df_chunks = load_file(f, file_type)
                    if file_type == 'csv':
                        for chunk in df_chunks:
                            cols = [c.lower() for c in chunk.columns]
                            kw_col = next((c for c in cols if 'keyword' in c or 'termo' in c), None)
                            vol_col = next((c for c in cols if 'volume' in c or 'search' in c), None) or kw_col

                            if not kw_col:
                                log(f"❌ Nenhuma coluna de palavras-chave encontrada em {f.name}")
                                continue

                            chunk.columns = cols
                            chunk = chunk[chunk[kw_col].notnull()]
                            chunk['keyword_cleaned'] = chunk[kw_col].astype(str).str.lower().apply(
                                lambda x: ' '.join(w for w in x.split() if w not in remove_words)
                            )
                            chunk = chunk[chunk['keyword_cleaned'] != '']
                            chunk['volume'] = pd.to_numeric(chunk[vol_col], errors='coerce').fillna(0).astype(int)
                            chunk['source'] = f.name
                            all_keywords.append(chunk[['keyword_cleaned', 'volume', 'source']])
                    else:
                        df = df_chunks
                        cols = [c.lower() for c in df.columns]
                        kw_col = next((c for c in cols if 'keyword' in c or 'termo' in c), None)
                        vol_col = next((c for c in cols if 'volume' in c or 'search' in c), None) or kw_col

                        if not kw_col:
                            log(f"❌ Nenhuma coluna de palavras-chave encontrada em {f.name}")
                            continue

                        df.columns = cols
                        df = df[df[kw_col].notnull()]
                        df['keyword_cleaned'] = df[kw_col].astype(str).str.lower().apply(
                            lambda x: ' '.join(w for w in x.split() if w not in remove_words)
                        )
                        df = df[df['keyword_cleaned'] != '']
                        df['volume'] = pd.to_numeric(df[vol_col], errors='coerce').fillna(0).astype(int)
                        df['source'] = f.name
                        all_keywords.append(df[['keyword_cleaned', 'volume', 'source']])
                    log(f"✅ {f.name}: {sum(len(df) for df in all_keywords if df['source'].iloc[0] == f.name)} entradas válidas")
                except Exception as e:
                    log(f"❌ Erro em {f.name}: {str(e)}")

                progress_bar.progress((i + 1) / total_files, text=f"Processando {f.name} ({int((i + 1) / total_files * 100)}%)")

            if all_keywords:
                log("🧮 Combinando e deduplicando...")
                df_all = pd.concat(all_keywords)
                if mode == 'Global - Remove Todas as Duplicatas':
                    df_final = df_all.drop_duplicates(subset='keyword_cleaned')
                elif mode == 'Por Arquivo - Mantém se vierem de arquivos diferentes':
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
                    st.markdown('<div class="section-container">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Original</div><div class="metric-value">{total_original:,.0f}</div></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Após Deduplicação</div><div class="metric-value">{total_final:,.0f}</div></div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Volume Total</div><div class="metric-value">{volume_total:,.0f}</div></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                csv = df_final.to_csv(index=False).encode('utf-8')
                with button_col2:
                    download_button_placeholder.download_button(
                        label="📥 Baixar Resultado (CSV)",
                        data=csv,
                        file_name=f"keywords_processadas_{uuid.uuid4().hex[:8]}.csv",
                        mime="text/csv"
                    )
                st.dataframe(df_final.head(50), use_container_width=True)
            else:
                log("⚠️ Nenhum dado válido encontrado.")

            progress_bar.empty()
