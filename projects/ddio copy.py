def __init__(self, project=None, seq=None, shot=None, user=None):
    self.project = project
    self.seq = seq
    self.shot = shot
    self.user = user
    self.base_url = "http://localhost:5000/"
    self.session = requests.Session()
    # Authenticate
    self.token = None
    self.login("balajid", "Gotham9!")  # Note: Consider using environment variables for credentials

def login(self, username, password):
    """Login to AYON using REST API"""
    endpoint = f"{self.base_url}api/auth/login"
    
    payload = {
        "name": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception on 4XX/5XX status
        
        data = response.json()
        if isinstance(data, dict) and "token" in data:
            self.token = data["token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return True
        else:
            print(f"Unexpected response format: {data}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Login error: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Login failed: {str(e)}")

def io_get_projects(self):
    """Get all projects using REST API"""
    endpoint = f"{self.base_url}api/projects"
    try:
        response = self.session.get(endpoint)
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the projects list from the response
        if isinstance(response_data, dict) and 'projects' in response_data:
            projects_list = response_data['projects']
        else:
            projects_list = response_data
            
        projects = []
        if isinstance(projects_list, list):
            for project in projects_list:
                if isinstance(project, dict) and 'name' in project:
                    projects.append(project["name"])
        
        return projects
    except requests.exceptions.RequestException as e:
        print(f"Error getting projects: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get projects: {str(e)}")

def io_get_users(self):
    """Get all users using REST API"""
    endpoint = f"{self.base_url}api/users"
    try:
        response = self.session.get(endpoint)
        response.raise_for_status()
        
        response_data = response.json()
        
        if isinstance(response_data, dict) and 'users' in response_data:
            users_list = response_data['users']
        else:
            users_list = response_data
            
        users = []
        if isinstance(users_list, list):
            for user in users_list:
                if isinstance(user, dict) and 'name' in user:
                    users.append(user["name"])
        
        return users
    except requests.exceptions.RequestException as e:
        print(f"Error getting users: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get users: {str(e)}")

def io_get_sequences(self, project_name=None):
    """Get sequences for a specific project using REST API"""
    if project_name:
        self.project = project_name
        
    if not self.project:
        raise ValueError("Project name must be specified")
    
    endpoint = f"{self.base_url}api/projects/{self.project}/folders"
    
    # To get only top-level sequences in the project
    params = {
        "folder_types": "Sequence",
        "parent_id": None  # This gets only top-level sequences
    }
    
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract sequences from response
        if isinstance(response_data, dict) and 'folders' in response_data:
            sequences_list = response_data['folders']
        else:
            sequences_list = response_data
        
        sequences = []
        if isinstance(sequences_list, list):
            for sequence in sequences_list:
                if isinstance(sequence, dict) and 'name' in sequence:
                    sequences.append(sequence["name"])
        
        return sequences
    except requests.exceptions.RequestException as e:
        print(f"Error getting sequences: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get sequences: {str(e)}")

def io_get_sequence_by_name(self, seq_name=None):
    """Get sequence details by name using REST API"""
    if seq_name:
        self.seq = seq_name
        
    if not self.seq or not self.project:
        raise ValueError("Both project and sequence name must be specified")
        
    endpoint = f"{self.base_url}api/projects/{self.project}/folders/names/{self.seq}"
    
    try:
        response = self.session.get(endpoint)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting sequence '{self.seq}': {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return None

def io_get_shots(self, sequence_name=None):
    """Get shots for a specific sequence using REST API"""
    if sequence_name:
        self.seq = sequence_name
        
    if not self.seq or not self.project:
        raise ValueError("Both project and sequence must be specified")
    
    # First, get the sequence by name to obtain its ID
    sequence_data = self.io_get_sequence_by_name()
    if not sequence_data or "id" not in sequence_data:
        raise ValueError(f"Sequence '{self.seq}' not found in project '{self.project}'")
        
    seq_id = sequence_data["id"]
    
    endpoint = f"{self.base_url}api/projects/{self.project}/folders"
    params = {
        "parent_id": seq_id,  # Use parent_id (singular) as per API docs
        "folder_types": "Shot"
    }
    
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract shots from response
        if isinstance(response_data, dict) and 'folders' in response_data:
            shots_list = response_data['folders']
        else:
            shots_list = response_data
        
        shots = []
        if isinstance(shots_list, list):
            for shot in shots_list:
                if isinstance(shot, dict) and 'name' in shot:
                    shots.append(shot["name"])
        
        return shots
    except requests.exceptions.RequestException as e:
        print(f"Error getting shots: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get shots: {str(e)}")

def io_get_shot_by_name(self, shot_name=None):
    """Get shot details by name using REST API"""
    if shot_name:
        self.shot = shot_name
        
    if not self.project or not self.seq or not self.shot:
        raise ValueError("Project, sequence, and shot must all be specified")
    
    # First get the sequence ID
    sequence_data = self.io_get_sequence_by_name()
    if not sequence_data or "id" not in sequence_data:
        raise ValueError(f"Sequence '{self.seq}' not found in project '{self.project}'")
        
    seq_id = sequence_data["id"]
    
    # Get shots for this sequence
    endpoint = f"{self.base_url}api/projects/{self.project}/folders"
    params = {
        "parent_id": seq_id,
        "folder_types": "Shot",
        "names": self.shot  # Filter by shot name
    }
    
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        if isinstance(response_data, dict) and 'folders' in response_data:
            shots = response_data['folders']
            if len(shots) > 0:
                return shots[0]  # Return the first matching shot
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting shot '{self.shot}': {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return None

def io_get_shot_id(self, shot_name=None):
    """Get shot ID using REST API"""
    if shot_name:
        self.shot = shot_name
        
    shot_data = self.io_get_shot_by_name()
    if shot_data and "id" in shot_data:
        return shot_data["id"]
    
    return None

def io_get_tasks(self, shot_name=None):
    """Get tasks for a specific shot using REST API"""
    if shot_name:
        self.shot = shot_name
    
    # If project, sequence, and shot are all provided, get tasks for the shot
    if self.project and self.seq and self.shot:
        shot_id = self.io_get_shot_id()
        if not shot_id:
            raise ValueError(f"Shot '{self.shot}' not found in sequence '{self.seq}'")
            
        endpoint = f"{self.base_url}api/projects/{self.project}/tasks"
        params = {
            "folder_id": shot_id  # Filter by folder ID (shot ID)
        }
    # If only project is provided, get all tasks for the project
    elif self.project:
        endpoint = f"{self.base_url}api/projects/{self.project}/tasks"
        params = {}
    else:
        raise ValueError("Project must be specified at minimum")
        
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract tasks from response
        if isinstance(response_data, dict) and 'tasks' in response_data:
            tasks_list = response_data['tasks']
        else:
            tasks_list = response_data
            
        tasks = []
        if isinstance(tasks_list, list):
            for task in tasks_list:
                tasks.append(task)
        
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Error getting tasks: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get tasks: {str(e)}")

def io_get_task(self, task_id):
    """Get specific task by ID using REST API"""
    if task_id is None:
        print("Please check for task ID")
        return None
            
    endpoint = f"{self.base_url}api/projects/{self.project}/tasks"
    params = {"task_ids": task_id}
    
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract tasks from response
        if isinstance(response_data, dict) and 'tasks' in response_data:
            tasks_list = response_data['tasks']
        else:
            tasks_list = response_data
            
        tasks = []
        if isinstance(tasks_list, list):
            for task in tasks_list:
                tasks.append(task)
        
        return tasks[0] if tasks else None
    except requests.exceptions.RequestException as e:
        print(f"Error getting task: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get task: {str(e)}")

def io_get_user_tasks(self, project=None, user=None):
    """Get tasks assigned to a specific user using REST API"""
    if project:
        self.project = project
    if user:
        self.user = user
        
    if not self.project or not self.user:
        raise ValueError("Both project and user must be specified")
        
    try:
        print(f"Fetching tasks for user: {self.user}")
        endpoint = f"{self.base_url}api/projects/{self.project}/tasks"
        params = {"assignees": self.user}
        
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract tasks from response
        if isinstance(response_data, dict) and 'tasks' in response_data:
            tasks_list = response_data['tasks']
        else:
            tasks_list = response_data
        
        tasks = []
        if isinstance(tasks_list, list):
            for task in tasks_list:
                tasks.append(task)
        
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {e}")
        return []

def io_create_project(self, project_name=None):
    """Create a new project using REST API"""
    if project_name:
        self.project = project_name
        
    if not self.project:
        raise ValueError("Project name must be specified")
        
    try:
        proj_code = self.project.upper()
        endpoint = f"{self.base_url}api/projects"
        
        payload = {
            "name": self.project,
            "code": proj_code,
            "preset_name": "DDHB"
        }
        
        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()
        
        return f"{self.project} Project Created successfully"
    except requests.exceptions.RequestException as e:
        print(f"Error creating project: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return e

def io_create_sequence(self, project_name=None, sequence_name=None):
    """Create a new sequence using REST API"""
    if project_name:
        self.project = project_name
    if sequence_name:
        self.seq = sequence_name
        
    if not self.project or not self.seq:
        raise ValueError("Both project and sequence name must be specified")
        
    try:
        endpoint = f"{self.base_url}api/projects/{self.project}/folders"
        
        payload = {
            "name": self.seq,
            "folder_type": "Sequence",
            # Set parent_id to null for top-level sequence
            "parent_id": None
        }
        
        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()
        
        return f"{self.seq} Sequence Created successfully in project {self.project}"
    except requests.exceptions.RequestException as e:
        print(f"Error creating sequence: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return e

def io_create_shot(self, project_name=None, sequence_name=None, shot_name=None):
    """Create a new shot using REST API"""
    if project_name:
        self.project = project_name
    if sequence_name:
        self.seq = sequence_name
    if shot_name:
        self.shot = shot_name
        
    if not self.project or not self.seq or not self.shot:
        raise ValueError("Project, sequence, and shot name must all be specified")
        
    try:
        # First get the sequence to get its ID
        sequence_data = self.io_get_sequence_by_name()
        if not sequence_data or "id" not in sequence_data:
            raise ValueError(f"Sequence '{self.seq}' not found in project '{self.project}'")
            
        seq_id = sequence_data["id"]
        
        endpoint = f"{self.base_url}api/projects/{self.project}/folders"
        
        payload = {
            "name": self.shot,
            "parent_id": seq_id,
            "folder_type": "Shot"
        }
        
        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()
        
        return f"{self.shot} Shot Created successfully in sequence {self.seq} of project {self.project}"
    except requests.exceptions.RequestException as e:
        print(f"Error creating shot: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return f"Failed to create shot: {e}"

def io_create_task(self, shot_name=None, task_name=None, task_type=None, assignees=None):
    """Create a new task for a shot using REST API"""
    if shot_name:
        self.shot = shot_name
        
    if not self.project or not self.seq or not self.shot or not task_name or not task_type:
        raise ValueError("Project, sequence, shot, task name, and task type must all be specified")
        
    try:
        # Get shot ID
        shot_id = self.io_get_shot_id()
        if not shot_id:
            raise ValueError(f"Shot '{self.shot}' not found in sequence '{self.seq}'")
            
        endpoint = f"{self.base_url}api/projects/{self.project}/tasks"
        
        payload = {
            "name": task_name,
            "task_type": task_type,
            "folder_id": shot_id
        }
        
        if assignees:
            payload["assignees"] = assignees if isinstance(assignees, list) else [assignees]
        
        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()
        
        return f"Task '{task_name}' created successfully for shot {self.shot}"
    except requests.exceptions.RequestException as e:
        print(f"Error creating task: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return f"Failed to create task: {e}"

def io_get_events(self, limit=100):
    """Get events using REST API"""
    endpoint = f"{self.base_url}api/events"
    params = {"limit": limit}
    
    try:
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract events from response
        if isinstance(response_data, dict) and 'events' in response_data:
            events_list = response_data['events']
        else:
            events_list = response_data
        
        events = []
        if isinstance(events_list, list):
            for event in events_list:
                events.append(event)
        
        return events
    except requests.exceptions.RequestException as e:
        print(f"Error getting events: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to get events: {str(e)}")