from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .api_client import AyonAPIClient
from .forms import ProjectForm, SequenceForm, ShotForm, TaskForm

# Initialize API client
api_client = AyonAPIClient()

@login_required
def dashboard_view(request):
    """Dashboard view showing overview of projects."""
    try:
        api_response = api_client.get_projects()
        print("API response (projects):", api_response)  # Debugging: Print the API response
        
        # Extract the projects list from the response dictionary
        if isinstance(api_response, dict) and 'projects' in api_response:
            projects = api_response['projects']
        else:
            projects = api_response
        
        # Ensure projects is a list
        if not isinstance(projects, list):
            raise ValueError(f"Expected a list of projects, but got: {type(projects)}")
        
        # Get some stats
        projects_count = len(projects)
        active_projects = sum(1 for p in projects if p.get('active', False))
        
        return render(request, 'dashboard.html', {
            'projects': projects[:5],  # Show the first 5 projects
            'projects_count': projects_count,
            'active_projects': active_projects
        })
    except Exception as e:
        messages.error(request, f"Error fetching dashboard data: {str(e)}")
        return render(request, 'dashboard.html', {
            'error': str(e)
        })

# Project views
@login_required
def project_list(request):
    try:
        response = api_client.get_projects()
        
        # Extract the projects list from the response
        if isinstance(response, dict) and 'projects' in response:
            projects = response['projects']
        else:
            projects = response
            
        print("Projects data:", projects)
        return render(request, 'projects/list.html', {'projects': projects})
    except Exception as e:
        messages.error(request, f"Error fetching projects: {str(e)}")
        return render(request, 'projects/list.html', {'error': str(e)})

@login_required
def project_detail(request, project_name):
    """View showing details of a specific project."""
    try:
        project = api_client.get_project(project_name)
        sequences = api_client.get_folders(project_name, folder_type="Sequence")
        shots = api_client.get_products(project_name, product_type="Shot")
        tasks = api_client.get_tasks(project_name)
        
        return render(request, 'projects/detail.html', {
            'project': project,
            'project_name': project_name,  
            'sequences_count': len(sequences),
            'shots_count': len(shots),
            'tasks_count': len(tasks),
            'sequences': sequences[:5],  # Show first 5 sequences
            'shots': shots[:5],  # Show first 5 shots
            'tasks': tasks[:5]  # Show first 5 tasks
        })
    except Exception as e:
        messages.error(request, f"Error fetching project details: {str(e)}")
        return render(request, 'projects/detail.html', {'error': str(e)})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            try:
                project_name = form.cleaned_data['name']
                project_data = {
                    "code": form.cleaned_data['code'],
                    "library": False,
                    "folderTypes": [
                        {
                            "name": "FolderType1",
                            "original_name": "FolderType1",
                            "shortName": "",
                            "icon": "folder"
                        }
                    ],
                    "taskTypes": [
                        {
                            "name": "TaskType1",
                            "original_name": "TaskType1",
                            "shortName": "",
                            "color": "#cccccc",
                            "icon": "task_alt"
                        }
                    ],
                    "linkTypes": [
                        {
                            "name": "reference|version|version",
                            "link_type": "reference",
                            "input_type": "version",
                            "output_type": "version",
                            "data": {
                                "color": "#ff0000"
                            }
                        }
                    ],
                    "statuses": [
                        {
                            "name": "Status1",
                            "original_name": "Status1",
                            "shortName": "PRG",
                            "state": "in_progress",
                            "icon": "play_arrow",
                            "color": "#3498db",
                            "scope": [
                                "folder",
                                "product",
                                "version",
                                "representation",
                                "task",
                                "workfile"
                            ]
                        }
                    ],
                    "tags": [
                        {
                            "name": "Tag1",
                            "original_name": "Tag1",
                            "color": "#3498db"
                        }
                    ],
                    "config": {},
                    "attrib": {
                        "priority": "urgent",
                        "fps": 25,
                        "resolutionWidth": 1920,
                        "resolutionHeight": 1080,
                        "pixelAspect": 1,
                        "clipIn": 1,
                        "clipOut": 1,
                        "frameStart": 1001,
                        "frameEnd": 1001,
                        "handleStart": 0,
                        "handleEnd": 0,
                        "startDate": "2021-01-01T00:00:00+00:00",
                        "endDate": "2021-01-01T00:00:00+00:00",
                        "description": form.cleaned_data['description']
                    },
                    "data": {},
                    "active": True
                }
                
                print("Project data being sent:", project_data)  # Debugging: Print the payload
                
                api_client.create_project(project_name, project_data)
                messages.success(request, f"Project '{project_name}' created successfully!")
                return redirect('project_list')
            except Exception as e:
                messages.error(request, f"Error creating project: {str(e)}")
                print("API error response:", e)  # Debugging: Print the error
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create.html', {'form': form})

@login_required
def project_update(request, project_name):
    """View for updating an existing project."""
    try:
        project = api_client.get_project(project_name)
    except Exception as e:
        messages.error(request, f"Error fetching project: {str(e)}")
        return redirect('project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            try:
                project_data = {
                    'name': form.cleaned_data['name'],
                    'code': form.cleaned_data['code'],
                    'library': form.cleaned_data['library'],
                    'active': form.cleaned_data['active'],
                    'description': form.cleaned_data['description']
                }
                
                # Add deadline if provided
                if form.cleaned_data['deadline']:
                    project_data['deadline'] = form.cleaned_data['deadline'].isoformat()
                
                api_client.update_project(project_name, project_data)
                messages.success(request, f"Project '{project_name}' updated successfully!")
                return redirect('project_detail', project_name=form.cleaned_data['name'])
            except Exception as e:
                messages.error(request, f"Error updating project: {str(e)}")
    else:
        # Convert deadline string to date object if it exists
        initial_data = project.copy()
        if 'deadline' in project and project['deadline']:
            from datetime import datetime
            try:
                initial_data['deadline'] = datetime.fromisoformat(project['deadline']).date()
            except (ValueError, TypeError):
                initial_data['deadline'] = None
        
        form = ProjectForm(initial=initial_data)
    
    return render(request, 'projects/update.html', {
        'form': form,
        'project': project
    })

@login_required
def project_delete(request, project_name):
    """View for deleting a project."""
    if request.method == 'POST':
        try:
            api_client.delete_project(project_name)
            messages.success(request, f"Project '{project_name}' deleted successfully!")
            return redirect('project_list')
        except Exception as e:
            messages.error(request, f"Error deleting project: {str(e)}")
            return redirect('project_detail', project_name=project_name)
    
    try:
        project = api_client.get_project(project_name)
        return render(request, 'projects/delete.html', {'project': project})
    except Exception as e:
        messages.error(request, f"Error fetching project: {str(e)}")
        return redirect('project_list')

# Sequence (Folder) views
@login_required
def sequence_list(request, project_name):
    """View showing all sequences in a project."""
    try:
        project = api_client.get_project(project_name)
        sequences = api_client.get_folders(project_name, folder_type="Sequence")
        return render(request, 'sequences/list.html', {
            'project': project,
            'sequences': sequences
        })
    except Exception as e:
        messages.error(request, f"Error fetching sequences: {str(e)}")
        return render(request, 'sequences/list.html', {
            'project_name': project_name,
            'error': str(e)
        })

@login_required
def sequence_detail(request, project_name, sequence_id):
    """View showing details of a specific sequence."""
    try:
        project = api_client.get_project(project_name)
        sequence = api_client.get_folder(project_name, sequence_id)
        
        # Get shots in this sequence
        all_shots = api_client.get_products(project_name, product_type="Shot")
        shots = [shot for shot in all_shots if shot.get('folder_id') == sequence_id]
        
        return render(request, 'sequences/detail.html', {
            'project': project,
            'sequence': sequence,
            'shots': shots
        })
    except Exception as e:
        messages.error(request, f"Error fetching sequence details: {str(e)}")
        return render(request, 'sequences/detail.html', {
            'project_name': project_name,
            'sequence_id': sequence_id,
            'error': str(e)
        })

@login_required
def sequence_create(request, project_name):
    """View for creating a new sequence."""
    try:
        project = api_client.get_project(project_name)
        folders = api_client.get_folders(project_name)
    except Exception as e:
        messages.error(request, f"Error fetching project data: {str(e)}")
        return redirect('project_detail', project_name=project_name)
    
    if request.method == 'POST':
        form = SequenceForm(request.POST, folders=folders)
        if form.is_valid():
            try:
                sequence_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'folder_type': 'Sequence',
                    'description': form.cleaned_data['description']
                }
                
                # Add parent folder if provided
                if form.cleaned_data['parent_id']:
                    sequence_data['parent_id'] = form.cleaned_data['parent_id']
                
                api_client.create_folder(project_name, sequence_data)
                messages.success(request, f"Sequence '{form.cleaned_data['name']}' created successfully!")
                return redirect('sequence_list', project_name=project_name)
            except Exception as e:
                messages.error(request, f"Error creating sequence: {str(e)}")
    else:
        form = SequenceForm(folders=folders)
    
    return render(request, 'sequences/create.html', {
        'form': form,
        'project': project
    })

@login_required
def sequence_update(request, project_name, sequence_id):
    """View for updating an existing sequence."""
    try:
        project = api_client.get_project(project_name)
        sequence = api_client.get_folder(project_name, sequence_id)
        folders = api_client.get_folders(project_name)
    except Exception as e:
        messages.error(request, f"Error fetching sequence data: {str(e)}")
        return redirect('sequence_list', project_name=project_name)
    
    if request.method == 'POST':
        form = SequenceForm(request.POST, folders=folders)
        if form.is_valid():
            try:
                sequence_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'folder_type': 'Sequence',
                    'description': form.cleaned_data['description']
                }
                
                # Add parent folder if provided
                if form.cleaned_data['parent_id']:
                    sequence_data['parent_id'] = form.cleaned_data['parent_id']
                
                api_client.update_folder(project_name, sequence_id, sequence_data)
                messages.success(request, f"Sequence '{form.cleaned_data['name']}' updated successfully!")
                return redirect('sequence_detail', project_name=project_name, sequence_id=sequence_id)
            except Exception as e:
                messages.error(request, f"Error updating sequence: {str(e)}")
    else:
        initial_data = {
            'name': sequence.get('name', ''),
            'label': sequence.get('label', ''),
            'parent_id': sequence.get('parent_id', ''),
            'description': sequence.get('description', '')
        }
        form = SequenceForm(initial=initial_data, folders=folders)
    
    return render(request, 'sequences/update.html', {
        'form': form,
        'project': project,
        'sequence': sequence
    })

@login_required
def sequence_delete(request, project_name, sequence_id):
    """View for deleting a sequence."""
    try:
        project = api_client.get_project(project_name)
        sequence = api_client.get_folder(project_name, sequence_id)
    except Exception as e:
        messages.error(request, f"Error fetching sequence: {str(e)}")
        return redirect('sequence_list', project_name=project_name)
    
    if request.method == 'POST':
        try:
            api_client.delete_folder(project_name, sequence_id)
            messages.success(request, f"Sequence '{sequence['name']}' deleted successfully!")
            return redirect('sequence_list', project_name=project_name)
        except Exception as e:
            messages.error(request, f"Error deleting sequence: {str(e)}")
    
    return render(request, 'sequences/delete.html', {
        'project': project,
        'sequence': sequence
    })

# Shot (Product) views
@login_required
def shot_list(request, project_name):
    """View showing all shots in a project."""
    try:
        project = api_client.get_project(project_name)
        shots = api_client.get_products(project_name, product_type="Shot")
        sequences = api_client.get_folders(project_name, folder_type="Sequence")
        
        # Create a mapping of folder_id to folder name for display
        folder_map = {folder['id']: folder['name'] for folder in sequences}
        
        return render(request, 'shots/list.html', {
            'project': project,
            'shots': shots,
            'folder_map': folder_map
        })
    except Exception as e:
        messages.error(request, f"Error fetching shots: {str(e)}")
        return render(request, 'shots/list.html', {
            'project_name': project_name,
            'error': str(e)
        })

@login_required
def shot_detail(request, project_name, shot_id):
    """View showing details of a specific shot."""
    try:
        project = api_client.get_project(project_name)
        shot = api_client.get_product(project_name, shot_id)
        
        # Get the sequence this shot belongs to
        sequence = None
        if 'folder_id' in shot:
            try:
                sequence = api_client.get_folder(project_name, shot['folder_id'])
            except:
                pass
        
        # Get tasks for this shot
        tasks = api_client.get_tasks(project_name, product_id=shot_id)
        
        return render(request, 'shots/detail.html', {
            'project': project,
            'shot': shot,
            'sequence': sequence,
            'tasks': tasks
        })
    except Exception as e:
        messages.error(request, f"Error fetching shot details: {str(e)}")
        return render(request, 'shots/detail.html', {
            'project_name': project_name,
            'shot_id': shot_id,
            'error': str(e)
        })

@login_required
def shot_create(request, project_name):
    """View for creating a new shot."""
    try:
        project = api_client.get_project(project_name)
        sequences = api_client.get_folders(project_name, folder_type="Sequence")
    except Exception as e:
        messages.error(request, f"Error fetching project data: {str(e)}")
        return redirect('project_detail', project_name=project_name)
    
    if request.method == 'POST':
        form = ShotForm(request.POST, folders=sequences)
        if form.is_valid():
            try:
                shot_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'folder_id': form.cleaned_data['folder_id'],
                    'product_type': 'Shot',
                    'status': form.cleaned_data['status'],
                    'description': form.cleaned_data['description'],
                    'attrib': {
                        'frameStart': form.cleaned_data['frame_start'],
                        'frameEnd': form.cleaned_data['frame_end']
                    }
                }
                
                api_client.create_product(project_name, shot_data)
                messages.success(request, f"Shot '{form.cleaned_data['name']}' created successfully!")
                return redirect('shot_list', project_name=project_name)
            except Exception as e:
                messages.error(request, f"Error creating shot: {str(e)}")
    else:
        form = ShotForm(folders=sequences)
    
    return render(request, 'shots/create.html', {
        'form': form,
        'project': project
    })

@login_required
def shot_update(request, project_name, shot_id):
    """View for updating an existing shot."""
    try:
        project = api_client.get_project(project_name)
        shot = api_client.get_product(project_name, shot_id)
        sequences = api_client.get_folders(project_name, folder_type="Sequence")
    except Exception as e:
        messages.error(request, f"Error fetching shot data: {str(e)}")
        return redirect('shot_list', project_name=project_name)
    
    if request.method == 'POST':
        form = ShotForm(request.POST, folders=sequences)
        if form.is_valid():
            try:
                shot_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'folder_id': form.cleaned_data['folder_id'],
                    'product_type': 'Shot',
                    'status': form.cleaned_data['status'],
                    'description': form.cleaned_data['description'],
                    'attrib': {
                        'frameStart': form.cleaned_data['frame_start'],
                        'frameEnd': form.cleaned_data['frame_end']
                    }
                }
                
                api_client.update_product(project_name, shot_id, shot_data)
                messages.success(request, f"Shot '{form.cleaned_data['name']}' updated successfully!")
                return redirect('shot_detail', project_name=project_name, shot_id=shot_id)
            except Exception as e:
                messages.error(request, f"Error updating shot: {str(e)}")
    else:
        attrib = shot.get('attrib', {})
        initial_data = {
            'name': shot.get('name', ''),
            'label': shot.get('label', ''),
            'folder_id': shot.get('folder_id', ''),
            'status': shot.get('status', 'in_progress'),
            'description': shot.get('description', ''),
            'frame_start': attrib.get('frameStart', 1001),
            'frame_end': attrib.get('frameEnd', 1100)
        }
        form = ShotForm(initial=initial_data, folders=sequences)
    
    return render(request, 'shots/update.html', {
        'form': form,
        'project': project,
        'shot': shot
    })

@login_required
def shot_delete(request, project_name, shot_id):
    """View for deleting a shot."""
    try:
        project = api_client.get_project(project_name)
        shot = api_client.get_product(project_name, shot_id)
    except Exception as e:
        messages.error(request, f"Error fetching shot: {str(e)}")
        return redirect('shot_list', project_name=project_name)
    
    if request.method == 'POST':
        try:
            api_client.delete_product(project_name, shot_id)
            messages.success(request, f"Shot '{shot['name']}' deleted successfully!")
            return redirect('shot_list', project_name=project_name)
        except Exception as e:
            messages.error(request, f"Error deleting shot: {str(e)}")
    
    return render(request, 'shots/delete.html', {
        'project': project,
        'shot': shot
    })

# Task views
@login_required
def task_list(request, project_name):
    """View showing all tasks in a project."""
    try:
        project = api_client.get_project(project_name)
        tasks = api_client.get_tasks(project_name)
        
        # Get all shots to create a mapping
        shots = api_client.get_products(project_name, product_type="Shot")
        shot_map = {shot['id']: shot['name'] for shot in shots}
        
        return render(request, 'tasks/list.html', {
            'project': project,
            'tasks': tasks,
            'shot_map': shot_map
        })
    except Exception as e:
        messages.error(request, f"Error fetching tasks: {str(e)}")
        return render(request, 'tasks/list.html', {
            'project_name': project_name,
            'error': str(e)
        })

@login_required
def task_detail(request, project_name, task_id):
    """View showing details of a specific task."""
    try:
        project = api_client.get_project(project_name)
        task = api_client.get_task(project_name, task_id)
        
        # Get the shot this task belongs to
        shot = None
        if 'product_id' in task:
            try:
                shot = api_client.get_product(project_name, task['product_id'])
            except:
                pass
        
        return render(request, 'tasks/detail.html', {
            'project': project,
            'task': task,
            'shot': shot
        })
    except Exception as e:
        messages.error(request, f"Error fetching task details: {str(e)}")
        return render(request, 'tasks/detail.html', {
            'project_name': project_name,
            'task_id': task_id,
            'error': str(e)
        })

@login_required
def task_create(request, project_name):
    """View for creating a new task."""
    try:
        project = api_client.get_project(project_name)
        products = api_client.get_products(project_name)
        
        # Get task types and statuses (assuming these are available via the API)
        task_types = api_client.get_task_types(project_name) if hasattr(api_client, 'get_task_types') else []
        statuses = api_client.get_statuses(project_name) if hasattr(api_client, 'get_statuses') else []
    except Exception as e:
        messages.error(request, f"Error fetching project data: {str(e)}")
        return redirect('project_detail', project_name=project_name)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, products=products, task_types=task_types, statuses=statuses)
        if form.is_valid():
            try:
                # Parse assignees from comma-separated string
                assignees = [assignee.strip() for assignee in form.cleaned_data['assignees'].split(',') if assignee.strip()]
                
                task_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'product_id': form.cleaned_data['product_id'],
                    'task_type': form.cleaned_data['task_type'],
                    'status': form.cleaned_data['status'],
                    'description': form.cleaned_data['description'],
                    'assignees': assignees
                }
                
                api_client.create_task(project_name, task_data)
                messages.success(request, f"Task '{form.cleaned_data['name']}' created successfully!")
                return redirect('task_list', project_name=project_name)
            except Exception as e:
                messages.error(request, f"Error creating task: {str(e)}")
    else:
        form = TaskForm(products=products, task_types=task_types, statuses=statuses)
    
    return render(request, 'tasks/create.html', {
        'form': form,
        'project': project
    })

@login_required
def task_update(request, project_name, task_id):
    """View for updating an existing task."""
    try:
        project = api_client.get_project(project_name)
        task = api_client.get_task(project_name, task_id)
        products = api_client.get_products(project_name)
        
        # Get task types and statuses
        task_types = api_client.get_task_types(project_name) if hasattr(api_client, 'get_task_types') else []
        statuses = api_client.get_statuses(project_name) if hasattr(api_client, 'get_statuses') else []
    except Exception as e:
        messages.error(request, f"Error fetching task data: {str(e)}")
        return redirect('task_list', project_name=project_name)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, products=products, task_types=task_types, statuses=statuses)
        if form.is_valid():
            try:
                # Parse assignees from comma-separated string
                assignees = [assignee.strip() for assignee in form.cleaned_data['assignees'].split(',') if assignee.strip()]
                
                task_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'product_id': form.cleaned_data['product_id'],
                    'task_type': form.cleaned_data['task_type'],
                    'status': form.cleaned_data['status'],
                    'description': form.cleaned_data['description'],
                    'assignees': assignees
                }
                
                api_client.update_task(project_name, task_id, task_data)
                messages.success(request, f"Task '{form.cleaned_data['name']}' updated successfully!")
                return redirect('task_detail', project_name=project_name, task_id=task_id)
            except Exception as e:
                messages.error(request, f"Error updating task: {str(e)}")
    else:
        # Convert assignees list to comma-separated string
        assignees = ', '.join(task.get('assignees', []))
        
        initial_data = {
            'name': task.get('name', ''),
            'label': task.get('label', ''),
            'product_id': task.get('product_id', ''),
            'task_type': task.get('task_type', ''),
            'status': task.get('status', 'todo'),
            'description': task.get('description', ''),
            'assignees': assignees
        }
        form = TaskForm(initial=initial_data, products=products, task_types=task_types, statuses=statuses)
    
    return render(request, 'tasks/update.html', {
        'form': form,
        'project': project,
        'task': task
    })

@login_required
def task_delete(request, project_name, task_id):
    """View for deleting a task."""
    try:
        project = api_client.get_project(project_name)
        task = api_client.get_task(project_name, task_id)
    except Exception as e:
        messages.error(request, f"Error fetching task: {str(e)}")
        return redirect('task_list', project_name=project_name)
    
    if request.method == 'POST':
        try:
            api_client.delete_task(project_name, task_id)
            messages.success(request, f"Task '{task['name']}' deleted successfully!")
            return redirect('task_list', project_name=project_name)
        except Exception as e:
            messages.error(request, f"Error deleting task: {str(e)}")
    
    return render(request, 'tasks/delete.html', {
        'project': project,
        'task': task
    })

@login_required
def shot_task_list(request, project_name, shot_id):
    """View showing all tasks for a specific shot."""
    try:
        project = api_client.get_project(project_name)
        shot = api_client.get_product(project_name, shot_id)
        tasks = api_client.get_tasks(project_name, product_id=shot_id)
        
        return render(request, 'tasks/shot_task_list.html', {
            'project': project,
            'shot': shot,
            'tasks': tasks
        })
    except Exception as e:
        messages.error(request, f"Error fetching shot tasks: {str(e)}")
        return render(request, 'tasks/shot_task_list.html', {
            'project_name': project_name,
            'shot_id': shot_id,
            'error': str(e)
        })

@login_required
def shot_task_create(request, project_name, shot_id):
    """View for creating a new task for a specific shot."""
    try:
        project = api_client.get_project(project_name)
        shot = api_client.get_product(project_name, shot_id)
        
        # Get task types and statuses
        task_types = api_client.get_task_types(project_name) if hasattr(api_client, 'get_task_types') else []
        statuses = api_client.get_statuses(project_name) if hasattr(api_client, 'get_statuses') else []
    except Exception as e:
        messages.error(request, f"Error fetching shot data: {str(e)}")
        return redirect('shot_detail', project_name=project_name, shot_id=shot_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, task_types=task_types, statuses=statuses)
        if form.is_valid():
            try:
                # Parse assignees from comma-separated string
                assignees = [assignee.strip() for assignee in form.cleaned_data['assignees'].split(',') if assignee.strip()]
                
                task_data = {
                    'name': form.cleaned_data['name'],
                    'label': form.cleaned_data['label'] or form.cleaned_data['name'],
                    'product_id': shot_id,  # Use the shot_id directly
                    'task_type': form.cleaned_data['task_type'],
                    'status': form.cleaned_data['status'],
                    'description': form.cleaned_data['description'],
                    'assignees': assignees
                }
                
                api_client.create_task(project_name, task_data)
                messages.success(request, f"Task '{form.cleaned_data['name']}' created successfully!")
                return redirect('shot_task_list', project_name=project_name, shot_id=shot_id)
            except Exception as e:
                messages.error(request, f"Error creating task: {str(e)}")
    else:
        # Pre-fill the product_id with the shot_id
        initial_data = {
            'product_id': shot_id
        }
        form = TaskForm(initial=initial_data, task_types=task_types, statuses=statuses)
    
    return render(request, 'tasks/shot_task_create.html', {
        'form': form,
        'project': project,
        'shot': shot
    })