import json
import os
import unicodedata
import re

# Ensure necessary directories exist
suspicious_dir = "suspicious_users"
if not os.path.exists(suspicious_dir):
    os.makedirs(suspicious_dir)

# Read group IDs
with open('group_ids.txt', encoding="utf-8") as f:
    group_ids = [line.strip() for line in f if line.strip()]

count = 0

def normalize_text(text):
    """Normalize text for consistent emoji and diacritic handling."""
    normalized_text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized_text if not unicodedata.combining(c))

flagged_users = {}  # Dictionary to store links with their reasons (ensures no duplicates)

# Remove old suspicious users files if they exist
for group_id in group_ids:
    suspicious_file = os.path.join(suspicious_dir, f'suspicious_users_{group_id}.json')
    if os.path.exists(suspicious_file):
        os.remove(suspicious_file)
        print(f"Removed existing file {suspicious_file}")

def append_to_json_file(file_name, document):
    """Write user data to the correct suspicious users JSON file."""
    file_path = os.path.join(suspicious_dir, file_name)

    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if isinstance(data, list):
                    data = {entry["id"]: entry for entry in data}  # Ensure uniqueness
            except json.JSONDecodeError:
                data = {}
    except FileNotFoundError:
        data = {}

    user_id = document["id"]
    data[user_id] = document  # Store only one entry per user

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(list(data.values()), file, indent=4, ensure_ascii=False)
        file.write('\n')
    #print(f"Appended user {user_id} to {file_path}")

def search_bio_in_json(file_path, group_id, *search_terms):
    """Search JSON file for suspicious keywords and save flagged users."""
    global count
    normalized_terms = [normalize_text(term) for term in search_terms]

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from: {file_path}")
        return

    if not isinstance(data, list):  # Ensure data is a list of role dictionaries
        print(f"Error: Expected a list of roles in {file_path}")
        return

    print(f"Scanning {len(data)} user entries in {file_path}")

    for entry in data:
        if not isinstance(entry, dict):
            continue

        for role, user in entry.items():  # Extract user from role-based dictionary
            if not isinstance(user, dict):
                continue

            # Extract user information safely
            user_id = user.get("id", "")
            username = normalize_text(user.get("username", ""))
            display_name = normalize_text(user.get("displayName", ""))
            bio = normalize_text(user.get("bio", ""))
            has_verified_badge = user.get("hasVerifiedBadge", False)
            created = user.get("created", "")
            is_banned = user.get("isBanned", False)
            link = user.get("link", "")

            # If user is already flagged, skip processing
            if link in flagged_users:
                continue  

            user_doc = {
                "id": user_id,
                "username": username,
                "display_name": display_name,
                "bio": bio,
                "hasVerifiedBadge": has_verified_badge,
                "created": created,
                "isBanned": is_banned,
                "link": link,
                "role": role,  # Include the role for reference
                "reason": ""
            }

            for term in normalized_terms:
                term_pattern = rf'\b{re.escape(term.lower())}\b'

                if re.search(term_pattern, bio.lower()):
                    user_doc["reason"] = f"bio: {term}"
                elif re.search(term_pattern, username.lower()):
                    user_doc["reason"] = f"username: {term}"
                elif re.search(term_pattern, display_name.lower()):
                    user_doc["reason"] = f"display name: {term}"
                else:
                    continue  # If no match, skip appending

                append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                print(f"{link} - {term}")

                # Save link with reason (ensures uniqueness)
                flagged_users[link] = user_doc["reason"]
                break  # Stop checking after the first match

# Process each group
for group_id in group_ids:
    file_path = os.path.join("groups", f"{group_id}_all_members.json")
    print(f"Processing group {group_id} from {file_path}")

    search_bio_in_json(
        file_path,
        group_id,
        'sub', 'dom', 'fem', 'studio', 'rp', ':3', 'socials', 'trade', 'app',
        'blue app', 'blueapp', 'h%es', 'btm', 'top', 'switch', 'social', 'step bro',
        'step sis', 'tos', 'snow', 'buns', 'bunny', 'lvl', 'bull', 'pound',
        'master', 'rper', 'bals', 'breed', 'yng', 'gorilla', 'cakedup', '\ud83d\uddcf',
        '\ud83d\uddc0', '\ud83d\uddc5', 'dc', 'maid', 'disk', 'fem boi',
        'https://www.roblox.com/users/', 'diaper', 'nappy', 'cons', 'femb', 'cake',
        'hairpull', 'mommy', 'daddy', 'literate', 'thug', 'clap', 'tyrone', 'inch',
        'pedo', 'mdni', '\ud83d\udc02', 'remboys', 'latex', 'endowed', 'plow',
        'stood', 'morph', 'grape', 'legal', 'blacked', 'own', 'huge', 'stiff',
        'stwudioo', 'cd', 'limitless', 'experienced', 'roleplay', '\ud83d\udd00',
        'teen', 'erp', 'eboni', 'aced', 'slyt', 'bounce', ';3', '>3', 'paws',
        '\ud83d\udc3e', 'anthros', 'cubz', '=3'
    )

# Save all flagged links with reasons (without duplicates)
with open('all_links.txt', 'w', encoding='utf-8') as f:
    for link, reason in flagged_users.items():
        f.write(f"{link} - {reason}\n")
        
print("Finished writing all_links.txt with unique flagged links.")
