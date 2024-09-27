#!/bin/bash

# Default values
output_dir="./sources/"
wait_time=1

# Function to display usage
usage() {
    echo "Usage: $0 --url <url> [--output-dir <output_dir>] [--wait <wait_time>]"
    exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --url)
            url="$2"
            shift
            ;;
        --output-dir)
            output_dir="$2"
            shift
            ;;
        --wait)
            wait_time="$2"
            shift
            ;;
        *)
            echo "Unknown parameter passed: $1"
            usage
            ;;
    esac
    shift
done

# Check if --url is provided
if [ -z "$url" ]; then
    echo "Error: --url is required."
    usage
fi

wget -r --continue --no-parent --reject '*.js,*.css,*.ico,*.txt,*.gif,*.jpg,*.jpeg,*.png,*.mp3,*.pdf,*.tgz,*.flv,*.avi,*.mpeg,*.iso' --follow-tags=a --wait=$wait_time --random-wait --directory-prefix=$output_dir $url