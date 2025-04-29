export const MPythonCode =
`import pandas as pd
import numpy as np

def load_data(file_path):
    return pd.read_csv(file_path)

def preprocess_data(df):
    df = df.fillna(0)
    
    df = df[df['value'] < df['value'].quantile(0.99)]
    
    return df

def main():
    data = load_data('vietnam_branch_product_a.csv')
    
    processed_data = preprocess_data(data)
    
    print(processed_data.shape)
    print(processed_data.describe())

if __name__ == "__main__":
    main()`
