import httpx
import json
from time import sleep
from tabulate import tabulate  # Importing for table format

# List of Roblox group IDs
group_ids = [10560880, 6553297, 9261176]  # Replace with actual group IDs

output_file = "all_members.json"

# Roblox authentication cookie
from config import roblox_cookie
# Headers with authentication
headers = {
    'Cookie': f'.ROBLOSECURITY={roblox_cookie}',
    'Content-Type': 'application/json'
}

# Function to send requests with retry and JSON validation
def send_request(url, params=None, retries=5, backoff_factor=2):
    delay = 1  # Initial delay time in seconds
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Requesting {url}")
            response = httpx.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()  # Raises HTTP errors if status is not 200

            # Return JSON data if successful
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
        
        # Wait with exponential backoff
        sleep(delay)
        delay *= backoff_factor
    
    # Raise an error if all attempts fail
    raise Exception(f"Failed to retrieve valid JSON from {url} after {retries} attempts.")


# Function to get all roles in a group
def get_group_roles(group_id):
    url = f'https://groups.roblox.com/v1/groups/{group_id}/roles'
    roles_data = send_request(url)
    return roles_data.get('roles', [])

# Function to get users by role
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

# Function to get additional user info (bio, username, display name)
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

# Function to get all members of multiple groups
def get_members_of_groups(group_ids):
    all_groups_members = {}
    for group_id in group_ids:
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
        with open(output_file, "a") as file:
            json.dump({group_id: group_members}, file, indent=4)
            file.write("\n")
    return all_groups_members

# Fetch members and print in table format
all_members = get_members_of_groups(group_ids)

print(f"Data exported successfully to {output_file}")
