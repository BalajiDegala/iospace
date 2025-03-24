import os
import requests
import json
from django.conf import settings
from django.core.cache import cache

#f0d57fdccd22401811d870e5e167235d5fe7b0be5d04dc24d15996662dbf7fb9
class AyonAPIClient:
    """
    Client for interacting with the AYON API.
    """
    def __init__(self):
        self.base_url = settings.AYON_API_URL
        self.api_key = settings.AYON_API_KEY
        self.username = settings.AYON_USERNAME
        self.password = settings.AYON_PASSWORD
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with the AYON API and get a token."""
        # Check if we have a token in cache
        cached_token = cache.get('ayon_api_token')
        if cached_token:
            self.token = cached_token
            return
            
        # If no cached token, authenticate
        auth_url = f"{self.base_url}/auth/login"
        payload = {
            "name": self.username,
            "password": self.password
        }
        
        print("Authenticating with payload:", payload)  # Debugging: Print the payload
        response = requests.post(auth_url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            self.token = response_data.get('token')
            print("Token obtained:", self.token)  # Debugging: Print the token
            # Cache the token for 1 hour (3600 seconds)
            cache.set('ayon_api_token', self.token, 3600)
        else:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the AYON API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"  # Ensure no double slashes
        headers = {
            "Authorization": f"Bearer {self.token}",  # Include the token
            "Content-Type": "application/json"
        }
        
        print("Making request to:", url)  # Debugging: Print the URL
        print("Headers:", headers)  # Debugging: Print the headers
        
        response = None
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [401, 403]:
            # Token might be expired, re-authenticate
            self._authenticate()
            headers["Authorization"] = f"Bearer {self.token}"
            
            # Retry the request
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
        
        return response

    # Projects
    def get_projects(self):
        """Get all projects."""
        response = self._make_request("GET", "projects")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get projects: {response.status_code} - {response.text}")
    
    def get_project(self, project_name):
        """Get a specific project by name."""
        response = self._make_request("GET", f"projects/{project_name}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get project {project_name}: {response.status_code} - {response.text}")
    
    def create_project(self, project_name, project_data):
        """Create a new project using a PUT request."""
        endpoint = f"projects/{project_name}"
        response = self._make_request("PUT", endpoint, data=project_data)
        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Failed to create project: {response.status_code} - {response.text}")

    def update_project(self, project_name, project_data):
        """Update an existing project."""
        response = self._make_request("PUT", f"projects/{project_name}", data=project_data)
        if response.status_code in [200, 204]:
            return response.json() if response.content else {"status": "success"}
        raise Exception(f"Failed to update project {project_name}: {response.status_code} - {response.text}")
    
    def delete_project(self, project_name):
        """Delete a project."""
        response = self._make_request("DELETE", f"projects/{project_name}")
        if response.status_code in [200, 204]:
            return {"status": "success"}
        raise Exception(f"Failed to delete project {project_name}: {response.status_code} - {response.text}")
    
    # Folders (including Sequences)
    def get_folders(self, project_name, folder_type=None):
        """Get all folders or sequences in a project."""
        endpoint = f"projects/{project_name}/folders"
        params = {"folder_type": folder_type} if folder_type else None
        
        response = self._make_request("GET", endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get folders: {response.status_code} - {response.text}")
    
    def get_folder(self, project_name, folder_id):
        """Get a specific folder by ID."""
        response = self._make_request("GET", f"projects/{project_name}/folders/{folder_id}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get folder {folder_id}: {response.status_code} - {response.text}")
    
    def create_folder(self, project_name, folder_data):
        """Create a new folder (sequence)."""
        response = self._make_request("POST", f"projects/{project_name}/folders", data=folder_data)
        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Failed to create folder: {response.status_code} - {response.text}")
    
    def update_folder(self, project_name, folder_id, folder_data):
        """Update an existing folder."""
        response = self._make_request("PUT", f"projects/{project_name}/folders/{folder_id}", data=folder_data)
        if response.status_code in [200, 204]:
            return response.json() if response.content else {"status": "success"}
        raise Exception(f"Failed to update folder {folder_id}: {response.status_code} - {response.text}")
    
    def delete_folder(self, project_name, folder_id):
        """Delete a folder."""
        response = self._make_request("DELETE", f"projects/{project_name}/folders/{folder_id}")
        if response.status_code in [200, 204]:
            return {"status": "success"}
        raise Exception(f"Failed to delete folder {folder_id}: {response.status_code} - {response.text}")
    
    # Products (Shots)
    def get_products(self, project_name, product_type="Shot"):
        """Get all products (shots) in a project."""
        params = {"product_type": product_type}
        response = self._make_request("GET", f"projects/{project_name}/products", params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get products: {response.status_code} - {response.text}")
    
    def get_product(self, project_name, product_id):
        """Get a specific product (shot) by ID."""
        response = self._make_request("GET", f"projects/{project_name}/products/{product_id}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get product {product_id}: {response.status_code} - {response.text}")
    
    def create_product(self, project_name, product_data):
        """Create a new product (shot)."""
        response = self._make_request("POST", f"projects/{project_name}/products", data=product_data)
        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Failed to create product: {response.status_code} - {response.text}")
    
    def update_product(self, project_name, product_id, product_data):
        """Update an existing product (shot)."""
        response = self._make_request("PUT", f"projects/{project_name}/products/{product_id}", data=product_data)
        if response.status_code in [200, 204]:
            return response.json() if response.content else {"status": "success"}
        raise Exception(f"Failed to update product {product_id}: {response.status_code} - {response.text}")
    
    def delete_product(self, project_name, product_id):
        """Delete a product (shot)."""
        response = self._make_request("DELETE", f"projects/{project_name}/products/{product_id}")
        if response.status_code in [200, 204]:
            return {"status": "success"}
        raise Exception(f"Failed to delete product {product_id}: {response.status_code} - {response.text}")
    
    # Tasks
    def get_tasks(self, project_name, product_id=None):
        """Get all tasks in a project, optionally filtered by product (shot)."""
        params = {"product_id": product_id} if product_id else None
        response = self._make_request("GET", f"projects/{project_name}/tasks", params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get tasks: {response.status_code} - {response.text}")
    
    def get_task(self, project_name, task_id):
        """Get a specific task by ID."""
        response = self._make_request("GET", f"projects/{project_name}/tasks/{task_id}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get task {task_id}: {response.status_code} - {response.text}")
    
    def create_task(self, project_name, task_data):
        """Create a new task."""
        response = self._make_request("POST", f"projects/{project_name}/tasks", data=task_data)
        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Failed to create task: {response.status_code} - {response.text}")
    
    def update_task(self, project_name, task_id, task_data):
        """Update an existing task."""
        response = self._make_request("PUT", f"projects/{project_name}/tasks/{task_id}", data=task_data)
        if response.status_code in [200, 204]:
            return response.json() if response.content else {"status": "success"}
        raise Exception(f"Failed to update task {task_id}: {response.status_code} - {response.text}")
    
    def delete_task(self, project_name, task_id):
        """Delete a task."""
        response = self._make_request("DELETE", f"projects/{project_name}/tasks/{task_id}")
        if response.status_code in [200, 204]:
            return {"status": "success"}
        raise Exception(f"Failed to delete task {task_id}: {response.status_code} - {response.text}")