"""
    project.py
"""


class Project(object):
    def __init__(self, uuid, parent=None, name=None, description=None):
        self._uuid = uuid
        self._parent = parent
        self._name = name
        self._description = description

    def __repr__(self):
        return "Project %s" % (self._uuid)

    def get_uuid(self):
        return self._uuid

    def get_parent(self):
        return self._parent

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description


class Projects(object):
    """Module for managing projects.

    """

    REST_ENDPOINT_PREFIX = '/project'

    def __init__(self, rest):
        self._rest = rest

    def __repr__(self):
        return "Projects module"

    def _get_projects(self):
        code, response = self._rest.get(self.REST_ENDPOINT_PREFIX)

        if code != 200:
            raise RuntimeError("Server status code: %s; Response: %s" % (code, response))

        return response['items']

    def get_sub_projects(self, parent):
        # For now, this just filters the returned values by parent project. We may eventually
        # choose to implement this server-side, in which case we will call into whatever API
        # that exposes.
        return [p for p in self.get_projects() if p.get_parent() == parent]

    def get_projects(self):
        """Gets projects that the current user has access to read.

        Returns:
            list(Project): a list of Projects.

        Raises:
            RuntimeError if the server returns a non-200.
        """
        projects = []
        for p in self._get_projects():
            project = Project(p['uuid'], p.get('parent'), p.get('name'), p.get('description'))
            projects.append(project)

        return projects

    def get_project(self, uuid) -> Project:
        """Gets project details.

        Args:
            uuid (str): the id of the project to get.

        Returns:
            Project: the newly-created Project.

        Raises:
            RuntimeError if the server returns a non-200.
        """
        if uuid is None:
            raise KeyError("Project id is required.")

        code, response = self._rest.get(f'{self.REST_ENDPOINT_PREFIX}/{uuid}')

        if code == 404:
            return None
        elif code != 200:
            raise RuntimeError("Server status code: %s; Response: %s" % (code, response))

        return Project(uuid,
                       response.get('parent'),
                       response.get('name'),
                       response.get('description'))

    def new_project(self, parent, name, description) -> Project:
        """Creates a new project.

        Args:
            parent (str): the parent project id.
            name (str): the name of the project.
            description (str): the description of this project.

        Returns:
            Project: the newly-created Project.

        Raises:
            RuntimeError if the server returns a non-200.
        """
        code, response = self._rest.post(
            self.REST_ENDPOINT_PREFIX,
            {'parent': parent, 'name': name, 'description': description})

        if code != 200:
            raise RuntimeError("Server status code: %s; Response: %s" % (code, response))

        return Project(response['uuid'], parent, name, description)

    def delete_project(self, uuid):
        """Deletes a project.

        Args:
            uuid (str): the id of the project to delete.

        Raises:
            RuntimeError if the server returns a non-204.
        """
        code = self._rest.delete(f'{self.REST_ENDPOINT_PREFIX}/{uuid}')

        if code != 204:
            raise RuntimeError("Server status code: %s" % (code))
