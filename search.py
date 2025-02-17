import json
import os
import unicodedata
import re

with open('group_ids.txt') as f:
    group_ids = [line.strip() for line in f]

count = 0

# Function to normalize text for consistent emoji and diacritic handling
def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized_text if not unicodedata.combining(c))

links = set()

for group_id in group_ids:
    if os.path.exists(f'suspicious_users\\suspicious_users_{group_id}.json'):
        os.remove(f'suspicious_users\\suspicious_users_{group_id}.json')

def append_to_json_file(file_path, document):
    file_path = f'suspicious_users\\{file_path}'
    
    try:
        # Read existing data
        with open(file_path, 'r+', encoding='utf-8') as file:
            try:
                data = json.load(file)
                # Convert list to dictionary if necessary
                if isinstance(data, list):
                    data = {entry["id"]: entry for entry in data}
            except json.JSONDecodeError:
                data = {}  # Handle empty or corrupted JSON

        user_id = document["id"]

        # Ensure uniqueness by using user ID as key
        if user_id not in data:
            data[user_id] = document  # Store only one entry per user

        # Write updated data
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(list(data.values()), file, indent=4, ensure_ascii=False)
            file.write('\n')

    except FileNotFoundError:
        # If the file doesn't exist, create it and write the first entry
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([document], file, indent=4, ensure_ascii=False)
            file.write('\n')

# Function to load JSON data, search bios, and decode Morse code if present
def search_bio_in_json(file_path, *search_terms):
    global count
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
                isBanned = user.get("isBanned"),
                link = user.get("link", "")

                user_doc = {
                    "id": id,
                    "username": username,
                    "display_name": display_name,
                    "bio": bio,
                    "hasVerifiedBadge": hasVerifiedBadge,
                    "created": created,
                    "isBanned": isBanned,
                    "link": link,
                    "reason": ""
                }
                
                count += 1

                for term in normalized_terms:
                    if re.search(rf'\b{re.escape(term.lower())}\b', bio.lower()):
                        user_doc["reason"] = f"bio: {term}"
                        append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                        print(f"{count}. Found {term} in bio of {display_name} link: {link}")
                        links.add(link)

                    if re.search(rf'\b{re.escape(term.lower())}\b', username.lower()):
                        user_doc["reason"] = f"username: {term}"
                        append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                        print(f"{count}. Found {term} in username of {display_name} link: {link}")
                        links.add(link)

                    if re.search(rf'\b{re.escape(term.lower())}\b', display_name.lower()):
                        user_doc["reason"] = f"display name: {term}"
                        append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                        print(f"{count}. Found {term} in display name of {display_name} link: {link}")
                        links.add(link)

    except json.JSONDecodeError:
        print(f"Error: The file could not be decoded as JSON. {file_path}")
    except FileNotFoundError:
        print(f"Error: The file was not found. {file_path}")

# Function to search the friends directory
def search_friends_directory(group_id, *search_terms):
    friends_file_path = f'friends\\{group_id}_friends.json'
    search_bio_in_json(friends_file_path, *search_terms)

for group_id in group_ids:
    file_path = f'group\\{group_id}_all_members.json'
    search_bio_in_json(file_path, 'sub', 'dom', 'fem', 'studio', 'rp', ':3', 'socials', 'trade', 'app', 'blue app', 'blueapp', 'h%es', 'btm', 'top', 'switch', 'social', 'step bro', 'step sis', 'tos', 'snow', 'buns', 'bunny', 'lvl','bull', 'pound', 'master', 'rper', 'bals', 'breed', 'yng', 'gorilla', 'cakedup', '💿', '📀', '💽', 'dc', 'maid', 'disk', 'fem boi', 'https://www.roblox.com/users/', 'diaper', 'nappy', 'cons', 'femb', 'cake', 'hairpull', 'mommy', 'daddy', 'literate', 'thug', 'clap', 'tyrone', 'inch', 'pedo', 'mdni', '🐂', 'remboys', 'latex', 'endowed', 'plow', 'stood', 'morph', 'grape', 'legal', 'blacked', 'own', 'huge', 'stiff', 'stwudioo', 'cd', 'limitless', 'experienced', 'roleplay', '🔁', 'teen', 'erp', 'eboni', 'aced', 'slyt')
    search_friends_directory(group_id, 'sub', 'dom', 'fem', 'studio', 'rp', ':3', 'socials', 'trade', 'app', 'blue app', 'blueapp', 'h%es', 'btm', 'top', 'switch', 'social', 'step bro', 'step sis', 'tos', 'snow', 'buns', 'bunny', 'lvl','bull', 'pound', 'master', 'rper', 'bals', 'breed', 'yng', 'gorilla', 'cakedup', '💿', '📀', '💽', 'dc', 'maid', 'disk', 'fem boi', 'https://www.roblox.com/users/', 'diaper', 'nappy', 'cons', 'femb', 'cake', 'hairpull', 'mommy', 'daddy', 'literate', 'thug', 'clap', 'tyrone', 'inch', 'pedo', 'mdni', '🐂', 'remboys', 'latex', 'endowed', 'plow', 'stood', 'morph', 'grape', 'legal', 'blacked', 'own', 'huge', 'stiff', 'stwudioo', 'cd', 'limitless', 'experienced', 'roleplay', '🔁', 'teen', 'erp', 'eboni', 'aced', 'slyt')

with open('all_links.txt', 'w', encoding='utf-8') as f:
    for link in links:
        f.write(f"{link}\n")

