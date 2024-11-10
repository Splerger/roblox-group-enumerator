import json

def search_bio_in_json(file_path, *search_terms):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    matches = []
    for group_id, group_members in data.items():
        for role_name, users in group_members.items():
            for user in users:
                bio = user.get('bio', '').lower()
                if all(term.lower() in bio for term in search_terms):
                    matches.append(user)
    
    return matches

# Example usage
file_path = "all_members.json"
search_terms = ["sub", "submissive", "slave", "bottom", "pet", "dom", "dominant", "master", "mistress", "top", "alpha", "beta", "omega"]
matching_users = search_bio_in_json(file_path, *search_terms)
usernames = [user['username'] for user in matching_users]
print(usernames)

