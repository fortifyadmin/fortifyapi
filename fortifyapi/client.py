from .exceptions import *
from .template import *
from .query import *
from .api import *


class FortifySSCClient:

    def __init__(self, url, auth):
        self._url = url
        self._auth = auth
        self._api = FortifySSCAPI(url, auth)

        self.projects = Project(self._api, None, self)
        self.jobs = CloudJob(self._api, None, self)
        self.reports = Report(self._api, None, self)

    def _list(self, endpoint, **kwargs):
        with self._api as api:
            for e in api.page_data(endpoint, **kwargs):
                yield e

    def list_engine_types(self, **kwargs):
        for e in self._list('/api/v1/engineTypes', **kwargs):
            yield Engine(self._api, e, self)

    def Project(self, obj=None):
        # why do i have this? unit tests use it only?...
        return Project(self._api, obj)


class SSCObject(dict):
    def __init__(self, api, obj=None, parent=None):
        super().__init__(obj if obj else {})
        self._api = api
        self.parent = parent

    def __str__(self):
        return f"{self.__class__}({super().__str__()})"


class Project(SSCObject):

    def __init__(self, api, obj=None, parent=None):
        super().__init__(api, obj, parent)
        self.versions = Version(api, None, self)

    def list(self, **kwargs):
        with self._api as api:
            for e in api.page_data('/api/v1/projects', **kwargs):
                yield Project(self._api, e, self.parent)

    def test(self, application_name):
        """
        Check whether the specified application name is already defined in the system
        :returns: If the application_name was found
        :rtype: bool
        """
        with self._api as api:
            return api.post(f"/api/v1/projects/action/test", applicationName=application_name)['data']['found']

    def get(self, id):
        """
        Get the given project by id
        :param id:
        :return: pyssc.Project
        """
        with self._api as api:
            return Project(self._api, api.get(f"/api/v1/projects/{id}")['data'], self.parent)

    def update(self):
        with self._api as api:
            return Project(self._api, api.put(f"/api/v1/projects/{self['id']}", self)['data'], self)

    def create(self, project_name, version_name, project_id=None, description="", active=True,
               commited=False, issue_template_id='Prioritized-HighRisk-Project-Template',
               template=DefaultVersionTemplate):
        """

        :param project_name:
        :param version_name:
        :param project_id:
        :param description:
        :param active:
        :param commited:
        :param issue_template_id:
        :param template:
        :return: Returns the Version object
        :rtype: pyssc.Version
        """
        with self._api as api:
            r = api.post(f"/api/v1/projectVersions", {
                'name': version_name,
                'description': description,
                'active': active,
                'commited': commited,
                'project': {
                    'id': project_id,  # if this is None it will create the project
                    'name': project_name,
                    'description': description,
                    'issueTemplateId': issue_template_id
                },
                'issueTemplateId': issue_template_id
            })
            v = Version(self._api, r['data'], self)
            v.initialize(template=template)
            return v

    def upsert(self, project_name, version_name, description="", active=True,
               commited=False, issue_template_id='Prioritized-HighRisk-Project-Template',
               template=DefaultVersionTemplate):
        """ same as create but uses existing project and version"""
        # see if the project exists
        q = Query().query("name", project_name)
        projects = list(self.list(q=q))
        if len(projects) == 0:
            return self.create(project_name, version_name, description=description, active=active, commited=commited,
                        issue_template_id=issue_template_id, template=template)
        else:
            # should be the first one
            project = projects[0]
            # but check if the version is there...
            for v in project.versions.list():
                print(f"name {v['name']}")
                if v['name'] == version_name:
                    print('found it')
                    print(v)
                    return v
            return self.create(project_name, version_name, project_id=project['id'], description=description, active=active,
                        commited=commited, issue_template_id=issue_template_id, template=template)

    def delete(self):
        # delete every version and project will delete
        for v in self.versions.list():
            v.delete()


class Version(SSCObject):

    def __init__(self, api, obj, parent):
        super().__init__(api, obj, parent)
        self.attributes = Attribute(api, obj, self)

    def initialize(self, template=DefaultVersionTemplate):
        """
        Called automatically when Version.create is called.

        :return:
        """
        with self._api as api:
            temp = template(api, self['id'])
            return api.bulk_request(temp.generate())

    def create(self, version_name, description="", active=True, commited=False, template=DefaultVersionTemplate):
        """ Creates a version for the CURRENT project """
        if not self._obj:
            raise Exception("Cannot create version for empty project - consider using `create_project_version`")
        return self.parent.create(self.parent['name'], version_name, description=description, active=active,
                           commited=commited, project_id=self.parent['id'],
                           issue_template_id=self.parent['issueTemplateId'], template=template)

    def list(self, **kwargs):
        if not self.parent:
            raise ParentNotFoundException("No project parent found to query versions from")
        with self._api as api:
            for e in api.page_data(f"/api/v1/projects/{self.parent['id']}/versions", **kwargs):
                yield Version(self._api, e, self.parent)

    def get(self, id):
        with self._api as api:
            return Version(self._api, api.get(f"/api/v1/projectVersions/{id}")['data'], self.parent)

    def delete(self):
        """ Delete the current version """
        with self._api as api:
            return api.delete(f"/api/v1/projectVersions/{self['id']}")

    def get_processing_rules(self, **kwargs):
        with self._api as api:
            return api.get(f"/api/v1/projectVersions/{self['id']}/resultProcessingRules", **kwargs)

    def set_processing_rules(self, rules):
        with self._api as api:
            return api.put(f"/api/v1/projectVersions/{self['id']}/resultProcessingRules", rules)

    def issue_summary(self, series_type='DEFAULT', group_axis_type='ISSUE_FOLDER'):
        with self._api as api:
            return api.get(f"/api/v1/projectVersions/{self['id']}/issueSummaries",
                           seriestype=series_type,
                           groupaxistype=group_axis_type)['data']


class Engine(SSCObject):
    pass


class CloudJob(SSCObject):

    def list(self, **kwargs):
        with self._api as api:
            for e in api.page_data(f"/api/v1/cloudjobs", **kwargs):
                yield CloudJob(self._api, e, self.parent)

    def get(self, jobToken):
        with self._api as api:
            return CloudJob(self._api, api.get(f"/api/v1/cloudjobs/{jobToken}"), self.parent)['data']

    def cancel(self):
        with self._api as api:
            return api.post(f"/api/v1/cloudjobs/action/cancel", jobTokens=[self['jobToken']])


class Scan(SSCObject):

    def get(self, id):
        f"/api/v1/scans/{id}" # GET


class Artifact(SSCObject):

    def get(self, id):
        f"/api/v1/artifacts/{id}" # GET

    def delete(self, id):
        f"/api/v1/artifacts/{id}" # DELETE

    def approve(self):
        f"/api/v1/artifacts/action/approve" # POST

    def purge(self):
        f"/api/v1/artifacts/action/purge" # POST


class Issue(SSCObject):
    pass


class Attachment(SSCObject):

    def list(self, **kwargs):
        with self._api as api:
            for e in api.page_data(f"/api/v1/issues/{self.id}/attachments", **kwargs):
                yield Attachment(self._api, e)

    def get(self, id):
        f"/api/v1/projectVersions/{self.id}/attributes/{id}" # GET

    def update(self):
        f"/api/v1/projectVersions/{self.parent.id}/attributes/{self.id}" # UPDATE

    def delete(self, id):
        f"/api/v1/projectVersions/{self.parent.id}/attributes/{self.id}" # UPDATE

    def upload(self):
        f"/api/v1/issues/{self.id}/attachments" # POST

    def delete_all(self):
        f"/api/v1/issues/{self.parent.id}/attachments" # DELETE


class Attribute(SSCObject):

    def list(self, **kwargs):
        with self._api as api:
            for e in api.page_data(f"/api/v1/projectVersions/{self['id']}/attributes", **kwargs):
                yield Attribute(self._api, e, self.parent)

    def get(self, id):
        f"/api/v1/projectVersions/{self['id']}/attributes/{id}" # GET
        pass

    def create(self):
        f"/api/v1/projectVersions/{self['id']}/attributes" # POST
        pass

    def update(self):
        f"/api/v1/projectVersions/{self['id']}/attributes" # PUT
        pass


class Report(SSCObject):

    def list(self, **kwargs):
        with self._api as api:
            for e in api.page_data(f"/api/v1/reports", **kwargs):
                yield Report(self._api, e, self.parent)

    def get(self, id):
        f"/api/v1/reports/{id}"
        pass

    def create(self):
        f"/api/v1/reports" # POST
        pass

    def delete(self):
        """ Delete the current report """
        with self._api as api:
            return api.delete(f"/api/v1/reports/{self['id']}")




