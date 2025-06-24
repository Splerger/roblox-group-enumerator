import httpx
import json
from time import sleep
from threading import Thread, Lock
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

folder_name = "group"

client = MongoClient('mongodb://192.168.0.16:27017/')
db = client['roblox']
users_collection = db['users']
groups_collection = db['groups']

with open('group_ids.txt') as f:
    group_ids = [line.strip() for line in f]

headers = {
    'Content-Type': 'application/json'
}

output_lock = Lock()


def send_request(url, params=None, retries=5, backoff_factor=2):
    delay = 2
    
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Requesting {url}")
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params, timeout=20)
                response.raise_for_status()
            return response.json()
        except (json.JSONDecodeError, httpx.HTTPStatusError, httpx.RequestError) as e:
            print(f"Attempt {attempt}: Error fetching {url} - {e}")
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                ratelimit_reset = int(response.headers.get('x-ratelimit-reset', 0)) - int(response.headers.get('x-ratelimit-remaining', 0))
                print(f"Rate limit exceeded. Waiting {ratelimit_reset} seconds before retrying.")
                if ratelimit_reset > 0:
                    sleep(ratelimit_reset)
                else:
                    sleep(60)
                continue
        sleep(delay)
        delay *= backoff_factor
    raise Exception(f"Failed to retrieve valid JSON from {url} after {retries} attempts.")

def get_group_roles(group_id):
    url = f'https://groups.roblox.com/v1/groups/{group_id}/roles'
    roles_data = send_request(url)
    return roles_data.get('roles', [])

def get_users_by_role(group_id, role_id):
    cursor = None
    while True:
        url = f'https://groups.roblox.com/v1/groups/{group_id}/roles/{role_id}/users'
        params = {'cursor': cursor} if cursor else {}
        data = send_request(url, params)
        for user in data.get('data', []):
            yield user
        cursor = data.get('nextPageCursor')
        if not cursor:
            break

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
        'link': f"https://www.roblox.com/users/{user_data.get('id', '')}",
        'lastChecked': datetime.now()
    }

def process_group(group_id):
    print(f"Fetching members for group ID: {group_id}")
    roles = get_group_roles(group_id)
    group_file = os.path.join(folder_name, f'{group_id}_all_members.json')
    
    data = {}
    for role in roles:
        role_id = role['id']
        role_name = role['name']
        print(f"  Fetching users for role: {role_name}")
        data[role_name] = []
        for user in get_users_by_role(group_id, role_id):
            user_id = user['userId']
            user_record = users_collection.find_one({'id': user_id})
            if user_record and user_record['lastChecked'] > datetime.now() - timedelta(days=3):
                user_info = user_record
            else:
                user_info = get_user_info(user_id)
                if user_info:
                    users_collection.update_one(
                        {'id': user_id},
                        {
                            '$set': {
                                'bio': user_info['bio'],
                                'username': user_info['username'],
                                'displayName': user_info['displayName'],
                                'hasVerifiedBadge': user_info['hasVerifiedBadge'],
                                'isBanned': user_info['isBanned'],
                                'lastChecked': datetime.now()
                            }
                        },
                        upsert=True
                    )
            if user_info:
                data[role_name].append(user_info)

    with open(group_file, 'w') as json_file:
        json.dump(data, json_file, default=str, indent=4)

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

num_threads = 5
threads = [Thread(target=process_group, args=(group_id,)) for group_id in group_ids]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(f"Data exported successfully")

