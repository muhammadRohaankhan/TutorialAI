import os
import pandas as pd

def update_csv_file(file_path, data):
    df = pd.DataFrame(data)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)  
    else:
        df.to_csv(file_path, index=False)

def save_token_cost_data(file_path, token_data):
    token_df = pd.DataFrame(token_data)
    if os.path.exists(file_path):
        token_df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        token_df.to_csv(file_path, index=False)