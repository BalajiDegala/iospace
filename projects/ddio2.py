#!/usr/bin/env python
import os
import ayon_api
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

class dd_io():
    def __init__(self, project=None, seq = None, shot = None , user= None):
        self.project = project
        self.seq = seq
        self.shot = shot
        self.user = user
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
        shot_id = self.io_get_shot_id()
        if shot_id is not None:
            ayon_tasks = self.con.get_tasks(self.project, folder_ids = [shot_id])
        else:
            ayon_tasks = self.con.get_tasks(self.project)
        tasks = []
        for task in ayon_tasks:
            tasks.append(task)
        return tasks

    def io_get_task(self, task_id):
        if task_id is not None:
            ayon_tasks = self.con.get_tasks("HYD", task_ids = task_id)
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

    def io_get_events(self):
        ayon_events = self.con.get_events(limit=100)
        events = [event for event in ayon_events ]
        return events





x = dd_io()
zx = x.io_get_events()
print(zx)