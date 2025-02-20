import json
import os
import sys

def convert_jsonl_to_json(input_file, output_file):
    data = []
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                data.append(item)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line in {input_file}: {line}\nError: {e}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Converted '{input_file}' to '{output_file}'.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_all.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Process each .jsonl file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.jsonl'):
            input_path = os.path.join(input_directory, filename)
            output_filename = os.path.splitext(filename)[0] + '.json'
            output_path = os.path.join(output_directory, output_filename)
            convert_jsonl_to_json(input_path, output_path)
