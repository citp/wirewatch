#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_file.csv>"
    exit 1
fi

input_file="$1"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

# Read each line of the CSV file
while IFS=, read -r column1 _; do
    # Run the program with the value from the first column
    apkeep -a "$column1" -d google-play -i ./apkeep.ini -o split_apk=true apps/
done < "$input_file"
