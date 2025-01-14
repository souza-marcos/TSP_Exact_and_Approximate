import os
import pandas as pd

def process_file(file_path):
    data = []
    with open(file_path, 'r') as f:
        content = f.read().strip().splitlines()
        entry = {}
        for line in content:
            if "Instancia:" in line:
                if entry:
                    data.append(entry)
                entry = {'Instancia': line.split(":")[1].strip()}
            elif "Algoritmo:" in line:
                entry['Algoritmo'] = line.split(":")[1].strip()
            elif "Custo Otimo da Instancia:" in line:
                entry['Custo Otimo'] = float(line.split(":")[1].strip())
            elif "Custo Encontrado:" in line:
                entry['Custo Encontrado'] = float(line.split(":")[1].strip())
            elif "Tempo Decorrido:" in line:
                entry['Tempo Decorrido'] = line.split(":")[1].strip()
            elif "Memoria Atual:" in line:
                entry['Memoria Atual'] = line.split(":")[1].strip()
            elif "Memoria de Pico:" in line:
                entry['Memoria Pico'] = line.split(":")[1].strip()
            elif "Timeout" in line:
                entry['Algoritmo'] = "Timeout"
                entry['Custo Otimo'] = None
                entry['Custo Encontrado'] = None
                entry['Tempo Decorrido'] = None
                entry['Memoria Atual'] = None
                entry['Memoria Pico'] = None
        if entry:
            data.append(entry)
    
    # Add "Branch and Bound" row
    if data:
        data.append({
            'Instancia': data[0]['Instancia'],
            'Algoritmo': "Branch and Bound",
            'Custo Otimo': None,
            'Custo Encontrado': None,
            'Tempo Decorrido': None,
            'Memoria Atual': None,
            'Memoria Pico': None
        })
    
    return data

def generate_latex_table(data):
    """
    Generates a LaTeX table from the processed data.
    """
    df = pd.DataFrame(data)
    
    df = df.groupby(['Instancia', 'Algoritmo']).first().reset_index()
    latex = df.to_latex(index=False, na_rep="NaN", escape=False, longtable=True)
    return latex

def main():
    input_dir = "output"  # Replace with your directory containing input files
    output_file = "output_table.tex"

    # Process all files in the directory
    all_data = []
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isfile(file_path):
            file_data = process_file(file_path)
            all_data.extend(file_data)
        
    
    # Generate LaTeX table
    latex_table = generate_latex_table(all_data)
    
    # Save to file
    with open(output_file, "w") as f:
        f.write(latex_table)

    print(f"LaTeX table saved to {output_file}")

if __name__ == "__main__":
    main()
