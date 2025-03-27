#!/usr/bin/env python
import os
import ayon_api
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

class RequestType:
    def __init__(self, name: str):
        self.name: str = name

    def __hash__(self):
        return self.name.__hash__()



class RequestTypes:
    get = RequestType("GET")
    post = RequestType("POST")
    put = RequestType("PUT")
    patch = RequestType("PATCH")
    delete = RequestType("DELETE")

class dd_io():
    def __init__(self, project=None, seq = None, shot = None , task = None , user= None):
        self.project = project
        self.seq = seq
        self.shot = shot
        self.user = user
        self.task = task
        self.con = ayon_api.GlobalServerAPI()
        self.con.login("balajid", "Gotham9!")

    def io_get_projects(self):
        ayon_projects = self.con.get_projects()
        projects = []
        for project in ayon_projects:
            projects.append(project["name"])
        return projects

    def io_get_users(self):
        ayon_users = self.con.get_users()
        users = []
        for user in ayon_users:
            users.append(user["name"])
        return users
        
    def io_get_tasks(self):
        tasks = self.con.get_tasks(self.project)
        return [task for task in tasks]

    def io_update_task(self, task_id, **kwargs):
        if not self.project:
            raise ValueError("Project name must be specified to update a task.")
        
        update_data = {key: value for key, value in kwargs.items() if value is not None}
        
        try:
            self.con.update_task(project_name=self.project, task_id=task_id, **update_data)
            return f"Task with ID {task_id} updated successfully."
        except Exception as e:
            return f"Failed to update task: {e}"


    def io_get_shot_tasks(self):
        shot_id = self.io_get_shot_id()
        if shot_id is not None:
            ayon_tasks = self.con.get_tasks(self.project, folder_ids = [shot_id])
        else:
            ayon_tasks = self.con.get_tasks(self.project)
        tasks = []
        for task in ayon_tasks:
            tasks.append(task)
        return tasks

    def io_get_task(self,task_id):
        if task_id :
            ayon_tasks = self.con.get_tasks(self.project, task_ids = task_id)
        else :
            print("Please check for task ID")
            return None
        tasks = []
        for task in ayon_tasks:
            tasks.append(task)
        return tasks


    def io_get_user_tasks(self, project):
        try:
            print(f"Fetching tasks for user: {self.user}")
            # Attempt to use the assignees filter directly
            ayon_tasks = self.con.get_tasks(project, assignees=self.user)
            tasks = [task for task in ayon_tasks]
            return tasks
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def io_get_folders(self):
        ayon_folders = self.con.get_folders(self.project)
        folders = []
        for folder in ayon_folders:
            folders.append(folder)
        return folders
    
    def io_update_folder(
        self,
        folder_id: str,
        name=None,
        folder_type=None,
        label=None,
        attrib=None,
        status=None,
        active=None,
    ):
        """Update folder attributes for a specific folder."""
        if not self.project:
            raise ValueError("Project name must be specified to update a folder.")

        # Prepare the update data
        update_data = {}
        for key, value in (
            ("name", name),
            ("folderType", folder_type),
            ("label", label),
            ("attrib", attrib),
            ("status", status),
            ("active", active),
        ):
            if value is not None:
                update_data[key] = value

        # Call the API update method
        try:
            self.con.update_folder(
                project_name=self.project,
                folder_id=folder_id,
                **update_data
            )
            return f"Folder with ID {folder_id} updated successfully."
        except Exception as e:
            return f"Failed to update folder: {e}"



    def io_get_sequences(self):
        ayon_sequences = self.con.get_folders(self.project, folder_types="Sequence")
        sequences = []
        for sequence in ayon_sequences:
            sequences.append(sequence["name"])
        return sequences
        
    def io_get_shots(self):
        get_seq = self.con.get_folder_by_name(self.project,self.seq)
        seq_id = get_seq["id"]
        shots = []
        ayon_shots = self.con.get_folders(self.project, parent_ids = [seq_id], folder_types="Shot")
        for shot in ayon_shots:
            shots.append(shot["name"])
        return shots

    def io_get_shot_id(self):
        try:
            get_seq = self.con.get_folder_by_name(self.project,self.seq)
            seq_id = get_seq["id"]
            get_shot = self.con.get_folders(self.project, parent_ids = [seq_id], folder_types="Shot")
            if self.shot is not None:
                for i in get_shot:
                    if i["name"] ==  self.shot:
                        return i["id"] 
                    else:
                        print("Please provide the correct Shot Name")
                        return None

        except Exception as e :
            return e

    def io_create_project(self):
        try:
            proj_code = self.project.upper()
            self.con.create_project(self.project, proj_code ,preset_name = "DDHB")
            return f"{self.project} Project Created successfully"
        except Exception as e :
            return e

    def io_create_sequence(self):
        try:
            self.con.create_folder(self.project, self.seq ,folder_type="Sequence")
            return f"{self.seq} Sequence Created successfully"
        except Exception as e :
            return e

    def io_create_shot(self):
        try:
            get_seq = self.con.get_folder_by_name(self.project,self.seq)
            seq_id = get_seq["id"]
            self.con.create_folder(self.project, self.shot, parent_id = seq_id , folder_type="Shot")
            return f"{self.shot} Shot Created successfully on {self.seq} Sequence {self.project} project"
        except Exception as e :
            return f"Failed to create shot: {e}" 

    def io_create_task(self, task_type):
        try:
            get_shot = self.con.get_folder_by_path(self.project,f"{self.seq}/{self.shot}")
            shot_id = get_shot["id"]
            print("shot_id",get_shot)
            self.con.create_task(self.project, self.task ,  task_type = task_type , folder_id = shot_id )
            return f"{self.task} Shot Created successfully on {self.shot} Shot on {self.seq} {self.project} project"
        except Exception as e :
            return f"Failed to create shot: {e}" 
        

    def io_get_events(self):
        ayon_events = self.con.get_events(limit=100)
        events = [event for event in ayon_events ]
        return events

    


from django.apps import AppConfig
class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'



