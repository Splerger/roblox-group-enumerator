import json
import os

def clean_jsonl(input_file, output_file):
    valid_entries = []

    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            try:
                data = json.loads(line)

                # Extract first (and only) key dynamically
                if isinstance(data, dict) and len(data) == 1:
                    first_key = next(iter(data))
                    if isinstance(data[first_key], dict):  # Ensure value is a dictionary
                        valid_entries.append(data[first_key])

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Skipping malformed JSON line: {line[:100]}...")  # Show first 100 chars

    # Save cleaned data to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_entries, f, indent=4, ensure_ascii=False)

    print(f"Cleaned JSONL saved to: {output_file}")

# Process all .jsonl files in the "group" directory
input_directory = "group"
output_directory = "groups"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for filename in os.listdir(input_directory):
    if filename.endswith(".jsonl"):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename.replace(".jsonl", "_cleaned.json"))

        clean_jsonl(input_path, output_path)
