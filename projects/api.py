 def get_folders(
        self,
        project_name: str,
        folder_ids: Optional[Iterable[str]] = None,
        folder_paths: Optional[Iterable[str]] = None,
        folder_names: Optional[Iterable[str]] = None,
        folder_types: Optional[Iterable[str]] = None,
        parent_ids: Optional[Iterable[str]] = None,
        folder_path_regex: Optional[str] = None,
        has_products: Optional[bool] = None,
        has_tasks: Optional[bool] = None,
        has_children: Optional[bool] = None,
        statuses: Optional[Iterable[str]] = None,
        assignees_all: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        active: "Union[bool, None]" = True,
        has_links: Optional[bool] = None,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> Generator["FolderDict", None, None]:
        """Query folders from server.

        Todos:
            Folder name won't be unique identifier, so we should add
                folder path filtering.

        Notes:
            Filter 'active' don't have direct filter in GraphQl.

        Args:
            project_name (str): Name of project.
            folder_ids (Optional[Iterable[str]]): Folder ids to filter.
            folder_paths (Optional[Iterable[str]]): Folder paths used
                for filtering.
            folder_names (Optional[Iterable[str]]): Folder names used
                for filtering.
            folder_types (Optional[Iterable[str]]): Folder types used
                for filtering.
            parent_ids (Optional[Iterable[str]]): Ids of folder parents.
                Use 'None' if folder is direct child of project.
            folder_path_regex (Optional[str]): Folder path regex used
                for filtering.
            has_products (Optional[bool]): Filter folders with/without
                products. Ignored when None, default behavior.
            has_tasks (Optional[bool]): Filter folders with/without
                tasks. Ignored when None, default behavior.
            has_children (Optional[bool]): Filter folders with/without
                children. Ignored when None, default behavior.
            statuses (Optional[Iterable[str]]): Folder statuses used
                for filtering.
            assignees_all (Optional[Iterable[str]]): Filter by assigness
                on children tasks. Task must have all of passed assignees.
            tags (Optional[Iterable[str]]): Folder tags used
                for filtering.
            active (Optional[bool]): Filter active/inactive folders.
                Both are returned if is set to None.
            has_links (Optional[Literal[IN, OUT, ANY]]): Filter
                representations with IN/OUT/ANY links.
            fields (Optional[Iterable[str]]): Fields to be queried for
                folder. All possible folder fields are returned
                if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Generator[FolderDict, None, None]: Queried folder entities.

        """
        if not project_name:
            return

        filters = {
            "projectName": project_name
        }
        if not _prepare_list_filters(
            filters,
            ("folderIds", folder_ids),
            ("folderPaths", folder_paths),
            ("folderNames", folder_names),
            ("folderTypes", folder_types),
            ("folderStatuses", statuses),
            ("folderTags", tags),
            ("folderAssigneesAll", assignees_all),
        ):
            return

        for filter_key, filter_value in (
            ("folderPathRegex", folder_path_regex),
            ("folderHasProducts", has_products),
            ("folderHasTasks", has_tasks),
            ("folderHasLinks", has_links),
            ("folderHasChildren", has_children),
        ):
            if filter_value is not None:
                filters[filter_key] = filter_value

        if parent_ids is not None:
            parent_ids = set(parent_ids)
            if not parent_ids:
                return
            if None in parent_ids:
                # Replace 'None' with '"root"' which is used during GraphQl
                #   query for parent ids filter for folders without folder
                #   parent
                parent_ids.remove(None)
                parent_ids.add("root")

            if project_name in parent_ids:
                # Replace project name with '"root"' which is used during
                #   GraphQl query for parent ids filter for folders without
                #   folder parent
                parent_ids.remove(project_name)
                parent_ids.add("root")

            filters["parentFolderIds"] = list(parent_ids)

        if not fields:
            fields = self.get_default_fields_for_type("folder")
        else:
            fields = set(fields)
            self._prepare_fields("folder", fields)

        use_rest = False
        if "data" in fields and not self.graphql_allows_data_in_query:
            use_rest = True
            fields = {"id"}

        if active is not None:
            fields.add("active")

        if own_attributes and not use_rest:
            fields.add("ownAttrib")

        query = folders_graphql_query(fields)
        for attr, filter_value in filters.items():
            query.set_variable_value(attr, filter_value)

        for parsed_data in query.continuous_query(self):
            for folder in parsed_data["project"]["folders"]:
                if active is not None and active is not folder["active"]:
                    continue

                if use_rest:
                    folder = self.get_rest_folder(project_name, folder["id"])
                else:
                    self._convert_entity_data(folder)

                if own_attributes:
                    fill_own_attribs(folder)
                yield folder


[docs]    def get_folder_by_id(
        self,
        project_name: str,
        folder_id: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False,
    ) -> Optional["FolderDict"]:
        """Query folder entity by id.

        Args:
            project_name (str): Name of project where to look for queried
                entities.
            folder_id (str): Folder id.
            fields (Optional[Iterable[str]]): Fields that should be returned.
                All fields are returned if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[FolderDict]: Folder entity data or None
                if was not found.

        """
        folders = self.get_folders(
            project_name,
            folder_ids=[folder_id],
            active=None,
            fields=fields,
            own_attributes=own_attributes
        )
        for folder in folders:
            return folder
        return None


[docs]    def get_folder_by_path(
        self,
        project_name: str,
        folder_path: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False,
    ) -> Optional["FolderDict"]:
        """Query folder entity by path.

        Folder path is a path to folder with all parent names joined by slash.

        Args:
            project_name (str): Name of project where to look for queried
                entities.
            folder_path (str): Folder path.
            fields (Optional[Iterable[str]]): Fields that should be returned.
                All fields are returned if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[FolderDict]: Folder entity data or None
                if was not found.

        """
        folders = self.get_folders(
            project_name,
            folder_paths=[folder_path],
            active=None,
            fields=fields,
            own_attributes=own_attributes
        )
        for folder in folders:
            return folder
        return None


[docs]    def get_folder_by_name(
        self,
        project_name: str,
        folder_name: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False,
    ) -> Optional["FolderDict"]:
        """Query folder entity by path.

        Warnings:
            Folder name is not a unique identifier of a folder. Function is
                kept for OpenPype 3 compatibility.

        Args:
            project_name (str): Name of project where to look for queried
                entities.
            folder_name (str): Folder name.
            fields (Optional[Iterable[str]]): Fields that should be returned.
                All fields are returned if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[FolderDict]: Folder entity data or None
                if was not found.

        """
        folders = self.get_folders(
            project_name,
            folder_names=[folder_name],
            active=None,
            fields=fields,
            own_attributes=own_attributes
        )
        for folder in folders:
            return folder
        return None


[docs]    def get_folder_ids_with_products(
        self, project_name: str, folder_ids: Optional[Iterable[str]] = None
    ) -> Set[str]:
        """Find folders which have at least one product.

        Folders that have at least one product should be immutable, so they
        should not change path -> change of name or name of any parent
        is not possible.

        Args:
            project_name (str): Name of project.
            folder_ids (Optional[Iterable[str]]): Limit folder ids filtering
                to a set of folders. If set to None all folders on project are
                checked.

        Returns:
            set[str]: Folder ids that have at least one product.

        """
        if folder_ids is not None:
            folder_ids = set(folder_ids)
            if not folder_ids:
                return set()

        query = folders_graphql_query({"id"})
        query.set_variable_value("projectName", project_name)
        query.set_variable_value("folderHasProducts", True)
        if folder_ids:
            query.set_variable_value("folderIds", list(folder_ids))

        parsed_data = query.query(self)
        folders = parsed_data["project"]["folders"]
        return {
            folder["id"]
            for folder in folders
        }


[docs]    def create_folder(
        self,
        project_name: str,
        name: str,
        folder_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        label: Optional[str] = None,
        attrib: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        status: Optional[str] = None,
        active: Optional[bool] = None,
        thumbnail_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> str:
        """Create new folder.

        Args:
            project_name (str): Project name.
            name (str): Folder name.
            folder_type (Optional[str]): Folder type.
            parent_id (Optional[str]): Parent folder id. Parent is project
                if is ``None``.
            label (Optional[str]): Label of folder.
            attrib (Optional[dict[str, Any]]): Folder attributes.
            data (Optional[dict[str, Any]]): Folder data.
            tags (Optional[Iterable[str]]): Folder tags.
            status (Optional[str]): Folder status.
            active (Optional[bool]): Folder active state.
            thumbnail_id (Optional[str]): Folder thumbnail id.
            folder_id (Optional[str]): Folder id. If not passed new id is
                generated.

        Returns:
            str: Entity id.

        """
        if not folder_id:
            folder_id = create_entity_id()
        create_data = {
            "id": folder_id,
            "name": name,
        }
        for key, value in (
            ("folderType", folder_type),
            ("parentId", parent_id),
            ("label", label),
            ("attrib", attrib),
            ("data", data),
            ("tags", tags),
            ("status", status),
            ("active", active),
            ("thumbnailId", thumbnail_id),
        ):
            if value is not None:
                create_data[key] = value

        response = self.post(
            f"projects/{project_name}/folders",
            **create_data
        )
        response.raise_for_status()
        return folder_id


[docs]    def update_folder(
        self,
        project_name: str,
        folder_id: str,
        name: Optional[str] = None,
        folder_type: Optional[str] = None,
        parent_id: Optional[str] = NOT_SET,
        label: Optional[str] = NOT_SET,
        attrib: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        status: Optional[str] = None,
        active: Optional[bool] = None,
        thumbnail_id: Optional[str] = NOT_SET,
    ):
        """Update folder entity on server.

        Do not pass ``parent_id``, ``label`` amd ``thumbnail_id`` if you don't
            want to change their values. Value ``None`` would unset
            their value.

        Update of ``data`` will override existing value on folder entity.

        Update of ``attrib`` does change only passed attributes. If you want
            to unset value, use ``None``.

        Args:
            project_name (str): Project name.
            folder_id (str): Folder id.
            name (Optional[str]): New name.
            folder_type (Optional[str]): New folder type.
            parent_id (Optional[Union[str, None]]): New parent folder id.
            label (Optional[Union[str, None]]): New label.
            attrib (Optional[dict[str, Any]]): New attributes.
            data (Optional[dict[str, Any]]): New data.
            tags (Optional[Iterable[str]]): New tags.
            status (Optional[str]): New status.
            active (Optional[bool]): New active state.
            thumbnail_id (Optional[Union[str, None]]): New thumbnail id.

        """
        update_data = {}
        for key, value in (
            ("name", name),
            ("folderType", folder_type),
            ("attrib", attrib),
            ("data", data),
            ("tags", tags),
            ("status", status),
            ("active", active),
        ):
            if value is not None:
                update_data[key] = value

        for key, value in (
            ("label", label),
            ("parentId", parent_id),
            ("thumbnailId", thumbnail_id),
        ):
            if value is not NOT_SET:
                update_data[key] = value

        response = self.patch(
            f"projects/{project_name}/folders/{folder_id}",
            **update_data
        )
        response.raise_for_status()


[docs]    def delete_folder(
        self, project_name: str, folder_id: str, force: bool = False
    ):
        """Delete folder.

        Args:
            project_name (str): Project name.
            folder_id (str): Folder id to delete.
            force (Optional[bool]): Folder delete folder with all children
                folder, products, versions and representations.

        """
        url = f"projects/{project_name}/folders/{folder_id}"
        if force:
            url += "?force=true"
        response = self.delete(url)
        response.raise_for_status()


[docs]    def get_tasks(
        self,
        project_name: str,
        task_ids: Optional[Iterable[str]] = None,
        task_names: Optional[Iterable[str]] = None,
        task_types: Optional[Iterable[str]] = None,
        folder_ids: Optional[Iterable[str]] = None,
        assignees: Optional[Iterable[str]] = None,
        assignees_all: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        active: "Union[bool, None]" = True,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> Generator["TaskDict", None, None]:
        """Query task entities from server.

        Args:
            project_name (str): Name of project.
            task_ids (Iterable[str]): Task ids to filter.
            task_names (Iterable[str]): Task names used for filtering.
            task_types (Iterable[str]): Task types used for filtering.
            folder_ids (Iterable[str]): Ids of task parents. Use 'None'
                if folder is direct child of project.
            assignees (Optional[Iterable[str]]): Task assignees used for
                filtering. All tasks with any of passed assignees are
                returned.
            assignees_all (Optional[Iterable[str]]): Task assignees used
                for filtering. Task must have all of passed assignees to be
                returned.
            statuses (Optional[Iterable[str]]): Task statuses used for
                filtering.
            tags (Optional[Iterable[str]]): Task tags used for
                filtering.
            active (Optional[bool]): Filter active/inactive tasks.
                Both are returned if is set to None.
            fields (Optional[Iterable[str]]): Fields to be queried for
                folder. All possible folder fields are returned
                if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Generator[TaskDict, None, None]: Queried task entities.

        """
        if not project_name:
            return

        filters = {
            "projectName": project_name
        }
        if not _prepare_list_filters(
            filters,
            ("taskIds", task_ids),
            ("taskNames", task_names),
            ("taskTypes", task_types),
            ("folderIds", folder_ids),
            ("taskAssigneesAny", assignees),
            ("taskAssigneesAll", assignees_all),
            ("taskStatuses", statuses),
            ("taskTags", tags),
        ):
            return

        if not fields:
            fields = self.get_default_fields_for_type("task")
        else:
            fields = set(fields)
            self._prepare_fields("task", fields, own_attributes)

        use_rest = False
        if "data" in fields and not self.graphql_allows_data_in_query:
            use_rest = True
            fields = {"id"}

        if active is not None:
            fields.add("active")

        query = tasks_graphql_query(fields)
        for attr, filter_value in filters.items():
            query.set_variable_value(attr, filter_value)

        for parsed_data in query.continuous_query(self):
            for task in parsed_data["project"]["tasks"]:
                if active is not None and active is not task["active"]:
                    continue

                if use_rest:
                    task = self.get_rest_task(project_name, task["id"])
                else:
                    self._convert_entity_data(task)

                if own_attributes:
                    fill_own_attribs(task)
                yield task


[docs]    def get_task_by_name(
        self,
        project_name: str,
        folder_id: str,
        task_name: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False,
    ) -> Optional["TaskDict"]:
        """Query task entity by name and folder id.

        Args:
            project_name (str): Name of project where to look for queried
                entities.
            folder_id (str): Folder id.
            task_name (str): Task name
            fields (Optional[Iterable[str]]): Fields that should be returned.
                All fields are returned if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[TaskDict]: Task entity data or None if was not found.

        """
        for task in self.get_tasks(
            project_name,
            folder_ids=[folder_id],
            task_names=[task_name],
            active=None,
            fields=fields,
            own_attributes=own_attributes
        ):
            return task
        return None


[docs]    def get_task_by_id(
        self,
        project_name: str,
        task_id: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> Optional["TaskDict"]:
        """Query task entity by id.

        Args:
            project_name (str): Name of project where to look for queried
                entities.
            task_id (str): Task id.
            fields (Optional[Iterable[str]]): Fields that should be returned.
                All fields are returned if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[TaskDict]: Task entity data or None if was not found.

        """
        for task in self.get_tasks(
            project_name,
            task_ids=[task_id],
            active=None,
            fields=fields,
            own_attributes=own_attributes
        ):
            return task
        return None


[docs]    def get_tasks_by_folder_paths(
        self,
        project_name: str,
        folder_paths: Iterable[str],
        task_names: Optional[Iterable[str]] = None,
        task_types: Optional[Iterable[str]] = None,
        assignees: Optional[Iterable[str]] = None,
        assignees_all: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        active: "Union[bool, None]" = True,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> Dict[str, List["TaskDict"]]:
        """Query task entities from server by folder paths.

        Args:
            project_name (str): Name of project.
            folder_paths (list[str]): Folder paths.
            task_names (Iterable[str]): Task names used for filtering.
            task_types (Iterable[str]): Task types used for filtering.
            assignees (Optional[Iterable[str]]): Task assignees used for
                filtering. All tasks with any of passed assignees are
                returned.
            assignees_all (Optional[Iterable[str]]): Task assignees used
                for filtering. Task must have all of passed assignees to be
                returned.
            statuses (Optional[Iterable[str]]): Task statuses used for
                filtering.
            tags (Optional[Iterable[str]]): Task tags used for
                filtering.
            active (Optional[bool]): Filter active/inactive tasks.
                Both are returned if is set to None.
            fields (Optional[Iterable[str]]): Fields to be queried for
                folder. All possible folder fields are returned
                if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Dict[str, List[TaskDict]]: Task entities by
                folder path.

        """
        folder_paths = set(folder_paths)
        if not project_name or not folder_paths:
            return {}

        filters = {
            "projectName": project_name,
            "folderPaths": list(folder_paths),
        }
        if not _prepare_list_filters(
            filters,
            ("taskNames", task_names),
            ("taskTypes", task_types),
            ("taskAssigneesAny", assignees),
            ("taskAssigneesAll", assignees_all),
            ("taskStatuses", statuses),
            ("taskTags", tags),
        ):
            return {}

        if not fields:
            fields = self.get_default_fields_for_type("task")
        else:
            fields = set(fields)
            self._prepare_fields("task", fields, own_attributes)

        use_rest = False
        if "data" in fields and not self.graphql_allows_data_in_query:
            use_rest = True
            fields = {"id"}

        if active is not None:
            fields.add("active")

        query = tasks_by_folder_paths_graphql_query(fields)
        for attr, filter_value in filters.items():
            query.set_variable_value(attr, filter_value)

        output = {
            folder_path: []
            for folder_path in folder_paths
        }
        for parsed_data in query.continuous_query(self):
            for folder in parsed_data["project"]["folders"]:
                folder_path = folder["path"]
                for task in folder["tasks"]:
                    if active is not None and active is not task["active"]:
                        continue

                    if use_rest:
                        task = self.get_rest_task(project_name, task["id"])
                    else:
                        self._convert_entity_data(task)

                    if own_attributes:
                        fill_own_attribs(task)
                    output[folder_path].append(task)
        return output


[docs]    def get_tasks_by_folder_path(
        self,
        project_name: str,
        folder_path: str,
        task_names: Optional[Iterable[str]] = None,
        task_types: Optional[Iterable[str]] = None,
        assignees: Optional[Iterable[str]] = None,
        assignees_all: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        active: "Union[bool, None]" = True,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> List["TaskDict"]:
        """Query task entities from server by folder path.

        Args:
            project_name (str): Name of project.
            folder_path (str): Folder path.
            task_names (Iterable[str]): Task names used for filtering.
            task_types (Iterable[str]): Task types used for filtering.
            assignees (Optional[Iterable[str]]): Task assignees used for
                filtering. All tasks with any of passed assignees are
                returned.
            assignees_all (Optional[Iterable[str]]): Task assignees used
                for filtering. Task must have all of passed assignees to be
                returned.
            statuses (Optional[Iterable[str]]): Task statuses used for
                filtering.
            tags (Optional[Iterable[str]]): Task tags used for
                filtering.
            active (Optional[bool]): Filter active/inactive tasks.
                Both are returned if is set to None.
            fields (Optional[Iterable[str]]): Fields to be queried for
                folder. All possible folder fields are returned
                if 'None' is passed.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        """
        return self.get_tasks_by_folder_paths(
            project_name,
            [folder_path],
            task_names,
            task_types=task_types,
            assignees=assignees,
            assignees_all=assignees_all,
            statuses=statuses,
            tags=tags,
            active=active,
            fields=fields,
            own_attributes=own_attributes
        )[folder_path]


[docs]    def get_task_by_folder_path(
        self,
        project_name: str,
        folder_path: str,
        task_name: str,
        fields: Optional[Iterable[str]] = None,
        own_attributes: bool = False
    ) -> Optional["TaskDict"]:
        """Query task entity by folder path and task name.

        Args:
            project_name (str): Project name.
            folder_path (str): Folder path.
            task_name (str): Task name.
            fields (Optional[Iterable[str]]): Task fields that should
                be returned.
            own_attributes (Optional[bool]): Attribute values that are
                not explicitly set on entity will have 'None' value.

        Returns:
            Optional[TaskDict]: Task entity data or None if was not found.

        """
        for task in self.get_tasks_by_folder_path(
            project_name,
            folder_path,
            active=None,
            task_names=[task_name],
            fields=fields,
            own_attributes=own_attributes,
        ):
            return task
        return None


[docs]    def create_task(
        self,
        project_name: str,
        name: str,
        task_type: str,
        folder_id: str,
        label: Optional[str] = None,
        assignees: Optional[Iterable[str]] = None,
        attrib: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        active: Optional[bool] = None,
        thumbnail_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> str:
        """Create new task.

        Args:
            project_name (str): Project name.
            name (str): Folder name.
            task_type (str): Task type.
            folder_id (str): Parent folder id.
            label (Optional[str]): Label of folder.
            assignees (Optional[Iterable[str]]): Task assignees.
            attrib (Optional[dict[str, Any]]): Task attributes.
            data (Optional[dict[str, Any]]): Task data.
            tags (Optional[Iterable[str]]): Task tags.
            status (Optional[str]): Task status.
            active (Optional[bool]): Task active state.
            thumbnail_id (Optional[str]): Task thumbnail id.
            task_id (Optional[str]): Task id. If not passed new id is
                generated.

        Returns:
            str: Task id.

        """
        if not task_id:
            task_id = create_entity_id()
        create_data = {
            "id": task_id,
            "name": name,
            "taskType": task_type,
            "folderId": folder_id,
        }
        for key, value in (
            ("label", label),
            ("attrib", attrib),
            ("data", data),
            ("tags", tags),
            ("status", status),
            ("assignees", assignees),
            ("active", active),
            ("thumbnailId", thumbnail_id),
        ):
            if value is not None:
                create_data[key] = value

        response = self.post(
            f"projects/{project_name}/tasks",
            **create_data
        )
        response.raise_for_status()
        return task_id


[docs]    def update_task(
        self,
        project_name: str,
        task_id: str,
        name: Optional[str] = None,
        task_type: Optional[str] = None,
        folder_id: Optional[str] = None,
        label: Optional[str] = NOT_SET,
        assignees: Optional[List[str]] = None,
        attrib: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        active: Optional[bool] = None,
        thumbnail_id: Optional[str] = NOT_SET,
    ):
        """Update task entity on server.

        Do not pass ``label`` amd ``thumbnail_id`` if you don't
            want to change their values. Value ``None`` would unset
            their value.

        Update of ``data`` will override existing value on folder entity.

        Update of ``attrib`` does change only passed attributes. If you want
            to unset value, use ``None``.

        Args:
            project_name (str): Project name.
            task_id (str): Task id.
            name (Optional[str]): New name.
            task_type (Optional[str]): New task type.
            folder_id (Optional[str]): New folder id.
            label (Optional[Union[str, None]]): New label.
            assignees (Optional[str]): New assignees.
            attrib (Optional[dict[str, Any]]): New attributes.
            data (Optional[dict[str, Any]]): New data.
            tags (Optional[Iterable[str]]): New tags.
            status (Optional[str]): New status.
            active (Optional[bool]): New active state.
            thumbnail_id (Optional[Union[str, None]]): New thumbnail id.

        """
        update_data = {}
        for key, value in (
            ("name", name),
            ("taskType", task_type),
            ("folderId", folder_id),
            ("assignees", assignees),
            ("attrib", attrib),
            ("data", data),
            ("tags", tags),
            ("status", status),
            ("active", active),
        ):
            if value is not None:
                update_data[key] = value

        for key, value in (
            ("label", label),
            ("thumbnailId", thumbnail_id),
        ):
            if value is not NOT_SET:
                update_data[key] = value

        response = self.patch(
            f"projects/{project_name}/tasks/{task_id}",
            **update_data
        )
        response.raise_for_status()


[docs]    def delete_task(self, project_name: str, task_id: str):
        """Delete task.

        Args:
            project_name (str): Project name.
            task_id (str): Task id to delete.

        """
        response = self.delete(
            f"projects/{project_name}/tasks/{task_id}"
        )
        response.raise_for_status()



[docs]    def get_users(
        self,
        project_name: Optional[str] = None,
        usernames: Optional[Iterable[str]] = None,
        fields: Optional[Iterable[str]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Get Users.

        Only administrators and managers can fetch all users. For other users
            it is required to pass in 'project_name' filter.

        Args:
            project_name (Optional[str]): Project name.
            usernames (Optional[Iterable[str]]): Filter by usernames.
            fields (Optional[Iterable[str]]): Fields to be queried
                for users.

        Returns:
            Generator[dict[str, Any]]: Queried users.

        """
        filters = {}
        if usernames is not None:
            usernames = set(usernames)
            if not usernames:
                return
            filters["userNames"] = list(usernames)

        if project_name is not None:
            filters["projectName"] = project_name

        if not fields:
            fields = self.get_default_fields_for_type("user")

        query = users_graphql_query(set(fields))
        for attr, filter_value in filters.items():
            query.set_variable_value(attr, filter_value)

        for parsed_data in query.continuous_query(self):
            for user in parsed_data["users"]:
                user["accessGroups"] = json.loads(
                    user["accessGroups"])
                yield user


[docs]    def get_user_by_name(
        self,
        username: str,
        project_name: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get user by name using GraphQl.

        Only administrators and managers can fetch all users. For other users
            it is required to pass in 'project_name' filter.

        Args:
            username (str): Username.
            project_name (Optional[str]): Define scope of project.
            fields (Optional[Iterable[str]]): Fields to be queried
                for users.

        Returns:
            Union[dict[str, Any], None]: User info or None if user is not
                found.

        """
        if not username:
            return None

        for user in self.get_users(
            project_name=project_name,
            usernames={username},
            fields=fields,
        ):
            return user
        return None


[docs]    def get_user(
        self, username: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get user info using REST endpoit.

        Args:
            username (Optional[str]): Username.

        Returns:
            Optional[Dict[str, Any]]: User info or None if user is not
                found.

        """
        if username is None:
            output = self._get_user_info()
            if output is None:
                raise UnauthorizedError("User is not authorized.")
            return output

        response = self.get(f"users/{username}")
        response.raise_for_status()
        return response.data


    def get_schemas(self) -> Dict[str, Any]:
        """Get components schema.

        Name of components does not match entity type names e.g. 'project' is
        under 'ProjectModel'. We should find out some mapping. Also, there
        are properties which don't have information about reference to object
        e.g. 'config' has just object definition without reference schema.

        Returns:
            dict[str, Any]: Component schemas.

        """
        server_schema = self.get_server_schema()
        return server_schema["components"]["schemas"]


[docs]    def get_attributes_schema(
        self, use_cache: bool = True
    ) -> "AttributesSchemaDict":
        if not use_cache:
            self.reset_attributes_schema()

        if self._attributes_schema is None:
            result = self.get("attributes")
            result.raise_for_status()
            self._attributes_schema = result.data
        return copy.deepcopy(self._attributes_schema)


[docs]    def reset_attributes_schema(self):
        self._attributes_schema = None
        self._entity_type_attributes_cache = {}


[docs]    def set_attribute_config(
        self,
        attribute_name: str,
        data: "AttributeSchemaDataDict",
        scope: List["AttributeScope"],
        position: Optional[int] = None,
        builtin: bool = False,
    ):
        if position is None:
            attributes = self.get("attributes").data["attributes"]
            origin_attr = next(
                (
                    attr for attr in attributes
                    if attr["name"] == attribute_name
                ),
                None
            )
            if origin_attr:
                position = origin_attr["position"]
            else:
                position = len(attributes)

        response = self.put(
            f"attributes/{attribute_name}",
            data=data,
            scope=scope,
            position=position,
            builtin=builtin
        )
        if response.status_code != 204:
            # TODO raise different exception
            raise ValueError(
                f"Attribute \"{attribute_name}\" was not created/updated."
                f" {response.detail}"
            )

        self.reset_attributes_schema()


[docs]    def remove_attribute_config(self, attribute_name: str):
        """Remove attribute from server.

        This can't be un-done, please use carefully.

        Args:
            attribute_name (str): Name of attribute to remove.

        """
        response = self.delete(f"attributes/{attribute_name}")
        response.raise_for_status(
            f"Attribute \"{attribute_name}\" was not created/updated."
            f" {response.detail}"
        )

        self.reset_attributes_schema()


[docs]    def get_attributes_for_type(
        self, entity_type: "AttributeScope"
    ) -> Dict[str, "AttributeSchemaDict"]:
        """Get attribute schemas available for an entity type.

        Example::

            ```
            # Example attribute schema
            {
                # Common
                "type": "integer",
                "title": "Clip Out",
                "description": null,
                "example": 1,
                "default": 1,
                # These can be filled based on value of 'type'
                "gt": null,
                "ge": null,
                "lt": null,
                "le": null,
                "minLength": null,
                "maxLength": null,
                "minItems": null,
                "maxItems": null,
                "regex": null,
                "enum": null
            }
            ```

        Args:
            entity_type (str): Entity type for which should be attributes
                received.

        Returns:
            dict[str, dict[str, Any]]: Attribute schemas that are available
                for entered entity type.

        """
        attributes = self._entity_type_attributes_cache.get(entity_type)
        if attributes is None:
            attributes_schema = self.get_attributes_schema()
            attributes = {}
            for attr in attributes_schema["attributes"]:
                if entity_type not in attr["scope"]:
                    continue
                attr_name = attr["name"]
                attributes[attr_name] = attr["data"]

            self._entity_type_attributes_cache[entity_type] = attributes

        return copy.deepcopy(attributes)


[docs]    def get_attributes_fields_for_type(
        self, entity_type: "AttributeScope"
    ) -> Set[str]:
        """Prepare attribute fields for entity type.

        Returns:
            set[str]: Attributes fields for entity type.

        """
        attributes = self.get_attributes_for_type(entity_type)
        return {
            f"attrib.{attr}"
            for attr in attributes
        }


[docs]    def get_default_fields_for_type(self, entity_type: str) -> Set[str]:
        """Default fields for entity type.

        Returns most of commonly used fields from server.

        Args:
            entity_type (str): Name of entity type.

        Returns:
            set[str]: Fields that should be queried from server.

        """
        # Event does not have attributes
        if entity_type == "event":
            return set(DEFAULT_EVENT_FIELDS)

        if entity_type == "activity":
            return set(DEFAULT_ACTIVITY_FIELDS)

        if entity_type == "project":
            entity_type_defaults = set(DEFAULT_PROJECT_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "folder":
            entity_type_defaults = set(DEFAULT_FOLDER_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "task":
            entity_type_defaults = set(DEFAULT_TASK_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "product":
            entity_type_defaults = set(DEFAULT_PRODUCT_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "version":
            entity_type_defaults = set(DEFAULT_VERSION_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "representation":
            entity_type_defaults = (
                DEFAULT_REPRESENTATION_FIELDS
                | REPRESENTATION_FILES_FIELDS
            )
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "folderType":
            entity_type_defaults = set(DEFAULT_FOLDER_TYPE_FIELDS)

        elif entity_type == "taskType":
            entity_type_defaults = set(DEFAULT_TASK_TYPE_FIELDS)

        elif entity_type == "productType":
            entity_type_defaults = set(DEFAULT_PRODUCT_TYPE_FIELDS)

        elif entity_type == "workfile":
            entity_type_defaults = set(DEFAULT_WORKFILE_INFO_FIELDS)
            if not self.graphql_allows_data_in_query:
                entity_type_defaults.discard("data")

        elif entity_type == "user":
            entity_type_defaults = set(DEFAULT_USER_FIELDS)

        else:
            raise ValueError(f"Unknown entity type \"{entity_type}\"")
        return (
            entity_type_defaults
            | self.get_attributes_fields_for_type(entity_type)
        )
