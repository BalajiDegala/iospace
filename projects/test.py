import requests

def fetch_data_from_ayon():
    url = "http://localhost:30008/explorer"  # Replace with Ayon's GraphQL endpoint
    headers = {
        "Authorization": "Bearer your_access_token",  # Add your token if required
        "Content-Type": "application/json"
    }
    query = """
    {
      projects {
        name
        description
        status
      }
    }
    """
    response = requests.post(url, json={"query": query}, headers=headers)

    if response.status_code == 200:
        return response.json().get("data", {})
    else:
        raise Exception(f"Query failed: {response.status_code}, {response.text}")
