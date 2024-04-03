#!/bin/bash

# Hardcoded folder path
folder_path="/work/pi_yuanchang_xie_uml_edu/zubin/CODE/yolov8.0.137/runs/TRACK-Danvers-MTLD/Danvers-NN-VehSeg-Workzone"

# Check if the provided path is a directory
if [ ! -d "$folder_path" ]; then
    echo "Error: The provided path is not a valid directory."
    exit 1
fi

# List all folders in the provided directory
folders=$(find "$folder_path" -maxdepth 1 -type d)

# Loop through each folder and run the Python script
for folder in $folders; do
    if [ "$folder" != "$folder_path" ]; then
        echo "Running Python script for folder: $folder"
        python process_results.py "$folder"
    fi
done
