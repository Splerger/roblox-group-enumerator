import glob
import json

numbers = []
for filename in glob.glob("group\\*.json"):
    with open(filename, encoding='utf-8') as f:
        data = json.load(f)
        number = filename.split("_")[0].split("\\")[-1]
        numbers.append(number)

print(numbers)

