import argparse
import os
import shutil
import numpy as np
import pandas as pd


def get_parser():
    parser = argparse.ArgumentParser(
        description="Deterministically split dataset, organize files, and generate metadata .npy files."
    )
    parser.add_argument(
        "--csv_path",
        type=str,
        required=True,
        help="Path to the master dataset CSV file.",
    )
    parser.add_argument(
        "--data_root",
        type=str,
        default="./",
        help="Root directory where the original CSV paths can be resolved.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./",
        help="Directory where the new train/dev/test folders will be created.",
    )
    parser.add_argument(
        "--anno_save_dir",
        type=str,
        default="./preprocess/Egy-ArSLT",
        help="Directory where output .npy metadata and split CSVs should be saved.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible shuffling and splitting.",
    )
    parser.add_argument(
        "--train_ratio",
        type=float,
        default=0.70,
        help="Ratio for training set (default: 0.70).",
    )
    parser.add_argument(
        "--val_ratio",
        type=float,
        default=0.20,
        help="Ratio for validation/dev set (default: 0.20).",
    )
    parser.add_argument(
        "--move_files",
        action="store_true",
        help="If set, physically moves video files from data/ to {split}/ folders.",
    )
    parser.add_argument(
        "--copy_instead",
        action="store_true",
        help="If set along with --move_files, copies files instead of moving them.",
    )
    return parser


def clean_relative_path(orig_path: str) -> str:
    """Strips leading 'data/' or initial root path component to isolate subfolder/file."""
    parts = orig_path.replace("\\", "/").split("/")
    if parts[0] == "data":
        return "/".join(parts[1:])
    return "/".join(parts)


def main():
    args = get_parser().parse_args()

    np.random.seed(args.seed)
    df = pd.read_csv(args.csv_path)
    total_samples = len(df)
    print(f"Loaded {total_samples} samples from {args.csv_path}")

    df_shuffled = df.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

    n_train = int(total_samples * args.train_ratio)
    n_dev = int(total_samples * args.val_ratio)

    splits = {
        "train": df_shuffled.iloc[:n_train].copy(),
        "dev": df_shuffled.iloc[n_train : n_train + n_dev].copy(),
        "test": df_shuffled.iloc[n_train + n_dev :].copy(),
    }

    print(f"Split distribution: train={len(splits['train'])}, dev={len(splits['dev'])}, test={len(splits['test'])}")

    os.makedirs(args.anno_save_dir, exist_ok=True)
    
    missing_files_count = 0

    for split_name, split_df in splits.items():
        npy_dict = {}
        new_relative_paths = []

        for idx, (_, row) in enumerate(split_df.iterrows()):
            orig_rel_path = row["Path"]
            sub_path = clean_relative_path(orig_rel_path)

            new_rel_path = f"{split_name}/{sub_path}"
            new_relative_paths.append(new_rel_path)

            folder_id = sub_path.split("/")[0] if "/" in sub_path else ""
            file_base = os.path.splitext(os.path.basename(sub_path))[0]
            fileid = f"{folder_id}_{file_base}" if folder_id else file_base

            npy_dict[idx] = {
                "fileid": fileid,
                "folder": os.path.join(args.output_dir, new_rel_path),
            }

            if args.move_files:
                src = os.path.join(args.data_root, orig_rel_path)
                dst = os.path.join(args.output_dir, new_rel_path)

                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    if args.copy_instead:
                        shutil.copy2(src, dst)
                    else:
                        shutil.move(src, dst)
                else:
                    print(f"Warning: Source file not found -> {src}")
                    missing_files_count += 1

        npy_dict["prefix"] = f"{split_name}_prefix"
        npy_out_path = os.path.join(args.anno_save_dir, f"{split_name}_info.npy")
        np.save(npy_out_path, npy_dict)

        # Overwrite the 'Path' column with the new relative paths
        split_df["Path"] = new_relative_paths
        csv_out_path = os.path.join(args.anno_save_dir, f"{split_name}.csv")
        split_df.to_csv(csv_out_path, index=False)
        
    if missing_files_count > 0:
        print(f"\nCompleted with WARNINGS: {missing_files_count} files could not be found.")
    else:
        print("\nData preparation and file transfers completed successfully.")


if __name__ == "__main__":
    main()

# How To Use
# python prepare_dataset_splits.py \
#     --csv_path ./AR_EGY_SIGN_subset.csv \
#     --data_root ./ \
#     --output_dir ./ \
#     --anno_save_dir ./script_output \
#     --seed 42 \
#     --train_ratio 0.70 \
#     --val_ratio 0.20 \
#     --move_files \
#     --copy_instead