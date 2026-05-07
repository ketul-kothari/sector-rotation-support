import csv

def extract_symbols_to_string(file_path):
    symbols = []
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None) 
        
        for row in csv_reader:
            if row: 
                raw_symbol = row[0]
                cleaned_symbol = raw_symbol.replace('-', '_')
                final_symbol = f"NSE:{cleaned_symbol}"
                symbols.append(final_symbol) 
                
    # THE FIX: Joining with just a comma. Zero spaces allowed.
    formatted_string = ",".join(symbols)
    return formatted_string

if __name__ == "__main__":
    input_file = 'stocks.csv' 
    output_file = 'stocks.txt'
    
    try:
        result = extract_symbols_to_string(input_file)
        
        with open(output_file, mode='w', encoding='utf-8') as out_file:
            out_file.write(result)
            
        print(f"Success! Your file '{output_file}' is perfectly formatted for TradingView.")
        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{input_file}'.")