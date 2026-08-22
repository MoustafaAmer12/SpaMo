# Dataset Preparation

## Validating Dataset Download

- We need to validate that the videos mentioned in the csv file are actually in the data/ directory.

Run the following script

```
python verify_original_files_exist.py
```

- Now, we need to verify that only the mentioned videos are there

Run the following script

```
./count_files.sh ./data
```

## Generating Dataset Splits

- Now we need to split the whole dataset into train/dev/test splits, create a csv and the npy required for the embeddings extraction for each split and move the videos to the new paths.

Run the following deterministic script (provided the seed)

```
python prepare_dataset_splits.py \
    --csv_path ./AR_EGY_SIGN_subset.csv \
    --data_root ./ \
    --output_dir ./ \
    --anno_save_dir ./script_output \
    --seed 42 \
    --train_ratio 0.70 \
    --val_ratio 0.20 \
    --move_files \
    --copy_instead
```

- Now, verify the splits generated actually map the whole data and correct

Run the following script

```
python verify_splits.py \
    --master_csv ./AR_EGY_SIGN_subset.csv \
    --split_dir ./script_output \
    --data_dir ./
```

- Finally, delete the data/ directory, and move the csvs to the current directory, then move the npy files to the SpaMo/preprocess/DS-Name directory.
