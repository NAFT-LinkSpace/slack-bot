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
mmetl transform slack -t test -f $1 -o mattermost_import.jsonl

# Modify the JSONL file
jq -c 'if .type == "user" then
    .user.teams |= map(
      if (.channels | length) == 0 then
        .channels = [{"name":"off-topic","roles":"channel_user"}]
      else
        .
      end
    )
  else
    .
  end' mattermost_import.jsonl | sponge mattermost_import.jsonl

# Create a zip archive in bulk format
zip -r bulk_import.zip data mattermost_import.jsonl

# Start the import process
mmctl import process --bypass-upload ./bulk_import.zip --local


# # Clean up
# cd ..
# rm -rf $WORK_DIR
