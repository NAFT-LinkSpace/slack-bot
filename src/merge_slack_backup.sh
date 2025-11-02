# !/bin/bash

# Move to working directory
cd $(dirname "$0")
cd ../backup

# Load mmetl tool
export PATH=$PATH:$(pwd)/bin

# Create working directory
WORK_DIR="./temp"
mkdir -p $WORK_DIR
cd $WORK_DIR

# Run the mmetl tool to generate the mattermost bulk import JSONL file
mmetl transform slack -t $WORKSPACE_NAME -d bulk-export-attachments -f $0 -o mattermost_import.jsonl

# Create a zip archive in bulk format
mkdir data
mv bulk-export-attachments data
zip -r bulk_import.zip data mattermost_import.jsonl

# Copy the resulting file to the mattermost server, and upload it using mmctl tool
mmctl import upload ./bulk_import.zip

# List all import files to find out the filename that will be used to start the import process
mmctl import list available
IMPORT_FILE_NAME=$(mmctl import list available | grep bulk_import.zip | awk '{print $1}')

# Start the import process
mmctl import process $IMPORT_FILE_NAME

# Clean up
cd ..
rm -rf $WORK_DIR
