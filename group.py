import httpx
import json
from time import sleep
from threading import Thread, Lock
import os
from config import roblox_cookie
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

# List of proxies (use your actual list here)
proxy_list = [
    "socks5://109.169.243.104:7788",
    "socks4://117.60.45.208:38801",
    "socks5://43.155.169.227:15673",
    "socks4://203.194.103.30:5678"
    # Add more proxies as needed...
]

def send_request(url, params=None, retries=5, backoff_factor=2):
    delay = 1
    proxy = random.choice(proxy_list)  # Select a random proxy from the list
    
    # Ensure the proxy URL is complete and uses the proper scheme
    proxy_url = proxy.strip()  # Ensure there are no extra spaces or newlines

    # Set up the proxy configuration for HTTP or SOCKS
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Requesting {url} using proxy {proxy_url}")
            with httpx.Client(proxies=proxies) as client:
                response = client.get(url, headers=headers, params=params, timeout=20)
                response.raise_for_status()
            return response.json()
        except (json.JSONDecodeError, httpx.HTTPStatusError, httpx.RequestError) as e:
            print(f"Attempt {attempt}: Error fetching {url} - {e}")
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                print("Rate limit exceeded. Waiting 60 seconds before retrying.")
                sleep(60)
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
    group_file = os.path.join(folder_name, f'{group_id}_all_members.jsonl')
    
    with open(group_file, 'w') as json_file:
        for role in roles:
            role_id = role['id']
            role_name = role['name']
            print(f"  Fetching users for role: {role_name}")
            for user in get_users_by_role(group_id, role_id):
                user_id = user['userId']
                user_record = users_collection.find_one({'id': user_id})
                if user_record and user_record['lastChecked'] > datetime.now() - timedelta(days=3):
                    user_info = user_record
                else:
                    user_info = get_user_info(user_id)
                    if user_info:
                        users_collection.update_one({'id': user_id}, {'$set': user_info}, upsert=True)
                if user_info:
                    json_file.write(json.dumps({role_name: user_info}, default=str) + '\n')

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

num_threads = 5
threads = [Thread(target=process_group, args=(group_id,)) for group_id in group_ids]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(f"Data exported successfully")
