import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
INPUT_FILE = "nse_equity_with_sector.csv"
MIN_MCAP = 1000                # Minimum Market Cap in Crores
MIN_YEARS_LISTED = 1           # Minimum listing age in years
TOP_N_STOCKS = 39              # Max stocks per Pine Script call
EXCHANGE_PREFIX = "NSE"        # Prefix for Pine Script

def generate_pine_automation():
    # 1. Load Data
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    # 2. Pre-processing
    df['symbol'] = df['symbol'].astype(str).str.replace('-', '_', regex=False)
    df['listing_date'] = pd.to_datetime(df['listing_date'], format='%d-%b-%Y', errors='coerce')
    df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
    
    # 3. Apply Filters
    one_year_ago = datetime.now() - timedelta(days=365 * MIN_YEARS_LISTED)
    mask = (df['listing_date'] <= one_year_ago) & (df['market_cap'] >= MIN_MCAP)
    filtered_df = df[mask].copy()
    
    # 4. Core Formula Generator (Equal-Weighted Update)
    def build_pine_string(group):
        if group.empty: return ""
        # Still sort by market cap to grab the largest 39 stocks
        top_stocks = group.sort_values(by='market_cap', ascending=False).head(TOP_N_STOCKS).copy()
        
        # Omit the weight calculations entirely. Just append Exchange + Symbol.
        parts = [f"{EXCHANGE_PREFIX}:{row['symbol']}" for _, row in top_stocks.iterrows()]
        return ", ".join(parts)

    # 5. Process Categories
    results = []
    
    for category_name, col_name in [("Industry", "industry"), ("Basic Industry", "basic_industry")]:
        # Get unique names, drop NaNs, and sort
        unique_names = sorted([name for name in df[col_name].unique() if pd.notna(name)])
        
        # Generate the Dropdown Options List
        options_code = f"// {category_name} Dropdown Options\noptions=[\n     " + \
                       ", ".join([f'"{n}"' for n in unique_names]) + "\n     ]"
        
        # Generate the Switch Logic
        switch_lines = [f"// {category_name} Switch Statement"]
        for name in unique_names:
            group = filtered_df[filtered_df[col_name] == name]
            data_str = build_pine_string(group)
            switch_lines.append(f'    "{name}" => "{data_str}"')
        
        results.append(options_code)
        results.append("\n".join(switch_lines) + '\n    => ""')

    # 6. Save to Text File
    with open('pine_script_snippets.txt', 'w') as f:
        f.write("\n\n" + "="*50 + "\n")
        f.write(" COPY AND PASTE THE BLOCKS BELOW INTO PINE SCRIPT \n")
        f.write("="*50 + "\n\n")
        f.write("\n\n".join(results))

    print("Success! Open 'pine_script_snippets.txt' to copy your code.")

if __name__ == "__main__":
    generate_pine_automation()