from django.shortcuts import render
from .ddio import dd_io
from django.http import HttpResponse
from projects.iotc import time_data_collection
import django_filters
import django_tables2 as tables
from django.core.paginator import Paginator
from django_tables2 import RequestConfig
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
import os
from pprint import pprint
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
import logging
import requests
# Set up logging
logger = logging.getLogger(__name__)

@login_required
def home(request):
    return render(request, 'home.html', )

def about(request):
    return render(request, 'about.html')

def show_projects(request):
    val = dd_io()
    projects = val.io_get_projects()
    context = {"projects": projects}
    return render(request, 'projects.html', context)
def add_project(request):
    if request.method == "POST":
        project_name = request.POST.get("project_name")
        print("project_name",project_name)
        if project_name:
            val = dd_io(project=project_name)
            result = val.io_create_project()
            messages.success(request, result)
        else:
            messages.error(request, "Project name cannot be empty.")
    return redirect('proj')
def show_sequences(request, project_name):
    val = dd_io(project_name)
    sequences = val.io_get_sequences()
    context = {"project_name": project_name, "sequences": sequences}
    return render(request, 'sequences.html', context)
def add_sequence(request, project_name):
    if request.method == "POST":
        sequence_name = request.POST.get("sequence_name")
        if sequence_name:
            val = dd_io(project=project_name, seq=sequence_name)
            result = val.io_create_sequence()
            print("result",result)
            messages.success(request, result)
        else:
            messages.error(request, "Sequence name cannot be empty.")
    return redirect('seq', project_name=project_name)
def show_shots(request, project_name, sequence_name):
    val = dd_io(project_name, sequence_name)
    shots = val.io_get_shots()
    context = {"project_name": project_name, "sequence_name": sequence_name, "shots": shots}
    return render(request, 'shots.html', context)
def add_shot(request, project_name, sequence_name):
    if request.method == "POST":
        shot_name = request.POST.get("shot_name")
        if shot_name:
            val = dd_io(project=project_name, seq=sequence_name, shot=shot_name)
            result = val.io_create_shot()
            print("result", result)
            messages.success(request, result)
        else:
            messages.error(request, "Shot name cannot be empty.")
    return redirect('shot', project_name=project_name, sequence_name=sequence_name)

def show_tasks(request, project_name, sequence_name, shot_name):
    val = dd_io(project_name, sequence_name, shot_name)
    tasks = val.io_get_shot_tasks()
    context = {"shot_name": shot_name ,"project_name": project_name, "sequence_name": sequence_name, "tasks": tasks}
    return render(request, 'tasks.html', context)

def add_task(request, project_name, sequence_name, shot_name):
    if request.method == "POST":
        task_name = request.POST.get("task_name")
        task_type = request.POST.get("task_type")
        print("task_name",task_type)
        if task_name:
            val = dd_io(project=project_name, seq=sequence_name, shot=shot_name, task = task_name)
            result = val.io_create_task(task_type = task_type)
            print("result", result)
            messages.success(request, result)
        else:
            messages.error(request, "Shot name cannot be empty.")
    return redirect('task', project_name=project_name, sequence_name=sequence_name, shot_name = shot_name)


def get_headers():
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}


def tasks_page(request):
    ddio_instance = dd_io()
    projects = ddio_instance.io_get_projects()
    selected_project = request.POST.get("project_name")
    tasks = None
    dropdown_data = {}

    if selected_project:
        # Fetch tasks for the selected project
        ddio_instance = dd_io(project=selected_project)
        tasks = ddio_instance.io_get_tasks()

        # Fetch project details
        response = requests.get(f"http://localhost:30008/api/projects/{selected_project}",headers=get_headers())
        if response.status_code == 200:
            project_details = response.json()

            dropdown_data = {
                "statuses": [item["name"] for item in project_details.get("statuses", [])],
                "taskTypes": [item["name"] for item in project_details.get("taskTypes", [])],
                "tags": [item["name"] for item in project_details.get("tags", [])],
            }

    context = {
        "projects": projects,
        "selected_project": selected_project,
        "tasks": tasks,
        "dropdown_data": dropdown_data,  
    }

    return render(request, "foldertasks.html", context)


@csrf_exempt
def update_task(request, project_name, task_id):
    if request.method == "PATCH":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            print("data",data)
            # Log received data for debugging
            print(f"Received update for task {task_id} in project {project_name}")
            print("Received data:", json.dumps(data, indent=2))
            start_date = datetime.strptime(data.get('startDate'), "%Y-%m-%d") 
            iso_start_date = start_date.strftime("%Y-%m-%dT00:00:00+00:00")
            end_date = datetime.strptime(data.get("endDate"), "%Y-%m-%d")
            iso_end_date = end_date.strftime("%Y-%m-%dT00:00:00+00:00")
            # Prepare payload for the server
            payload = {
                'assignees': data.get("assignees"),
                "name": data.get("name"),
                "taskType": data.get("taskType"),
                "status": data.get("status"),
                "priority": data.get("priority"),
                "attrib": {
                    "startDate": iso_start_date,
                    "endDate": iso_end_date,
                },
            }
            print('payload',payload)

            print("Payload to send:", json.dumps(payload, indent=2))
            url = f"http://localhost:30008/api/projects/{project_name}/tasks/{task_id}"
            response = requests.patch(url, json=payload, headers=get_headers())

            print(f"Server response status: {response.status_code}")
            print(f"Server response text: {response.text}")

            if response.status_code == 204:
                return JsonResponse({"success": True, "message": "Task updated successfully!"})
            else:
                return JsonResponse({
                    "success": False, 
                    "message": response.text,
                    "status_code": response.status_code
                }, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    




def folders_page(request):
    ddio_instance = dd_io()
    projects = ddio_instance.io_get_projects()  
    folders = None
    selected_project = None

    if request.method == "POST":
        selected_project = request.POST.get("project_name")
        ddio_instance = dd_io(project=selected_project)
        folders = ddio_instance.io_get_folders() 

    context = {
        "projects": projects,
        "selected_project": selected_project,
        "folders": folders,
    }
    return render(request, "folders.html", context)



@csrf_exempt
def update_folder(request, project_name, folder_id):
    """
    Update a specific folder using the PATCH method.
    """
    if request.method != "PATCH":
        return JsonResponse({"error": "Invalid request method. Use PATCH."}, status=405)

    try:
        print(f"Received update for folder: {folder_id} in project: {project_name}")
        updates = json.loads(request.body)
        print(f"Update data: {updates}")

        url = f"http://localhost:30008/api/projects/{project_name}/folders/{folder_id}"
        
        response = requests.patch(url, json=updates, headers=get_headers())

        print(f"External API response status: {response.status_code}")
        print(f"External API response text: {response.text}")

        if response.status_code == 204:
            return JsonResponse({"message": f"Folder '{folder_id}' updated successfully."}, status=200)

        response.raise_for_status()
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    except json.JSONDecodeError:
        print("Invalid JSON body received from the request.")
        return JsonResponse({"error": "Invalid JSON body received from the request."}, status=400)




def show_users(request):
    val = dd_io()
    users = val.io_get_users()
    context = {"users": users }
    return render(request, 'users.html', context)
def show_my_tasks(request):
    val = dd_io(user="balajid")
    projects = val.io_get_projects()
    tasks = {}
    for i in projects:
        k = val.io_get_user_tasks(i)
        tasks[i] = k
    # Flatten the tasks dictionary
    user_tasks = {}
    for project, tasks_list in tasks.items():
        user_tasks[project] = [
            {
                'id': task['id'],
                'name': task['name'],
                'start_date': task['attrib'].get('startDate', 'N/A'),
                'end_date': task['attrib'].get('endDate', 'N/A'),
                'status': task['status'],
                "assignees": task['assignees'],
                "frameStart":  task['attrib'].get('frameStart', 'N/A'),
                "frameEnd":  task['attrib'].get('frameEnd', 'N/A'),
            }
            for task in tasks_list
        ]
    return render(request, 'my_tasks.html', {'tasks_by_show': user_tasks})
    
    
def task_detail(request, task_id):
    val = dd_io()  

    task = val.io_get_task(task_id=task_id)
    print("task",task)
    if not task:
        return render(request, 'task_detail.html', {'error': 'Task not found'})
    context = {"task": task[0]}  
    print("context",context)
    return render(request, 'task_detail.html', context)




# @csrf_exempt
# def update_task(request, project_name , task_id):
#     """
#     Update a specific project using the PATCH method.
#     """
#     if request.method != "PATCH":
#         return JsonResponse({"error": "Invalid request method. Use PATCH."}, status=405)

#     try:
#         print(f"Received update for project: {project_name}")
#         updates = json.loads(request.body)
#         print(f"Update data: {updates}")

#         # Construct API URL
#         url = f"http://localhost:30008/api/projects/{project_name}/tasks/{task_id}"

#         # Perform PATCH request
#         response = requests.patch(url, json=updates, headers=get_headers())
#         print(f"External API response status: {response.status_code}")
#         print(f"External API response text: {response.text}")

#         if response.status_code == 204:
#             return JsonResponse({"message": f"Project '{project_name}' updated successfully."}, status=200)

#         response.raise_for_status()
#         return JsonResponse(response.json())

#     except requests.exceptions.RequestException as e:
#         print(f"Request exception: {e}")
#         return JsonResponse({"error": str(e)}, status=500)
#     except json.JSONDecodeError:
#         print("Invalid JSON body received from external API.")
#         return JsonResponse({"error": "Invalid JSON body received from external API."}, status=500)


class MyTable(tables.Table):
    login = tables.Column()
    date = tables.Column(orderable=True)
    day = tables.Column()
    task = tables.LinkColumn(
        'task_detail',
        args=[tables.A('task_id')],
        verbose_name='Task',
        text=lambda record: record.get('task', 'Unknown Task'),
    )
    start_time = tables.Column()
    stop_time = tables.Column()
    work_time = tables.Column()
    system_id = tables.Column()
    department = tables.Column()

    class Meta:
        order_by = "-date"

# View function
def get_time_data(request):
    # Fetch and sort data by date (descending)
    time_data = list(time_data_collection.find({}, {'_id': 0}).sort("date", -1))

    # Normalize date field to datetime objects for accurate sorting

    for entry in time_data:
        try:
            # Normalize date format: Replace colons with hyphens
            normalized_date = entry['date'].replace(":", "-")
            entry['date'] = datetime.strptime(normalized_date, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Error parsing date for entry {entry}: {e}")
            # Handle entries with invalid dates (e.g., skip or assign a default value)
            entry['date'] = None

        if 'task' in entry:
            task_info = list(entry['task'].values())[0]
            entry['task_id'] = task_info.split('ID: ')[1].split(',')[0] if 'ID: ' in task_info else None

    # Manual filtering from GET parameters
    login = request.GET.get("login")
    date = request.GET.get("date")
    project = request.GET.get("project")
    system_id = request.GET.get("system_id")
    department = request.GET.get("department")

    if login:
        time_data = [entry for entry in time_data if login.lower() in entry.get("login", "").lower()]
    if date:
        time_data = [entry for entry in time_data if entry.get("date").strftime('%Y-%m-%d') == date]
    if project:
        time_data = [
            entry for entry in time_data if any(project.lower() in p.lower() for p in entry.get("project", []))
        ]
    if system_id:
        time_data = [entry for entry in time_data if system_id.lower() in entry.get("system_id", "").lower()]
    if department:
        time_data = [entry for entry in time_data if department.lower() in entry.get("department", "").lower()]

    # Paginate the data
    paginator = Paginator(time_data, 10)  # Show 10 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Create the table
    table = MyTable(page_obj)
    RequestConfig(request).configure(table)

    context = {
        "table": table,
        "page_obj": page_obj,
    }

    logger.debug(f"Rendered context: {context}")
    return render(request, 'timecard.html', context)

def get_access_token():
    login_url = "http://localhost:30008/api/auth/login"
    credentials = {"name": "balajid", "password": "Gotham9!"}
    try:
        response = requests.post(login_url, json=credentials)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        token = response_data.get("token")  # Retrieve the token key
        if not token:
            raise ValueError("No access token found in response.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    return None



def graphql_projects_view(request):
    # Define the GraphQL query
    query = """
        {
        projects {
            edges {
            node {
                active
                allAttrib
                code
                createdAt
                data
                name
                library
                projectName
            }
            }
        }
        }
    """
    # Replace with your GraphQL API endpoint
    endpoint = "http://localhost:30008/graphql"

    # Replace with your actual token
    access_token = get_access_token()
    print("access_token",access_token)

    try:
        # Fetch data from the GraphQL API with the access token
        response = requests.post(
            endpoint,
            json={"query": query},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()
        projects = data.get("data", {}).get("projects", {}).get("edges", [])
    except requests.exceptions.RequestException as e:
        projects = []
        print(f"Error fetching GraphQL data: {e}")

    context = {"projects": projects}
    return render(request, 'ql_projects.html', context)

@csrf_exempt
def edit_project(request, project_id):
    # Define the REST API endpoint
    api_url = f"http://localhost:30008/api/projects/{project_id}"

    if request.method == "POST":
        # Get updated data from the form
        project_name = request.POST.get("project_name")
        description = request.POST.get("description")

        # Prepare the data payload for the REST API
        data = {
            "name": project_name,
            "description": description
        }

        # Send the update request to the REST API
        access_token = get_access_token()  # Fetch the access token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.put(api_url, json=data, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                messages.success(request, "Project updated successfully!")
            else:
                messages.error(request, f"Failed to update project: {response.json().get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error connecting to API: {e}")

        # Redirect back to the projects list
        return redirect("proj")

    # Fetch existing project data for pre-filling the form
    access_token = get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        project_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching project details: {e}")
        project_data = {}

    return render(request, "edit_project.html", {"project": project_data})



# ##################################################################### #

# import requests

# def fetch_ayon_data(request):
#     url = f"http://localhost:30008/api/projects"
    
#     access_token = get_access_token() 
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {access_token}",
#     }

#     query = """
#             {
#             "detail": "Showing LENGTH of COUNT projects",
#             "count": 1,
#             "projects": [
#                 {
#                 "name": "Example project",
#                 "code": "ex",
#                 "active": true,
#                 "createdAt": "2025-03-21T10:01:23.977185",
#                 "updatedAt": "2025-03-21T10:01:23.977194"
#                 }
#             ]
#             }
#     """
#     try:
#         response = requests.get(url, json={"query": query}, headers=headers)
#         print(response)
#         if response.status_code == 200:
#             data = response.json().get("data", {}).get("projects", [])
#             print("data",data)
#         else:
#             data = []
#     except Exception as e:
#         data = []

#     return render(request, "ayon_table.html", {"data": data})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

ACCESS_TOKEN = get_access_token()


def projects_ui(request):
    """
    Renders the Projects Management UI.
    """
    return render(request, "ayon_table.html") 



def get_projects(request):
    """
    Fetch all projects from the external API and return them as JSON.
    """
    try:
        response = requests.get("http://localhost:30008/api/projects", headers=get_headers())
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def update_project(request, project_name):
    """
    Update a specific project using the PATCH method.
    """
    if request.method != "PATCH":
        return JsonResponse({"error": "Invalid request method. Use PATCH."}, status=405)

    try:
        # Log incoming data
        print(f"Received update for project: {project_name}")
        updates = json.loads(request.body)
        print(f"Update data: {updates}")

        # Construct API URL
        url = f"http://localhost:30008/api/projects/{project_name}"

        # Perform PATCH request
        response = requests.patch(url, json=updates, headers=get_headers())
        print(f"External API response status: {response.status_code}")
        print(f"External API response text: {response.text}")

        # Handle 204 No Content
        if response.status_code == 204:
            return JsonResponse({"message": f"Project '{project_name}' updated successfully."}, status=200)

        # Parse response JSON for other status codes
        response.raise_for_status()
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    except json.JSONDecodeError:
        print("Invalid JSON body received from external API.")
        return JsonResponse({"error": "Invalid JSON body received from external API."}, status=500)
    


########################################   Tasks ################################################



def autocomplete_users(request):
    term = request.GET.get("term", "")
    ddio_instance = dd_io()
    all_users = ddio_instance.io_get_users()
    matching_users = [user for user in all_users if term.lower() in user.lower()]
    return JsonResponse({"users": matching_users})
