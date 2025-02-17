import httpx
import json
from time import sleep
from threading import Thread, Lock
import os
import shutil
from config import roblox_cookie

folder_name = "group"
output_file = "all_members.json"
friends_dir = "friends"

with open('group_ids.txt') as f:
    group_ids = [line.strip() for line in f]

headers = {
    'Cookie': f'.ROBLOSECURITY={roblox_cookie}',
    'Content-Type': 'application/json'
}

output_lock = Lock()

def send_request(url, params=None, retries=5, backoff_factor=2):
    delay = 1
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Requesting {url}")
            response = httpx.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except json.JSONDecodeError:
            print(f"Attempt {attempt}: Failed to decode JSON from {url}")
        except httpx.HTTPStatusError as e:
            print(f"Attempt {attempt}: HTTP error {e.response.status_code} on {url}")
            if e.response.status_code == 429:
                print("Rate limit exceeded. Waiting 30 seconds before retrying.")
                sleep(45)
        except httpx.RequestError as e:
            print(f"Attempt {attempt}: Network error on {url} - {e}")
        sleep(delay)
        delay *= backoff_factor
    raise Exception(f"Failed to retrieve valid JSON from {url} after {retries} attempts.")

def get_group_roles(group_id):
    url = f'https://groups.roblox.com/v1/groups/{group_id}/roles'
    roles_data = send_request(url)
    return roles_data.get('roles', [])

def get_users_by_role(group_id, role_id):
    users = []
    cursor = None
    while True:
        url = f'https://groups.roblox.com/v1/groups/{group_id}/roles/{role_id}/users'
        params = {'cursor': cursor} if cursor else {}
        data = send_request(url, params)
        users.extend(data.get('data', []))
        cursor = data.get('nextPageCursor')
        if not cursor:
            break
    return users

def get_user_info(user_id):
    url = f'https://users.roblox.com/v1/users/{user_id}'
    user_data = send_request(url)
    if user_data.get('isBanned', False):
        return None
    return {
        'id': user_data.get('id', ''),
        'username': user_data.get('name', ''),
        'displayName': user_data.get('displayName', ''),
        'bio': user_data.get('description', ''),
        'hasVerifiedBadge': user_data.get('hasVerifiedBadge', ''),
        'created': user_data.get('created', ''),
        'isBanned': user_data.get('isBanned', ''),
        'link': f"https://www.roblox.com/users/{user_data.get('id', '')}"
    }

def get_user_friends(user_id):
    url = f'https://friends.roblox.com/v1/users/{user_id}/friends'
    friends_data = send_request(url)
    return friends_data.get('data', [])

def process_group(group_id):
    print(f"Fetching members for group ID: {group_id}")
    group_members = {}
    roles = get_group_roles(group_id)
    for role in roles:
        role_id = role['id']
        role_name = role['name']
        print(f"  Fetching users for role: {role_name}")
        users_with_info = []
        users = get_users_by_role(group_id, role_id)
        for user in users:
            try:
                user_info = get_user_info(user['userId'])
                if user_info:
                    users_with_info.append(user_info)
                    friends = get_user_friends(user['userId'])
                    with open(os.path.join(friends_dir, f"{user['userId']}_friends.json"), "w", encoding="utf-8") as f:
                        json.dump(friends, f, indent=4)
            except Exception as e:
                print(f"Failed to fetch info for user {user['userId']}. Error: {e}")
        group_members[role_name] = users_with_info
    
    with output_lock:
        with open(f"{group_id}_{output_file}", "w", encoding="utf-8") as file:
            json.dump({f"Group_{group_id}": group_members}, file, indent=4, ensure_ascii=False)
            file.write("\n")

if not os.path.exists(friends_dir):
    os.makedirs(friends_dir)

num_threads = 5
for group_id in group_ids:
    if os.path.exists(os.path.join(folder_name, f"{group_id}_{output_file}")):
        with open('group_ids.txt', 'r') as file:
            lines = file.readlines()
        with open('group_ids.txt', 'w') as file:
            for line in lines:
                if line.strip() != group_id:
                    file.write(line)
        exit()
    else:
        print(f"Processing group {group_id}")
    threads = [Thread(target=process_group, args=(group_id,)) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

print(f"Data exported successfully")

if not os.path.exists(folder_name):
    os.makedirs(folder_name)
for file in os.listdir():
    if file.endswith("_all_members.json"):
        shutil.move(file, os.path.join(folder_name, file))

