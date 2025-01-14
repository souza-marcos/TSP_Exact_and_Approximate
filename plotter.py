import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

# Function to parse data from a single file
def parse_file(filepath):
    data = {}
    with open(filepath, 'r') as file:
        for line in file:
            if match := re.match(r"Instancia: (.+)", line):
                data['Instancia'] = match.group(1)
            elif match := re.match(r"Algoritmo: (.+)", line):
                data['Algoritmo'] = match.group(1)
            elif match := re.match(r"Custo Otimo da Instancia: (.+)", line):
                data['Custo Otimo'] = float(match.group(1))
            elif match := re.match(r"Custo Encontrado: (.+)", line):
                data['Custo Encontrado'] = float(match.group(1))
            elif match := re.match(r"Tempo Decorrido: (.+) segundos", line):
                data['Tempo'] = float(match.group(1))
            elif match := re.match(r"Memoria Atual: (.+) MB", line):
                data['Memoria Atual'] = float(match.group(1))
            elif match := re.match(r"Memoria de Pico: (.+) MB", line):
                data['Memoria Pico'] = float(match.group(1))
                
    with open(filepath, 'r') as file:
        line = file.readlines()[-1]
        nameFile = (filepath
                    .split('/')[-1]
                    .split('.')[0])

        # Get just the numbers
        part = nameFile.split('_')[0]
        for i, el in enumerate(part):
            if el.isdigit():
                part = part[i:] 
                break
        
        data['Tamanho'] = int(part)
        
        nameFile = nameFile.split('_')[1]
        
        data['Timeout'] = False
        if re.match(r"Timeout(.+)", line):  
            data['Timeout'] = True
            data['Algoritmo'] = 'Christofides' if nameFile == 'chris' else 'Twice Around The Tree'
            
    return data

# Function to load data from multiple files
def load_data_from_files(directory):
    dataset = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            dataset.append(parse_file(filepath))
    return pd.DataFrame(dataset)

# Plot comparison charts
def plot_comparisons(df):
    df.sort_values(by=['Tamanho'], inplace=True)
    
    timeoutRows = df[df['Timeout'] == True].copy()
    freeTime = df[df['Timeout'] == False].copy()

    # latex = df[['Instancia', 'Algoritmo', 'Tamanho', 'Custo Encontrado', 'Custo Otimo',  'Tempo', 'Memoria Pico']].copy()

    # # Format float columns
    # for col in ['Custo Encontrado', 'Custo Otimo', 'Memoria Pico', 'Tempo']:
    #     latex[col] = latex[col].apply(lambda x: f"{x:.2f}" if not np.isnan(x) else "NaN")
    
    # # twice around the tree => TAT
    # latex['Algoritmo'] = latex['Algoritmo'].apply(lambda x: 'TAT' if x == 'Twice Around The Tree' else 'Christofides')
    
    # latex['Custo Otimo'] = latex['Custo Otimo'].apply(lambda x: "NaN" if x == "NaN" else int(float(x)))

    # latex = latex.groupby(['Instancia', 'Algoritmo']).first().sort_values(by=['Tamanho']).reset_index()
   
    # result = ''
    # multirow = ''
    # for i in range(len(latex)):
    #     line = latex.iloc[i]
        
    #     if i % 2 == 0:
    #         multirow += "\\multirow{2}{4em}{" + line['Instancia'] + "} & "
    #     else: multirow += "\t\t\t\t& "
        
    #     multirow += f"{line['Tamanho']} & {line['Algoritmo']} & {line['Custo Encontrado']} & {line['Custo Otimo']} & {line['Tempo']} & {line['Memoria Pico']} \\\\ \n"
        
    #     if i % 2 == 1:
    #         result += multirow + "\\hline\n"
    #         multirow = ''

    # with open('output_table.tex', 'w') as f:
    #     f.write(result)
 

    import seaborn as sns
    sns.set_theme(style="whitegrid")

    # fig, ax = plt.subplots()
    # sns.scatterplot(x='Tamanho', y='Tempo', data=freeTime, hue='Algoritmo', ax=ax)
    
    # Fator de aproximação
    freeTime['Fator de Aproximacao'] = freeTime['Custo Encontrado'] / freeTime['Custo Otimo']
    
    
    # Set the width and height of the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='Tamanho', y='Fator de Aproximacao', data=freeTime, hue='Algoritmo', ax=ax)
    
    # Add a median line 
    median_chris = freeTime[freeTime['Algoritmo'] == 'Christofides']['Fator de Aproximacao'].median()
    median_tat = freeTime[freeTime['Algoritmo'] == 'Twice Around The Tree']['Fator de Aproximacao'].median()
    
    ax.axhline(median_chris, color='orange', linestyle='--')
    ax.axhline(median_tat, color='blue', linestyle='--')
    
    plt.savefig("fator_aproximacao.png", format='png')
    
    
    fix, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='Tamanho', y='Tempo', data=freeTime, hue='Algoritmo', ax=ax)
    sns.lineplot(x='Tamanho', y='Tempo', data=freeTime, hue='Algoritmo', ax=ax)
    plt.savefig("tempo.png", format='png')
    
    # Space consuming
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='Tamanho', y='Memoria Pico', data=freeTime, hue='Algoritmo', ax=ax)
    sns.lineplot(x='Tamanho', y='Memoria Pico', data=freeTime, hue='Algoritmo', ax=ax)
    plt.savefig("memoria.png", format='png')
    
    
    

# Main function
def main():
    directory = 'output'  # Directory containing the text files

    df = load_data_from_files(directory)
    plot_comparisons(df)

if __name__ == "__main__":
    main()
