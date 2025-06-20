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
    mode = st.selectbox("Modo de Duplicatas",['Global - Remove Todas as Duplicatas', 'Por Arquivo - Mantén se vierem de arquivos diferentes','Mesclar - Remove Duplicatas e Soma os Volumes'], index=2)

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

# Resto do processamento virá depois disso
