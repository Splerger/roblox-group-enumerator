import json
import os
import unicodedata
import re
from config import group_ids

# Function to normalize text for consistent emoji and diacritic handling
def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized_text if not unicodedata.combining(c))

def append_to_json_file(file_path, document):
    file_path = f'suspicious_users\\{file_path}'
    try:
        # Read the existing data
        with open(file_path, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            
            # Append the new document
            data.append(document)
            
            # Move the file pointer to the beginning and truncate the file
            file.seek(0)
            file.truncate()
            
            # Write the updated data back to the file
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write('\n')
    except FileNotFoundError:
        # If the file doesn't exist, create it and write the document as the first entry in a list
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([document], file, indent=4, ensure_ascii=False)
            file.write('\n')
    except json.JSONDecodeError:
        # If the file is empty or not a valid JSON, write the document as the first entry in a list
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([document], file, indent=4, ensure_ascii=False)
            file.write('\n')


# Function to load JSON data, search bios, and decode Morse code if present
def search_bio_in_json(file_path, *search_terms):
    normalized_terms = [normalize_text(term) for term in search_terms]

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        
        for role, users in data.get(f"Group_{group_id}", {}).items():
            for user in users:
                if user is None:
                    continue
                id = user.get("id", "")
                username = normalize_text(user.get("username", ""))
                display_name = normalize_text(user.get("displayName", ""))
                bio = normalize_text(user.get("bio", ""))
                hasVerifiedBadge = user.get("hasVerifiedBadge", "")
                created = user.get("created", "")
                isBanned = user.get("isBanned", "")

                user_doc = {
                    "id": id,
                    "username": username,
                    "display_name": display_name,
                    "bio": bio,
                    "hasVerifiedBadge": hasVerifiedBadge,
                    "created": created,
                    "isBanned": isBanned,
                    "reason": ""
                }

                # Search for terms in plain bio
                if any(re.search(rf'\b{re.escape(term.lower())}\b', bio.lower()) for term in normalized_terms):
                    print(f"Username: {username}")
                    print(f"Display Name: {display_name}")
                    print(f"Bio: {bio}")
                    print(f"ID: {id}")
                    print(f"Created: {created}")
                    print('reason: bio')
                    print("-" * 40)
                    
                    user_doc["reason"] = "bio"
                    append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                    
                if any(re.search(rf'\b{re.escape(term.lower())}\b', username.lower()) for term in normalized_terms):
                    print(f"Username: {username}")
                    print(f"Display Name: {display_name}")
                    print(f"Bio: {bio}")
                    print(f"ID: {id}")
                    print(f"Created: {created}")
                    print('reason: username')
                    print("-" * 40)
                    
                    user_doc["reason"] = "username"
                    append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                    
                if any(re.search(rf'\b{re.escape(term.lower())}\b', display_name.lower()) for term in normalized_terms):
                    print(f"Username: {username}")
                    print(f"Display Name: {display_name}")
                    print(f"Bio: {bio}")
                    print(f"ID: {id}")
                    print(f"Created: {created}")
                    print('reason: display name')
                    print("-" * 40)
                    
                    user_doc["reason"] = "display name"
                    append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)

    except json.JSONDecodeError:
        print("Error: The file could not be decoded as JSON.")
    except FileNotFoundError:
        print(f"Error: The specified file was not found. {file_path}")
        

for group_id in group_ids:
    file_path = f'D:\\code\\python\\roblox group enumerator\\group\\{group_id}_all_members.json'
    search_bio_in_json(file_path, 'sub', 'dom', 'fem', 'studio', 'rp', ':3', 'socials', 'trade', 'app', 'blue app', 'h%es', 'btm', 'top', 'switch', 'social', 'step bro', 'step sis', 'tos', 'snow', 'buns', 'bunny', 'lvl','bull', 'pound', 'master', 'rper', 'bals', 'breed', 'yng', 'gorilla', 'cakedup', '💿', '📀', '💽', 'dc', 'maid', 'disk', 'fem boi', 'https://www.roblox.com/users/', 'diaper', 'nappy', 'cons')

