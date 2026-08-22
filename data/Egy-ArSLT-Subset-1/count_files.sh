#!/bin/bash

# Use the first argument as the target directory, or default to current directory (.)
TARGET_DIR="${1:-.}"

# Check if the provided argument is a valid directory
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Find all regular files recursively and count the lines
FILE_COUNT=$(find "$TARGET_DIR" -type f | wc -l)

echo "Total files in '$TARGET_DIR': $FILE_COUNT"