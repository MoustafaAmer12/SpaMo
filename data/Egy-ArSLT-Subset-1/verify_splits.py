import argparse
import os
import pandas as pd


def get_parser():
    parser = argparse.ArgumentParser(
        description="Verify dataset splits mapping and physical file existence."
    )
    parser.add_argument(
        "--master_csv",
        type=str,
        required=True,
        help="Path to the original master CSV.",
    )
    parser.add_argument(
        "--split_dir",
        type=str,
        default="./preprocess/Egy-ArSLT",
        help="Directory containing the generated train.csv, dev.csv, and test.csv.",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./",
        help="Base directory where the new train/, dev/, and test/ folders are located.",
    )
    return parser

def clean_master_path(orig_path: str) -> str:
    """Extracts the core sub-path from the master CSV (e.g., 'data/folder/vid.mp4' -> 'folder/vid.mp4')."""
    parts = str(orig_path).replace("\\", "/").split("/")
    if parts[0] == "data":
        return "/".join(parts[1:])
    return "/".join(parts)

def clean_split_path(split_path: str) -> str:
    """Extracts the core sub-path from the split CSVs (e.g., 'train/folder/vid.mp4' -> 'folder/vid.mp4')."""
    parts = str(split_path).replace("\\", "/").split("/")
    # The first element will be 'train', 'dev', or 'test', so we skip it
    return "/".join(parts[1:])

def main():
    args = get_parser().parse_args()

    print("Loading CSV files...")
    if not os.path.exists(args.master_csv):
        print(f"Error: Master CSV not found at {args.master_csv}")
        return
        
    master_df = pd.read_csv(args.master_csv)
    
    splits = ["train", "dev", "test"]
    split_dfs = {}
    
    for split in splits:
        csv_path = os.path.join(args.split_dir, f"{split}.csv")
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found.")
            return
        split_dfs[split] = pd.read_csv(csv_path)
        print(f"  Loaded {split}.csv: {len(split_dfs[split])} records.")

    # Convert paths to normalized sub-paths for accurate set logic
    master_subpaths = set(master_df["Path"].apply(clean_master_path))
    train_subpaths = set(split_dfs["train"]["Path"].apply(clean_split_path))
    dev_subpaths = set(split_dfs["dev"]["Path"].apply(clean_split_path))
    test_subpaths = set(split_dfs["test"]["Path"].apply(clean_split_path))

    print("\n--- 1. Verifying Completeness & Disjointness ---")
    
    combined_subpaths = train_subpaths.union(dev_subpaths).union(test_subpaths)
    missing_from_splits = master_subpaths - combined_subpaths
    extra_in_splits = combined_subpaths - master_subpaths

    if not missing_from_splits and not extra_in_splits:
        print("[✅] Completeness: All original files are exactly accounted for in the splits.")
    else:
        if missing_from_splits:
            print(f"[❌] Completeness Error: {len(missing_from_splits)} master files are missing from splits.")
        if extra_in_splits:
            print(f"[❌] Completeness Error: Found {len(extra_in_splits)} extra/unknown files in splits.")

    leak_train_dev = train_subpaths.intersection(dev_subpaths)
    leak_train_test = train_subpaths.intersection(test_subpaths)
    leak_dev_test = dev_subpaths.intersection(test_subpaths)

    if not leak_train_dev and not leak_train_test and not leak_dev_test:
        print("[✅] Disjointness: No data leakage found between splits.")
    else:
        if leak_train_dev: print(f"[❌] LEAKAGE: {len(leak_train_dev)} files in both train and dev.")
        if leak_train_test: print(f"[❌] LEAKAGE: {len(leak_train_test)} files in both train and test.")
        if leak_dev_test: print(f"[❌] LEAKAGE: {len(leak_dev_test)} files in both dev and test.")

    print("\n--- 2. Verifying Physical File Existence ---")
    
    missing_physical_files = []
    
    for split in splits:
        df = split_dfs[split]
        split_missing = 0
        
        for _, row in df.iterrows():
            # Uses the overwritten Path column which now looks like 'train/folder/vid.mp4'
            split_path = row["Path"] 
            full_path = os.path.join(args.data_dir, split_path)
            
            if not os.path.exists(full_path):
                missing_physical_files.append(full_path)
                split_missing += 1
        
        if split_missing == 0:
            print(f"[✅] {split}: All {len(df)} mapped files exist on disk.")
        else:
            print(f"[❌] {split}: {split_missing} files missing on disk.")

    if missing_physical_files:
        print(f"\n[!] Verification Failed: {len(missing_physical_files)} total files are missing from the disk.")
        print("First 5 missing file paths:")
        for p in missing_physical_files[:5]:
            print(f"  - {p}")
    else:
        print("\n[✅] VERIFICATION SUCCESS: Split mapping is perfect and all files exist on disk.")


if __name__ == "__main__":
    main()

# python verify_splits.py \
#     --master_csv ./AR_EGY_SIGN_subset.csv \
#     --split_dir ./script_output \
#     --data_dir ./