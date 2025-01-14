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

    # plotting tamanho x tempo
    fig, ax = plt.subplots()
    ax.plot(freeTime['Tamanho'], freeTime['Tempo'], label='Tempo de Execução')
    ax.plot(timeoutRows['Tamanho'], timeoutRows['Tempo'], label='Timeout')
    ax.set_xlabel('Tamanho')
    ax.set_ylabel('Tempo (s)')
    ax.set_title('Tamanho x Tempo de Execução')
    ax.legend()
    plt.show()
    
    
    
    

# Main function
def main():
    directory = 'output'  # Directory containing the text files

    df = load_data_from_files(directory)
    plot_comparisons(df)

if __name__ == "__main__":
    main()
