import json
import os
import unicodedata
import re

# Ensure output directory exists
suspicious_dir = "suspicious_users"
os.makedirs(suspicious_dir, exist_ok=True)

# Read group IDs
with open('group_ids.txt', encoding="utf-8") as f:
    group_ids = [line.strip() for line in f if line.strip()]

flagged_users = {}  # link => reason


def normalize_text(text):
    """Normalize text for consistent emoji and diacritic handling."""
    if not isinstance(text, str):
        return ""
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized if not unicodedata.combining(c))


def append_to_json_file(file_name, document):
    """Write user data to JSON, ensuring no duplicates."""
    file_path = os.path.join(suspicious_dir, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                data = {entry["id"]: entry for entry in data}
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[document["id"]] = document  # Overwrite or add

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(list(data.values()), f, indent=4, ensure_ascii=False)


def search_bio_in_json(file_path, group_id, *search_terms):
    """Search for suspicious terms in JSON format where roles map to user lists."""
    normalized_terms = [normalize_text(term) for term in search_terms]

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error reading {file_path}")
        return

    if not isinstance(data, dict):
        print(f"Invalid JSON structure in {file_path}")
        return

    total_users = sum(len(users) for users in data.values() if isinstance(users, list))
    print(f"Scanning {total_users} users in {file_path}")

    for role, users in data.items():
        if not isinstance(users, list):
            continue

        for user in users:
            if not isinstance(user, dict):
                continue

            user_id = str(user.get("id", ""))
            link = f"https://www.roblox.com/users/{user_id}/profile"

            if link in flagged_users:
                continue

            username = normalize_text(user.get("username", ""))
            display_name = normalize_text(user.get("displayName", ""))
            bio = normalize_text(user.get("bio", ""))
            created = user.get("created", "")
            has_verified_badge = user.get("hasVerifiedBadge", False)
            is_banned = user.get("isBanned", False)

            user_doc = {
                "id": user_id,
                "username": username,
                "display_name": display_name,
                "bio": bio,
                "hasVerifiedBadge": has_verified_badge,
                "created": created,
                "isBanned": is_banned,
                "link": link,
                "role": role,
                "reason": ""
            }

            full_text = f"{bio} {username} {display_name}".lower()

            for term in normalized_terms:
                pattern = rf'\b{re.escape(term.lower())}\b'
                if re.search(pattern, full_text):
                    user_doc["reason"] = f"matched: {term}"
                    append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                    flagged_users[link] = user_doc["reason"]
                    print(f"{link} - {term}")
                    break

    """Search for suspicious terms in bio, username, display name."""
    normalized_terms = [normalize_text(term) for term in search_terms]

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error reading {file_path}")
        return

    if not isinstance(data, list):
        print(f"Invalid JSON format in {file_path}")
        return

    print(f"Scanning {len(data)} entries in {file_path}")

    for entry in data:
        if not isinstance(entry, dict):
            continue

        for role, user in entry.items():
            if not isinstance(user, dict):
                continue

            user_id = user.get("id", "")
            link = user.get("link", "")
            if not link or link in flagged_users:
                continue

            username = normalize_text(user.get("username", ""))
            display_name = normalize_text(user.get("displayName", ""))
            bio = normalize_text(user.get("bio", ""))
            created = user.get("created", "")
            has_verified_badge = user.get("hasVerifiedBadge", False)
            is_banned = user.get("isBanned", False)

            user_doc = {
                "id": user_id,
                "username": username,
                "display_name": display_name,
                "bio": bio,
                "hasVerifiedBadge": has_verified_badge,
                "created": created,
                "isBanned": is_banned,
                "link": link,
                "role": role,
                "reason": ""
            }

            full_text = f"{bio} {username} {display_name}".lower()

            for term in normalized_terms:
                pattern = rf'\b{re.escape(term.lower())}\b'
                if re.search(pattern, full_text):
                    user_doc["reason"] = f"matched: {term}"
                    append_to_json_file(f"suspicious_users_{group_id}.json", user_doc)
                    flagged_users[link] = user_doc["reason"]
                    print(f"{link} - {term}")
                    break


# Clean old files
for group_id in group_ids:
    suspicious_file = os.path.join(suspicious_dir, f'suspicious_users_{group_id}.json')
    if os.path.exists(suspicious_file):
        os.remove(suspicious_file)
        print(f"Removed {suspicious_file}")

# Process each group
for group_id in group_ids:
    file_path = os.path.join("group", f"{group_id}_all_members.json")
    print(f"Processing group {group_id}...")

    search_bio_in_json(
        file_path,
        group_id,
        # Add suspicious terms here (include unicode directly or as u"\uXXXX\uXXXX")
        'sub', 'dom', 'fem', 'studio', 'rp', ':3', 'socials', 'trade', 'app',
        'blue app', 'blueapp', 'h%es', 'btm', 'top', 'switch', 'social', 'step bro',
        'step sis', 'tos', 'snow', 'buns', 'bunny', 'lvl', 'bull', 'pound',
        'master', 'rper', 'bals', 'breed', 'yng', 'gorilla', 'cakedup', '📏',
        '🗀', '🗅', 'dc', 'maid', 'disk', 'fem boi',
        'https://www.roblox.com/users/', 'diaper', 'nappy', 'cons', 'femb', 'cake',
        'hairpull', 'mommy', 'daddy', 'literate', 'thug', 'clap', 'tyrone', 'inch',
        'pedo', 'mdni', '🐂', 'remboys', 'latex', 'endowed', 'plow',
        'stood', 'morph', 'grape', 'legal', 'blacked', 'own', 'huge', 'stiff',
        'stwudioo', 'cd', 'limitless', 'experienced', 'roleplay', '🔀',
        'teen', 'erp', 'eboni', 'aced', 'slyt', 'bounce', ';3', '>3', 'paws',
        '🐾', 'anthros', 'cubz', '=3', '🔵', 'twnk', 'x app', 'wfsn', 'toy', 'bll', 'bubblebt'
    )

# Write final list
with open('all_links.txt', 'w', encoding='utf-8') as f:
    for link, reason in flagged_users.items():
        f.write(f"{link} - {reason}\n")

print("Done. Flagged links written to all_links.txt")
