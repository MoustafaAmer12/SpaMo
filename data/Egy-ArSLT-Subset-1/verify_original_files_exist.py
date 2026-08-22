import os
import pandas as pd

def verify_paths(csv_filename):
    # Read the CSV
    df = pd.read_csv(csv_filename)
    
    if 'Path' not in df.columns:
        print("Error: 'Path' column missing.")
        return
        
    # Apply a function to check if each path exists
    # We convert to string in case there are missing/NaN values
    df['File_Exists'] = df['Path'].astype(str).apply(os.path.exists)
    
    # Filter for rows where the file does NOT exist
    missing_df = df[~df['File_Exists']]
    
    if not missing_df.empty:
        print(f"❌ Found {len(missing_df)} missing files.")
        print(missing_df[['Path']]) # Prints the missing paths
    else:
        print("✅ All files exist!")

if __name__ == "__main__":
    verify_paths('AR_EGY_SIGN_subset.csv')