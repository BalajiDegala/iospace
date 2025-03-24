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

def home(request):
    val = dd_io()
    events = val.io_get_events()
    context = {"events": []}
    return render(request, 'home.html', context)

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
            print("result",result)
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
    tasks = val.io_get_tasks()
    context = {"shot_name": shot_name ,"project_name": project_name, "sequence_name": sequence_name, "tasks": tasks}
    return render(request, 'tasks.html', context)

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
    print("user_tasks",user_tasks)
    return render(request, 'my_tasks.html', {'tasks_by_show': user_tasks})
    
    
def task_detail(request, task_id):
    val = dd_io()  

    task = val.io_get_task(task_id=task_id)
    if not task:
        return render(request, 'task_detail.html', {'error': 'Task not found'})
    context = {"task": task[0]}  
    return render(request, 'task_detail.html', context)



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
    login_url = "http://localhost:5000/api/auth/login"
    credentials = {"name": "balajid", "password": "Gotham9!"}
    try:
        response = requests.post(login_url, json=credentials)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        print(f"Login response: {response_data}")  # Debug the response
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
    endpoint = "http://localhost:5000/graphql"

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
    api_url = f"http://localhost:5000/api/projects/{project_id}"

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

