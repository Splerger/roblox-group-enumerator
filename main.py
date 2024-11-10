import httpx
import json
from time import sleep
from tabulate import tabulate
from threading import Thread, Lock

group_ids = [10560880, 6553297, 9261176]
output_file = "all_members.json"
from config import roblox_cookie

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
                sleep(30)
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
        'username': user_data.get('name', ''),
        'displayName': user_data.get('displayName', ''),
        'bio': user_data.get('description', '')
    }

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
                users_with_info.append(user_info)
            except Exception as e:
                print(f"Failed to fetch info for user {user['userId']}. Error: {e}")
        group_members[role_name] = users_with_info
    with output_lock:
        with open(output_file, "a") as file:
            json.dump({group_id: group_members}, file, indent=4)
            file.write("\n")

threads = [Thread(target=process_group, args=(group_id,)) for group_id in group_ids]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(f"Data exported successfully to {output_file}")