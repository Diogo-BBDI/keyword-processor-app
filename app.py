import pandas as pd
import time

# Medir o tempo de execução
start_time = time.time()

# Configurações
csv_file = 'keywords.csv'  # Arquivo CSV de entrada
txt_file = 'remove_words.txt'  # Arquivo com palavras a remover
keyword_column = 'Keyword'  # Nome da coluna de palavras-chave
output_file = 'cleaned_keywords.csv'  # Arquivo de saída

print(f"Processando arquivo: {csv_file}")

# Ler o arquivo TXT com palavras a serem removidas
try:
    print(f"Lendo lista de palavras a remover do arquivo {txt_file}...")
    with open(txt_file, 'r', encoding='utf-8') as file:
        remove_words = set(line.strip().lower() for line in file if line.strip())
    print(f"Carregadas {len(remove_words)} palavras para filtrar")
except FileNotFoundError:
    print(f"Erro: Arquivo {txt_file} não encontrado.")
    exit(1)

try:
    # Verificar se o arquivo CSV existe e suas colunas
    try:
        df_sample = pd.read_csv(csv_file, nrows=1)
        print(f"Colunas disponíveis no CSV: {df_sample.columns.tolist()}")
        
        if keyword_column not in df_sample.columns:
            print(f"Erro: Coluna '{keyword_column}' não encontrada no CSV.")
            exit(1)
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        exit(1)
    
    # Leitura completa do arquivo CSV
    print("Lendo o arquivo CSV completo...")
    df = pd.read_csv(csv_file, usecols=[keyword_column], encoding='utf-8')
    
    # Relatório antes da limpeza
    total_keywords = len(df)
    print(f"Total de palavras-chave antes da limpeza: {total_keywords}")
    
    # Aplicar limpeza
    print("Aplicando limpeza de palavras-chave...")
    print("Isso pode levar alguns minutos devido ao grande número de palavras a serem filtradas.")
    
    # Para melhorar o desempenho, vamos criar um conjunto de palavras exclusivas
    # para processar e depois mapear de volta para o dataframe
    unique_keywords = set(df[keyword_column].dropna().unique())
    print(f"Processando {len(unique_keywords)} palavras-chave únicas...")
    
    # Criar um dicionário de mapeamento {original: limpo}
    keyword_mapping = {}
    for keyword in unique_keywords:
        if pd.isna(keyword):
            keyword_mapping[keyword] = ""
            continue
            
        keyword_str = str(keyword).lower().strip()
        if not keyword_str:
            keyword_mapping[keyword] = ""
            continue
            
        # Dividir a frase em palavras
        words = keyword_str.split()
        # Manter apenas palavras que não estão na lista de remoção
        filtered_words = [word for word in words if word not in remove_words]
        # Reconstruir a frase
        cleaned = ' '.join(filtered_words).strip()
        keyword_mapping[keyword] = cleaned
    
    # Aplicar o mapeamento ao dataframe
    df[keyword_column] = df[keyword_column].map(lambda x: keyword_mapping.get(x, ""))
    
    # Remover palavras-chave vazias
    df = df[df[keyword_column].str.strip() != ""]
    
    # Remover duplicatas
    print("Removendo duplicatas...")
    df_unique = df.drop_duplicates(subset=[keyword_column])
    
    # Relatório após limpeza
    total_after_cleaning = len(df_unique)
    print(f"Total de palavras-chave após limpeza e remoção de duplicatas: {total_after_cleaning}")
    print(f"Removidas {total_keywords - total_after_cleaning} entradas (duplicatas ou vazias)")
    
    # Salvar resultados
    df_unique.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Arquivo limpo salvo como {output_file}")
    
    # Tempo de execução
    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos")

except Exception as e:
    print(f"Erro durante o processamento: {e}")
