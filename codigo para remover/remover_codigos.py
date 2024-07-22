import pandas as pd


def remove_codes_from_csv(input_csv_path, output_csv_path, codes_txt_path):
    # Lê o arquivo CSV com o delimitador correto
    df = pd.read_csv(input_csv_path, header=None, sep=';')

    # Lê os códigos a serem removidos do arquivo de texto
    with open(codes_txt_path, 'r') as file:
        codes_to_remove = [line.strip()
                           for line in file.readlines() if line.strip()]

    # Remove as linhas com os códigos mencionados na primeira coluna
    df_filtered = df[~df.iloc[:, 0].astype(str).isin(codes_to_remove)]

    # Salva o novo DataFrame em um novo arquivo CSV
    df_filtered.to_csv(output_csv_path, index=False, header=False, sep=';')
    print(f"Arquivo CSV atualizado salvo como {output_csv_path}")


# Caminho para o arquivo CSV de entrada
input_csv_path = r'C:\Users\Charles\Documents\vscode projetos\estoque finalizado chc 13.07.24.csv'

# Caminho para o arquivo CSV de saída
output_csv_path = r'C:\Users\Charles\Documents\vscode projetos\estoque_finalizado_chc_13.07.24_atualizado.csv'

# Caminho para o arquivo de texto com os códigos a serem removidos
codes_txt_path = r'C:\Users\Charles\Documents\vscode projetos\codigos_para_remover.txt'

# Executa a função
remove_codes_from_csv(input_csv_path, output_csv_path, codes_txt_path)
