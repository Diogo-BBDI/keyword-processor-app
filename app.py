```python
import streamlit as st
import pandas as pd
import io
import os
import time

st.set_page_config(page_title="Keyword Processor Pro", layout="wide", initial_sidebar_state="collapsed")

# CSS Professional Dark Theme com ajustes
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset e Base */
* {
    box-sizing: border-box;
}

.stApp {
    background: linear-gradient(135deg, #0a0b0f 0%, #1a1d29 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #f8fafc;
    min-height: 100vh;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Header Section */
.header-container {
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(71, 85, 105, 0.2);
    border-radius: 20px;
    padding: 0.5rem 2rem;
    margin-top: 0 !important;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Card System */
.card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1–

1px solid rgba(71, 85, 105, 0.2);
}

.card-icon {
    font-size: 1.5rem;
    opacity: 0.8;
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 0;
}

/* Metrics Cards */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.metric-card {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 0.25rem;
    display: block;
}

.metric-label {
    font-size: 0.875rem;
    color: #94a3b8;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.3s ease;
    width: 100%;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(0);
}

/* Estilo para botão desativado */
.stDownloadButton > button:disabled {
    background: linear-gradient(135deg, #64748b, #475569);
    color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
}

/* File Uploader */
.stFileUploader > div {
    border-radius: 10px;
    border: 2px dashed rgba(71, 85, 105, 0.4);
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: rgba(59, 130, 246, 0.6);
    background: rgba(59, 130, 246, 0.05);
}

/* Select Boxes */
.stSelectbox > div > div {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 8px;
}

.stMultiSelect > div > div {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 8px;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 10px;
}

/* Log Box */
.log-container {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 12px;
    padding: 1rem;
    height: 320px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.4;
    color: #cbd5e1;
    scrollbar-width: thin;
    scrollbar-color: rgba(71, 85, 105, 0.5) transparent;
}

.log-container::-webkit-scrollbar {
    width: 6px;
}

.log-container::-webkit-scrollbar-track {
    background: transparent;
}

.log-container::-webkit-scrollbar-thumb {
    background: rgba(71, 85, 105, 0.5);
    border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb:hover {
    background: rgba(71, 85, 105, 0.7);
}

/* Labels */
label, .css-1kyxreq, .css-14xtw13, .css-81oif8, .css-1aumxhk {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

/* Status Messages */
.status-success {
    color: #10b981;
    font-weight: 500;
}

.status-error {
    color: #ef4444;
    font-weight: 500;
}

.status-warning {
    color: #f59e0b;
    font-weight: 500;
}

.status-info {
    color: #3b82f6;
    font-weight: 500;
}

/* Enhanced Components */
.stExpander {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 10px;
    margin: 0.5rem 0;
}

.stExpander > div > div > div {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

.processing-status {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.feature-badge {
    display: inline-block;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.25rem;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.info-panel {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    color: #93c5fd;
    font-size: 0.875rem;
}

.warning-panel {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    color: #fbbf24;
    font-size: 0.875rem;
}

.success-panel {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    color: #6ee7b7;
    font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 768px) {
    .header-title {
        font-size: 2rem;
    }
    
    .card {
        padding: 1rem;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .header-container {
        padding: 1.5rem;
    }
}

/* Table Styling */
.stDataFrame {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(71, 85, 105, 0.3);
}

/* Spacing */
.section-spacer {
    margin: 2rem 0;
}

.small-spacer {
    margin: 1rem 0;
}

/* Ajuste para alinhamento dos botões */
.button-container {
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: flex-start;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Header with features
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🚀 Keyword Processor Pro</h1>
    <p class="header-subtitle">
        Ferramenta profissional para processamento e análise de palavras-chave com deduplicação inteligente
    </p>
    <div style="margin-top: 1rem;">
        <span class="feature-badge">📊 Múltiplos Formatos</span>
        <span class="feature-badge">🔄 Deduplicação Inteligente</span>
        <span class="feature-badge">⚡ Processamento Rápido</span>
        <span class="feature-badge">📈 Análise de Volume</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics placeholder
metrics_container = st.empty()

# Main layout
col_left, col_right = st.columns([1.4, 1])

with col_left:
    # Upload Section
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span class="card-icon">📁</span>
            <h3 class="card-title">Upload de Arquivos</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Arquivos de Palavras-chave**")
    keyword_files = st.file_uploader(
        "Selecione arquivos CSV ou XLSX com suas palavras-chave",
        type=['csv', 'xlsx'], 
        accept_multiple_files=True,
        help="Suporta múltiplos arquivos. Colunas aceitas: 'keyword', 'termo', 'volume', 'search'"
    )
    
    st.markdown("<div class='small-spacer'></div>", unsafe_allow_html=True)
    
    st.markdown("**Arquivos de Exclusão (Opcional)**")
    exclusion_files = st.file_uploader(
        "Arquivos TXT com termos a serem removidos (uma palavra por linha)",
        type=['txt'], 
        accept_multiple_files=True,
        help="Palavras listadas nesses arquivos serão removidas das keywords"
    )
    
    # Preset exclusions section
    st.markdown("<div class='small-spacer'></div>", unsafe_allow_html=True)
    
    with st.expander("🎯 **Exclusões Predefinidas**", expanded=False):
        PRESET_DIR = "exclusoes_predefinidas"
        os.makedirs(PRESET_DIR, exist_ok=True)
        preset_files = [f for f in os.listdir(PRESET_DIR) if f.endswith('.txt')]
        
        if preset_files:
            selected_presets = st.multiselect(
                "Arquivos de exclusão disponíveis",
                preset_files,
                help="Selecione arquivos predefinidos para exclusão automática"
            )
            
            # Show preset info
            if selected_presets:
                total_preset_words = 0
                for preset in selected_presets:
                    try:
                        with open(os.path.join(PRESET_DIR, preset), 'r', encoding='utf-8') as f:
                            words = len([line for line in f.readlines() if line.strip()])
                            total_preset_words += words
                    except:
                        pass
                
                st.info(f"📊 {len(selected_presets)} arquivo(s) selecionado(s) com ~{total_preset_words} palavras")
        else:
            selected_presets = []
            st.info("💡 Nenhum arquivo predefinido encontrado. Adicione arquivos .txt na pasta 'exclusoes_predefinidas' para usar esta funcionalidade.")
            
            # Quick preset creator
            st.markdown("**Criar Preset Rápido**")
            col_preset1, col_preset2 = st.columns([2, 1])
            with col_preset1:
                preset_name = st.text_input("Nome do preset", placeholder="ex: stopwords_pt")
            with col_preset2:
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                if st.button("Criar", disabled=not preset_name):
                    # Create basic stopwords preset
                    basic_stopwords = [
                        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
                        "to", "was", "will", "with", "com", "para", "por", "em", "de",
                        "da", "do", "das", "dos", "na", "no", "nas", "nos", "um", "uma"
                    ]
                    try:
                        with open(os.path.join(PRESET_DIR, f"{preset_name}.txt"), 'w', encoding='utf-8') as f:
                            f.write('\n'.join(basic_stopwords))
                        st.success(f"✅ Preset '{preset_name}.txt' criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao criar preset: {str(e)}")

with col_right:
    # Settings Section
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span class="card-icon">⚙️</span>
            <h3 class="card-title">Configurações</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    mode = st.selectbox(
        "**Estratégia de Deduplicação**",
        options=[
            'Mesclar - Remove Duplicatas e Soma os Volumes',
            'Global - Remove Todas as Duplicatas',
            'Por Arquivo - Mantém se vierem de arquivos diferentes'
        ],
        index=0,
        help="• **Mesclar**: Combina volumes de palavras duplicadas\n• **Global**: Remove todas as duplicatas\n• **Por Arquivo**: Mantém duplicatas de arquivos diferentes"
    )
    
    # Advanced settings
    with st.expander("⚙️ **Configurações Avançadas**", expanded=False):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            min_volume = st.number_input(
                "Volume mínimo",
                min_value=0,
                value=0,
                help="Filtrar palavras com volume menor que este valor"
            )
            
        with col_adv2:
            max_results = st.number_input(
                "Máximo de resultados",
                min_value=0,
                value=0,
                help="Limitar número de resultados (0 = sem limite)"
            )
        
        case_sensitive = st.checkbox(
            "Diferenciação de maiúsculas/minúsculas",
            value=False,
            help="Tratar 'Keyword' e 'keyword' como diferentes"
        )
        
        sort_by = st.selectbox(
            "Ordenar por",
            ["Volume (Decrescente)", "Volume (Crescente)", "Alfabética", "Sem ordenação"],
            help="Como ordenar os resultados finais"
        )
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Process Section
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span class="card-icon">🔄</span>
            <h3 class="card-title">Processamento</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress and status
    progress_status = st.empty()
    progress_bar = st.progress(0)
    
    # Estado inicial do botão de download
    if 'download_data' not in st.session_state:
        st.session_state.download_data = b""  # Valor padrão seguro (bytes vazios)
        st.session_state.download_filename = "resultados.csv"
        st.session_state.download_mime = "text/csv"
    
    # Control buttons
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    button_col1, button_col2 = st.columns([1, 1])
    with button_col1:
        start_button = st.button("🚀 Processar", type="primary")
    with button_col2:
        download_label = f"📥 Baixar {st.session_state.get('export_format', 'CSV')}"
        download_placeholder = st.download_button(
            label=download_label,
            data=st.session_state.download_data,
            file_name=st.session_state.download_filename,
            mime=st.session_state.download_mime,
            disabled=st.session_state.download_data == b"",
            type="secondary"
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Log Section
st.markdown("""
<div class="card">
    <div class="card-header">
        <span class="card-icon">📊</span>
        <h3 class="card-title">Log de Processamento</h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Log container
log_buffer = []
log_container = st.empty()

# Initialize empty log
log_container.markdown(f'<div class="log-container">🔄 Sistema iniciado. Aguardando processamento...</div>', unsafe_allow_html=True)

def log(message, status_type="info"):
    timestamp = time.strftime("[%H:%M:%S]")
    status_class = f"status-{status_type}"
    formatted_message = f'<span class="{status_class}">{timestamp} {message}</span>'
    log_buffer.append(formatted_message)
    
    # Keep only last 50 messages
    if len(log_buffer) > 50:
        log_buffer.pop(0)
    
    log_html = '<br>'.join(log_buffer)
    log_container.markdown(f'<div class="log-container">{log_html}</div>', unsafe_allow_html=True)

# Processing logic
if start_button:
    if not keyword_files:
        st.error("⚠️ Por favor, envie pelo menos um arquivo de palavras-chave.")
        log("❌ Nenhum arquivo de palavras-chave enviado", "error")
    else:
        # Initialize processing
        progress_status.info("🔄 Iniciando processamento...")
        log("🚀 Iniciando processamento de palavras-chave", "info")
        
        # Collect exclusion words
        remove_words = set()
        log("📋 Carregando palavras de exclusão...", "info")
        
        # Process uploaded exclusion files
        exclusion_count = 0
        for txt_file in exclusion_files or []:
            try:
                lines = txt_file.read().decode('utf-8'). personally_splitlines()
                new_words = {line.strip().lower() for line in lines if line.strip()}
                remove_words.update(new_words)
                exclusion_count += len(new_words)
                log(f"✅ {txt_file.name}: {len(new_words)} palavras carregadas", "success")
            except Exception as e:
                log(f"❌ Erro ao ler {txt_file.name}: {str(e)}", "error")
        
        # Process preset exclusion files
        for preset_name in selected_presets:
            try:
                with open(os.path.join(PRESET_DIR, preset_name), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    new_words = {line.strip().lower() for line in lines if line.strip()}
                    remove_words.update(new_words)
                    exclusion_count += len(new_words)
                    log(f"✅ {preset_name}: {len(new_words)} palavras carregadas", "success")
            except Exception as e:
                log(f"❌ Erro ao ler preset {preset_name}: {str(e)}", "error")
        
        log(f"📊 Total de {len(remove_words)} palavras únicas para exclusão", "info")
        
        # Process keyword files
        all_keywords = []
        total_files = len(keyword_files)
        processed_files = 0
        
        for i, keyword_file in enumerate(keyword_files):
            progress_bar.progress((i) / total_files)
            progress_status.info(f"📄 Processando {keyword_file.name}... ({i+1}/{total_files})")
            log(f"📄 Processando arquivo: {keyword_file.name}", "info")
            
            try:
                # Read file
                if keyword_file.name.endswith('.csv'):
                    df = pd.read_csv(keyword_file)
                else:
                    df = pd.read_excel(keyword_file)
                
                original_count = len(df)
                log(f"📊 {keyword_file.name}: {original_count} registros carregados", "info")
                
                # Normalize column names
                cols_original = df.columns.tolist()
                cols_lower = [c.lower().strip() for c in df.columns]
                df.columns = cols_lower
                
                # Find keyword and volume columns
                keyword_col = None
                volume_col = None
                
                for col in cols_lower:
                    if any(term in col for term in ['keyword', 'termo', 'palavra']):
                        keyword_col = col
                        break
                
                for col in cols_lower:
                    if any(term in col for term in ['volume', 'search', 'busca', 'vol']):
                        volume_col = col
                        break
                
                if not keyword_col:
                    keyword_col = cols_lower[0]  # Use first column as fallback
                
                if not volume_col:
                    volume_col = keyword_col  # Use keyword column as fallback
                
                log(f"🔍 Colunas identificadas - Keywords: '{keyword_col}', Volume: '{volume_col}'", "info")
                
                # Clean data
                df = df[df[keyword_col].notnull()].copy()
                
                # Clean keywords
                df['keyword_cleaned'] = df[keyword_col].astype(str).str.lower().apply(
                    lambda x: ' '.join(word for word in x.split() if word not in remove_words)
                )
                
                # Remove empty keywords
                df = df[df['keyword_cleaned'].str.strip() != '']
                
                # Handle volume
                if volume_col in df.columns:
                    df['volume'] = pd.to_numeric(df[volume_col], errors='coerce').fillna(0).astype(int)
                else:
                    df['volume'] = 0
                
                # Add source
                df['source'] = keyword_file.name
                
                # Select final columns
                final_df = df[['keyword_cleaned', 'volume', 'source']].copy()
                all_keywords.append(final_df)
                
                processed_files += 1
                valid_count = len(final_df)
                removed_count = original_count - valid_count
                
                log(f"✅ {keyword_file.name}: {valid_count} palavras válidas ({removed_count} removidas)", "success")
                
            except Exception as e:
                log(f"❌ Erro ao processar {keyword_file.name}: {str(e)}", "error")
                continue
        
        progress_bar.progress(1.0)
        
        if all_keywords:
            progress_status.info("🔄 Combinando e deduplicando dados...")
            log("🔄 Iniciando combinação e deduplicação...", "info")
            
            # Combine all data
            df_combined = pd.concat(all_keywords, ignore_index=True)
            total_combined = len(df_combined)
            
            # Apply deduplication based on selected mode
            if 'Global' in mode:
                df_final = df_combined.drop_duplicates(subset='keyword_cleaned').reset_index(drop=True)
                log("🔄 Aplicando deduplicação global", "info")
            elif 'Por Arquivo' in mode:
                df_final = df_combined.drop_duplicates(subset=['keyword_cleaned', 'source']).reset_index(drop=True)
                log("🔄 Aplicando deduplicação por arquivo", "info")
            else:  # Merge mode
                df_final = df_combined.groupby('keyword_cleaned').agg({
                    'volume': 'sum',
                    'source': lambda x: ', '.join(sorted(set(x)))
                }).reset_index()
                log("🔄 Aplicando mesclagem com soma de volumes", "info")
            
            # Apply filters
            if min_volume > 0:
                original_count = len(df_final)
                df_final = df_final[df_final['volume'] >= min_volume]
                filtered_count = original_count - len(df_final)
                if filtered_count > 0:
                    log(f"🔍 Filtro de volume: {filtered_count} registros removidos (volume < {min_volume})", "info")
            
            # Apply sorting
            if "Volume (Decrescente)" in sort_by:
                df_final = df_final.sort_values('volume', ascending=False)
                log("📊 Resultados ordenados por volume (decrescente)", "info")
            elif "Volume (Crescente)" in sort_by:
                df_final = df_final.sort_values('volume', ascending=True)
                log("📊 Resultados ordenados por volume (crescente)", "info")
            elif "Alfabética" in sort_by:
                df_final = df_final.sort_values('keyword_cleaned')
                log("📊 Resultados ordenados alfabeticamente", "info")
            
            # Apply result limit
            if max_results > 0 and len(df_final) > max_results:
                df_final = df_final.head(max_results)
                log(f"🔢 Limitando resultados a {max_results} registros", "info")
            
            # Calculate final metrics
            total_original = sum(len(df) for df in all_keywords)
            total_final = len(df_final)
            total_volume = df_final['volume'].sum()
            total_removed = total_original - total_final
            
            # Display final metrics
            metrics_html = f"""
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{total_original:,}</span>
                    <span class="metric-label">Total Original</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{total_final:,}</span>
                    <span class="metric-label">Após Processamento</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{total_removed:,}</span>
                    <span class="metric-label">Removidas</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{total_volume:,}</span>
                    <span class="metric-label">Volume Total</span>
                </div>
            </div>
            """
            metrics_container.markdown(metrics_html, unsafe_allow_html=True)
            
            # Final logs
            log("🎉 Processamento concluído com sucesso!", "success")
            log(f"📊 Estatísticas finais:", "info")
            log(f"   • Registros originais: {total_original:,}", "info")
            log(f"   • Registros finais: {total_final:,}", "info")
            log(f"   • Registros removidos: {total_removed:,}", "info")
            log(f"   • Volume total: {total_volume:,}", "info")
            
            # Display preview with enhanced info
            st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
            
            preview_col1, preview_col2 = st.columns([2, 1])
            
            with preview_col1:
                st.markdown("### 📋 Prévia dos Resultados")
            
            with preview_col2:
                # Export options
                export_format = st.selectbox(
                    "Formato de exportação",
                    ["CSV", "Excel", "TSV"],
                    help="Escolha o formato para download"
                )
                st.session_state.export_format = export_format  # Armazenar formato selecionado
            
            # Show data quality insights
            if len(df_final) > 0:
                avg_volume = df_final['volume'].mean()
                median_volume = df_final['volume'].median()
                max_volume = df_final['volume'].max()
                zero_volume = len(df_final[df_final['volume'] == 0])
                
                st.markdown(f"""
                <div class="info-panel">
                    📊 <strong>Insights dos Dados:</strong><br>
                    • Volume médio: {avg_volume:,.0f} | Volume mediano: {median_volume:,.0f}<br>
                    • Maior volume: {max_volume:,.0f} | Registros sem volume: {zero_volume:,}<br>
                    • Fontes únicas: {df_final['source'].nunique()}
                </div>
                """, unsafe_allow_html=True)
            
            # Prepare download based on format
            if export_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Keywords')
                file_data = output.getvalue()
                file_ext = "xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif export_format == "TSV":
                file_data = df_final.to_csv(index=False, sep='\t', encoding='utf-8').encode('utf-8')
                file_ext = "tsv"
                mime_type = "text/tab-separated-values"
            else:  # CSV
                file_data = df_final.to_csv(index=False, encoding='utf-8').encode('utf-8')
                file_ext = "csv"
                mime_type = "text/csv"
            
            # Atualizar estado do botão de download
            st.session_state.download_data = file_data
            st.session_state.download_filename = f"keywords_processadas_{time.strftime('%Y%m%d_%H%M%S')}.{file_ext}"
            st.session_state.download_mime = mime_type
            
            st.dataframe(
                df_final.head(100), 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "keyword_cleaned": st.column_config.TextColumn("Palavra-chave", width="large"),
                    "volume": st.column_config.NumberColumn("Volume", format="%d"),
                    "source": st.column_config.TextColumn("Fonte", width="medium")
                }
            )
            
        else:
            progress_status.error("❌ Nenhum dado válido foi processado.")
            log("❌ Processamento falhou - nenhum dado válido encontrado", "error")
        
        progress_bar.empty()
```
