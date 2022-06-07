#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Brandon Spruth (brandon@spruth.co)"
__contributors__ = ["Brandon Spruth"]
__status__ = "Production"
__license__ = "MIT"

import urllib3
import json
import ntpath
import requests
import requests.auth
import requests.exceptions
import urllib.parse
from . import __version__ as version


class FortifyApi(object):
    def __init__(self, host, username=None, password=None, token=None, verify_ssl=True, timeout=60, user_agent=None,
                 client_version='21.10'):

        self.host = host
        self.username = username
        self.password = password
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.client_version = client_version

        if not user_agent:
            self.user_agent = 'fortify_api/' + version
        else:
            self.user_agent = user_agent

        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Set auth_type based on what's been provided
        if username is not None:
            self.auth_type = 'basic'
        elif token is not None:
            self.auth_type = 'token'
        else:
            self.auth_type = 'unauthenticated'

    def bulk_create_new_application_version_request(self, version_id, development_phase, development_strategy,
                                                    accessibility, business_risk_ranking, custom_attributes=[]):
        """
        Creates a new Application Version by using the Bulk Request API. 'create_new_project_version' must be used
        before calling this method.
        :param version_id: Version ID
        :param development_phase: Development Phase GUID of Version
        :param development_strategy: Development Strategy GUID of Version
        :param accessibility: Accessibility GUID of Version
        :param business_risk_ranking: Business Risk Rank GUID of Version
        :param custom_attributse: List of custom Attribute tuples that consist of attributeDefinitionId, values, & value. 
                                  Default is a empty string tuple.
        :return: A response object containing the newly created project and project version
        """
        data = self._bulk_format_new_application_version_payload(version_id=version_id,
                                                                 development_phase=development_phase,
                                                                 development_strategy=development_strategy,
                                                                 accessibility=accessibility,
                                                                 business_risk_ranking=business_risk_ranking,
                                                                 custom_attributes=custom_attributes)
        url = '/api/v1/bulk'
        return self._request('POST', url, data=data)

    @staticmethod
    def _bulk_format_attribute_definition(attribute_definition_id_value, guid_value='', value='null'):
        json_application_version = dict(attributeDefinitionId=attribute_definition_id_value,
                                        values=[],
                                        value=value)
        if guid_value is not None:
            json_application_version['values'] = [dict(guid=guid_value)]
        return json_application_version

    def _bulk_format_new_application_version_payload(self, version_id, development_phase, development_strategy,
                                                     accessibility, business_risk_ranking, custom_attributes):
        json_application_version = dict(requests=[
            self._bulk_create_attributes(version_id, development_phase, development_strategy, accessibility,
                                         business_risk_ranking, custom_attributes),
            self._bulk_create_responsibilities(version_id),
            self._bulk_create_configurations(version_id),
            self._bulk_create_commit(version_id),
            self._bulk_create_version(version_id)
        ])
        return json.dumps(json_application_version)

    def _bulk_create_attributes(self, version_id, development_phase, development_strategy,
                                accessibility, business_risk_ranking, custom_attributes):
        if business_risk_ranking is None:
            business_risk_ranking = 'High'
        json_application_version = dict(
            uri=self.host + '/api/v1/projectVersions/' + str(version_id) + '/attributes',
            httpVerb='PUT',
            postData=[
                self._bulk_format_attribute_definition('5', development_phase),
                self._bulk_format_attribute_definition('6', development_strategy),
                self._bulk_format_attribute_definition('7', accessibility),
                self._bulk_format_attribute_definition('1', business_risk_ranking),
            ])
        for a in custom_attributes:
            guid_value = a[1]
            if guid_value == "":
                guid_value = None
            json_application_version['postData'].append(
                self._bulk_format_attribute_definition(
                    attribute_definition_id_value=a[0],
                    guid_value=guid_value,
                    value=a[2]))

        return json_application_version

    def _bulk_create_responsibilities(self, version_id):
        json_application_version = dict(
            uri=self.host + '/api/v1/projectVersions/' + str(version_id) + '/responsibilities',
            httpVerb='PUT',
            postData=[]
        )
        json_application_version['postData'] = [dict(responsibilityGuid='projectmanager',
                                                     userId='null'),
                                                dict(responsibilityGuid='securitychampion',
                                                     userId='null'),
                                                dict(responsibilityGuid='developmentmanager',
                                                     userId='null'),
                                                ]
        return json_application_version

    def _bulk_create_configurations(self, version_id):
        json_application_version = dict(uri=self.host + '/api/v1/projectVersions/' + str(version_id) + '/action',
                                        httpVerb='POST',
                                        postData=[dict(
                                            type='COPY_FROM_PARTIAL',
                                            values={
                                                "projectVersionId": str(version_id),
                                                "previousProjectVersionId": '-1',
                                                "copyAnalysisProcessingRules": 'true',
                                                "copyBugTrackerConfiguration": 'true',
                                                "copyCurrentStateFpr": 'false',
                                                "copyCustomTags": 'true'
                                            }
                                        )]
                                        )
        return json_application_version

    def _bulk_create_commit(self, version_id):
        json_application_version = dict(
            uri=self.host + '/api/v1/projectVersions/' + str(version_id),
            httpVerb='PUT',
            postData={
                "committed": 'true'
            }
        )
        return json_application_version

    def _bulk_create_version(self, version_id):
        json_application_version = dict(uri=self.host + '/api/v1/projectVersions/' + str(version_id) + '/action',
                                        httpVerb='POST',
                                        postData=[dict(
                                            type='COPY_CURRENT_STATE',
                                            values={
                                                "projectVersionId": str(version_id),
                                                "previousProjectVersionId": '-1',
                                                "copyCurrentStateFpr": 'false'
                                            }
                                        )]
                                        )
        return json_application_version

    def set_processing_rules(self, version_id):
        """
        :param version_id: SSC Project Version to modify
        :return: A response object changing all required processing default fields from true to false
        """
        data = [
            {"identifier": "com.fortify.manager.BLL.processingrules.BuildProjectProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.ExternalListVersionProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.FileCountProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.ForceMigrationProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.FortifyAnnotationsProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.LOCCountProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.MigrationProcessingRule",
             "enabled": True},
            {"identifier": "com.fortify.manager.BLL.processingrules.NewerEngineVersionProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.QuickScanProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.RulePackVersionProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.ValidCertificationProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.WarningProcessingRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.UnknownOrDisallowedAuditedAttrChecker",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.AuditedAnalysisRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.HiddenTagAuditsAnalysisRule",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.PendingApprovalChecker",
             "enabled": False},
            {"identifier": "com.fortify.manager.BLL.processingrules.VetoCascadingApprovalProcessingRule",
             "enabled": False}
        ]
        url = '/api/v1/projectVersions/' + str(version_id) + '/resultProcessingRules'
        return self._request('PUT', url, json=data)
    
    def get_processing_rules(self, version_id):
        """
        :param version_id: Project Version ID from SSC to query
        :return: Listing of all result processing rules for a given SSC project version
        """
        url = '/api/v1/projectVersions/' + str(version_id) + '/resultProcessingRules'
        return self._request('GET', url)

    def create_application_version(self, application_name, application_template, version_name, description,
                                   application_id=None, issue_template_id=None):
        """
        :param application_name: Project name
        :param application_id: Project ID
        :param application_template: Application template name
        :param version_name: Version name
        :param description: Application Version description
        :param issue_template_id: Optional for when you already know the id you want to use
        :return: A response object containing the created project version
        """
        # If no application ID is given, sets JSON value to null.
        if application_id is None:
            application_id = 'null'

        if issue_template_id is None:
            # Gets Template ID
            issue_template = self.get_issue_template_id(project_template_name=application_template)
            issue_template_id = issue_template.data['data'][0]['id']

        data = dict(name=version_name,
                    description=description,
                    active=True,
                    committed=False,
                    project={
                        'name': application_name,
                        'description': description,
                        'issueTemplateId': issue_template_id,
                        'id': application_id
                    },
                    issueTemplateId=issue_template_id)

        url = '/api/v1/projectVersions'
        return self._request('POST', url, json=data)
    
    def delete_application_version(self, id):
        """
        Delete a given application or project version from SSC
        :param id: Project Version ID
        :return:
        """
        url = "/api/v1/projectVersions/" + str(id)
        return self._request('DELETE', url)
    
    def download_artifact(self, artifact_id):
        """
        You might use this method like this, for example
            api = FortifyApi("https://my-fortify-server:my-port", token=get_token())
            response, file_name = api.download_artifact_scan("my-id")
            if response.success:
                file_content = response.data
                with open('/path/to/some/folder/' + file_name, 'wb') as f:
                    f.write(file_content)
            else:
                print response.message

        We've coded this for the entire file to load into memory. A future change may be to permit
        streaming/chunking of the file and handing back a stream instead of content.
        :param artifact_id: the id of the artifact to download
        :return: binary file data and file name
        """
        file_token = self.get_file_token('DOWNLOAD').data['data']['token']

        url = "/download/artifactDownload.html?mat=" + file_token + "&id=" + str(
            artifact_id) + "&clientVersion=" + self.client_version

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        response = self._request('GET', url, stream=True, headers=headers)

        try:
            file_name = response.headers['Content-Disposition'].split('=')[1].strip("\"'")
        except:
            file_name = ''

        return response, file_name

    def download_artifact_scan(self, artifact_id):
        """
        You might use this method like this, for example
            api = FortifyApi("https://my-fortify-server:my-port", token=get_token())
            response, file_name = api.download_artifact_scan("my-id")
            if response.success:
                file_content = response.data
                with open('/path/to/some/folder/' + file_name, 'wb') as f:
                    f.write(file_content)
            else:
                print response.message

        We've coded this for the entire file to load into memory. A future change may be to permit
        streaming/chunking of the file and handing back a stream instead of content.
        :param artifact_id: the id of the artifact scan to download
        :return: binary file data and file name
        """
        file_token = self.get_file_token('DOWNLOAD').data['data']['token']

        url = "/download/currentStateFprDownload.html?mat=" + file_token + "&id=" + str(
            artifact_id) + "&clientVersion=" + self.client_version + "&includeSource=true"

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        response = self._request('GET', url, stream=True, headers=headers)

        try:
            file_name = response.headers['Content-Disposition'].split('=')[1].strip("\"'")
        except:
            file_name = ''

        return response, file_name

    def get_artifact_scans(self, parent_id):
        """
        :param parent_id: parent resource identifier
        :return: A response object containing artifact scans
        """
        url = "/api/v1/artifacts/" + str(parent_id) + "/scans"
        return self._request('GET', url)

    def get_attribute_definition(self, search_expression):
        """
        :param search_expression: A fortify-formatted search expression, e.g. Development Phase
        :return: A response object containing the result of the GET
        """
        if search_expression:
            url = '/api/v1/attributeDefinitions?q=name:"' + search_expression + '"'
            return self._request('GET', url)
        else:
            return FortifyResponse(message='A search expression must be provided', success=False)

    def get_attribute_definitions(self):
        """
        :return: A response object containing all attribute definitions
        """
        url = '/api/v1/attributeDefinitions?start=0&limit=-1'
        return self._request('GET', url)

    def get_cloudscan_jobs(self):
        """
        :return: A response object containing all cloudscan jobs
        """
        url = '/api/v1/cloudjobs?start=0&limit=-1'
        return self._request('GET', url)

    def get_cloudscan_job_status(self, scan_id):
        """
        :return: A response object containing a cloudscan job
        """
        url = '/api/v1/cloudjobs/' + scan_id
        return self._request('GET', url)

    def set_cloudscan_cancel_job(self, scan_id):
        url = '/api/v1/cloudjobs/' + scan_id + '/action'
        data = (
            {"type": "cancel"}
        )
        return self._request('POST', url, json=data)

    def get_file_token(self, purpose):
        """
        :param purpose: specify if the token is for file 'UPLOAD' or 'DOWNLOAD'
        :return: a response body containing a file token for the specified purpose
        """

        url = "/api/v1/fileTokens"
        if purpose == 'UPLOAD':
            data = (
                {
                    "fileTokenType": "UPLOAD"
                }
            )
        elif purpose == 'DOWNLOAD':
            data = (
                {
                    "fileTokenType": "DOWNLOAD"
                }
            )
        else:
            return FortifyResponse(message='attribute purpose must be either UPLOAD or DOWNLOAD', success=False)

        return self._request('POST', url, json=data)

    def get_issue_template(self, project_template_id):
        """
        :param project_template_id: id of project template
        :return: A response object with data containing issue templates for the supplied project name
        """

        url = "/api/v1/issueTemplates" + "?limit=1&q=id:\"" + project_template_id + "\""
        return self._request('GET', url)

    def get_issue_template_id(self, project_template_name):
        """
        :param project_template_name: name of project template
        :return: A response object with data containing issue templates for the supplied project name
        """

        url = "/api/v1/issueTemplates" + "?limit=1&fields=id&q=name:\"" + project_template_name + "\""
        return self._request('GET', url)

    def get_project_version_artifacts(self, parent_id):
        """
        :param parent_id: parent resource identifier
        :return: A response object containing project version artifacts
        """
        url = "/api/v1/projectVersions/" + str(parent_id) + "/artifacts?start=0&limit=-1"
        return self._request('GET', url)

    def get_project_version_attributes(self, project_version_id):
        """
        :param project_version_id: Project version id
        :return: A response object containing the project version attributes
        """
        url = '/api/v1/projectVersions/' + str(project_version_id) + '/attributes/?start=0&limit=-1'
        return self._request('GET', url)

    def get_all_project_versions(self):
        """
        :return: A response object with data containing project versions
        """
        url = "/api/v1/projectVersions?start=0&limit=-1"
        return self._request('GET', url)

    def get_project_version(self, version_id):
        """
        :version_id: Project Version ID
        :return: Details of a Project Version
        """
        url = "/api/v1/projectVersions/" + version_id
        return self._request('GET', url)
    
    def get_project_versions(self, project_name):
        """
        Implemented on SSC as project-version-controller to manage application versions.
        A variety of associated resources are accessible via links.
        :return: A response object with data containing project versions
        """
        url = "/api/v1/projectVersions?limit=0&q=project.name:\"" + project_name + "\""
        return self._request('GET', url)

    def get_version(self, version_name):
        """
        :return: A response object with data containing just a project's version
        """
        url = "/api/v1/projectVersions?q=name:\"" + version_name + "\""
        return self._request('GET', url)
    
    def set_project_versions_test(self, project_name, project_version_name):
        """
        Check whether the specified application name is already defined in the system
        :param project_name: Application or Project name in SSC you want to test the value of.
        :param project_version_name: Application or Project version you want to test the value of.
        :return: A response object of found for true or false
        """
        data = {
            "projectName": project_name,
            "projectVersionName": project_version_name
        }

        url = "/api/v1/projectVersions/action/test"
        return self._request('POST', url, json=data)

    def set_projects_test(self, application_name):
        """
        Check whether the specified application name is already defined in the system.  For some reason SSC is not
        consistent here on naming conventions between project and application.
        :param application_name: Application or Project name in SSC you want to test the value of.
        :return: A response object of found for true or false
        """
        data = {
            "applicationName": application_name
        }

        url = "/api/v1/projects/action/test"
        return self._request('POST', url, json=data)

    def get_projects_id_from_name(self, project_name):
        """
        Don't want to trust user input here.  Encoding for spaces with + sign and other encoding
        :return: the data object from querying by a Project or Application name
        """

        url = "/api/v1/projects?q=name:" + urllib.parse.quote_plus(project_name)
        return self._request('GET', url)

    def get_projects(self):
        """
        :return: A response object with data containing projects
        """

        url = "/api/v1/projects?start=0&limit=-1"

        return self._request('GET', url)

    def get_token(self, description, type='UnifiedLoginToken'):
        """
        Token types include UnifiedLoginToken, UploadFileTransferToken, DownloadFileTransferToken
        :return: A response object with data containing create date, terminal date, and the actual token
        """
        data = {
            "description": description,
            "type": type
        }

        url = '/api/v1/tokens'
        return self._request('POST', url, json=data)

    def post_attribute_definition(self, attribute_definition):
        """
        :param attribute_definition:
        :return:
        """
        url = '/api/v1/attributeDefinitions'
        return self._request('POST', url, json=attribute_definition)

    def upload_artifact_scan(self, file_path, project_version_id):
        """
        :param file_path: full path to the file to upload
        :param project_version_id: project_version_id
        :return: Response from the file upload operation
        """
        upload = self.get_file_token('UPLOAD')
        if upload is None or upload.data['data'] is None:
            return FortifyResponse(message='Failed to get the SSC upload file token', success=False)

        file_token = upload.data['data']['token']
        url = "/upload/resultFileUpload.html?mat=" + file_token
        files = {'file': (ntpath.basename(file_path), open(file_path, 'rb'))}

        headers = {
            'Accept': 'Accept:application/xml, text/xml, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        params = {
            'entityId': project_version_id,
            'clientVersion': self.client_version,
            'Upload': "Submit Query",
            'Filename': ntpath.basename(file_path)
        }

        return self._request('POST', url, params, files=files, stream=True, headers=headers)

    #TODO change to '/api/v1/coreRulepacks/', "file=@rule.xml;type=text/xml, 'Content-Type': 'multipart/form-data',
    def upload_rulepack(self, file_path):
        """
        Upload rulepack to Fortify SSC
        :param file_path:
        :return:
        """
        upload = self.get_file_token('UPLOAD')
        if upload is None or upload.data['data'] is None:
            return FortifyResponse(message='Failed to get the SSC upload file token', success=False)

        file_token = upload.data['data']['token']
        url = "/upload/rulepackUpload.html?mat=" + file_token
        files = {'file': (ntpath.basename(file_path), open(file_path, 'rb'))}

        headers = {
            'Accept': 'Accept:application/xml, text/xml, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

        params = {
            'clientVersion': self.client_version,
            'Filename': ntpath.basename(file_path)
        }

        return self._request('POST', url, params, files=files, stream=True, headers=headers)

    def delete_token(self, token_id):
        """
        Delete a token by ID from the auth-token-controller
        :param id:
        :return:
        """
        url = "/api/v1/tokens/" + str(token_id)
        return self._request('DELETE', url)

    def delete_all_user_tokens(self):
        """
        Delete all tokens by user from the auth-token-controller
        :return:
        """
        url = '/api/v1/tokens' + '?all=true'
        return self._request('DELETE', url)

    def get_all_tokens(self):
        """
        Get all tokens for all users
        :return:
        """
        url = "/api/v1/tokens?start=0&limit=-1"
        return self._request('GET', url)

    #TODO: fix expire_date to one year out
    def set_token(self, description, token_type, expire_date="2028-12-29T22:40:11.000+0000"):
        """
        Create any type of SSC token required
        :param description:
        :param token_type:
        :return:
        """
        data = {
            "description": description,
            "type": token_type,
            "terminalDate": expire_date
        }

        url = "/api/v1/tokens"
        return self._request('POST', url, json=data)

    def get_all_rulepacks(self):
        """
        List all rules on an SSC instance
        :return:
        """
        url = "/api/v1/coreRulepacks"
        return self._request('GET', url)

    def delete_rulepack(self, rulepack_id):
        """
        Delete a given rulepack by ID
        :param rulepack_id:
        :return:
        """
        url = "/api/v1/coreRulepacks/" + str(rulepack_id)
        return self._request('DELETE', url)

    def update_rulepacks(self):
        """
        Described as a Dolimport, update rulepacks from the public fortify server and return status with rulepacks
        updated.
        Update Fortify Stock Rulepacks
        :return:
        """
        url = "/api/v1/updateRulepacks"
        return self._request('GET', url)

    def get_all_issue_aging(self):
        """
         :return: Get total summary of applicationVersions, averageDaysToRemediate, averageDaysToReview, filesScanned,
         issuesPendingReview, issuesRemediated, linesOfCode, openIssues, openIssuesReviewed
         """
        url = "/api/v1/portlets/issueaging"
        return self._request('GET', url)

    def get_project_version_issues(self, version_id, orderby='friority'):
        """
        Issues per application/project version, with optional orderby query param
        :param version_id:
        :return: a List w/ no Project Version Name
        """
        url = '/api/v1/projectVersions/' + str(version_id) + '/issues?start=0&limit=-1&' + orderby + '&' \
                                                             'showhidden=false&' \
                                                             'showremoved=false&showsuppressed=false&' \
                                                             'showshortfilenames=false'
        return self._request('GET', url)

    def get_project_version_issue_details(self, instance_id, project_name, version_name, engine='SCA'):
        """
        Returns trace analysis and other details of a given issue.  The issue ID can be found from the /issues or
        projectVersions endpoint.
        :param instance_id:
        :param project_name:
        :param version_name:
        :param engine:
        :return: full detail of a given issue
        """
        url = '/api/v1/issueDetails?instanceId=' + str(instance_id) + '&projectName=' + str(project_name) + '&projectVersionName='\
              + str(version_name) + '&engineType=' + str(engine)

        return self._request('GET', url)

    def get_project_version_source_file(self, version_id, path):
        """
        Returns an object with information on a source file from a specific project version.
        It includes the file content.
        :param version_id: application version id
        :param path: the relative path of the file from the project root folder
        :return: details on a source file
        """
        url = f'/api/v1/projectVersions/{version_id}/sourceFiles?q=path:"{path}"'
        return self._request("GET", url)

    def get_cloud_pool_list(self):
        """
        Get listing of all cloud pools
        :return:
        """
        url = '/api/v1/cloudpools'
        return self._request('GET', url)

    def get_cloud_worker_list(self):
        """
        Get listing of all cloud sensors/workers
        :return:
        """
        url = '/api/v1/cloudworkers'
        return self._request('GET', url)

    def set_cloud_pool(self, description, name):
        """
        Creates a cloudscan pool
        :param description:
        :param name:
        :return:
        """
        data = {
            "description": description,
            "name": name
        }
        url = '/api/v1/cloudpools'
        return self._request('POST', url, json=data)

    def set_cloud_worker(self, worker_uuid, pool_id):
        """
        Assignes a cloudscan worker to a pool
        :param pool_id: ID of cloudpool
        :param worker_uuid: uuid from the cloudworker
        :return:
        """
        data = {
                "workerUuids": [str(worker_uuid)]
        }
        url = '/cloudpools/' + pool_id + '/workers/action/assign'
        return self._request('POST', url, json=data)

    def get_all_ldap_users(self):
        """
        List all ldap users
        :return:
        """
        url = '/api/v1/ldapObjects'
        return self._request('GET', url)

    def set_ldap_user(self, distinguished_name, project_version_id):
        """
        Add LDAP user to Fortify SSC
        :return:
        """
        data = {"distinguishedName": distinguished_name,
                "roles": [{"permissionIds": [str(project_version_id)]}]
               }
        url = '/api/v1/ldapObjects'
        return self._request('POST', url, json=data)

    def get_all_auth_entities(self):
        """
        Manage aggregated list of authentication entities (local and LDAP user accounts). LDAP groups can be accessed
        via a linked resource. This controller does not support creation of new accounts. To create new local or LDAP
        user accounts, use the corresponding specific controllers.  In other words Give me a listing of all users local
        or LDAP, for identying the auth_entity_id to be used in get_auth_entity, and set_auth_entity_to_version
        :return:
        """
        url = '/api/v1/authEntities?fulltextsearch=false'
        return self._request('GET', url)

    def get_auth_entity(self, auth_entity_id):
        """
        Manage the association of application versions to the authentication entity (local or LDAP user)
        :param auth_entity_id:
        :return:
        """
        url = '/api/v1/authEntities/' + auth_entity_id + '/projectVersions'
        return self._request('GET', url)

    def modify_auth_entity_to_version(self, auth_entity_id, project_version_id):
        """
        TODO: NOT SURE IF NEEDED
        :param auth_entity_id:
        :param project_version_id:
        :return:
        """
        data = [project_version_id]
        url = '/api/v1/authEntities' + auth_entity_id + 'projectVersions'
        return self._request('PUT', url, json=data)

    def set_auth_entity_to_version(self, auth_entity_id, project_version_id):
        """
        Associate the specified application versions to the authentication entity
        :return:
        """
        data = {"projectVersionIds": [str(project_version_id)]}
        url = '/api/v1/authEntities' + auth_entity_id + 'projectVersions/action/assign'
        return self._request('POST', url, json=data)

    def get_all_auth_entity_of_project_version(self, project_version_id,
                                               extract_users_from_groups=True, include_universal_access_entities=True):
        """
        Retrieve the authentication entities associated with this application version.  What this really means is
        give me the users entitled for a given Project version
        :param project_version_id:
        :return: List all users associated with the Project Version
        """
        url = '/api/v1/projectVersions/' + str(project_version_id) + '/authEntities'
        params = {
            'extractusersfromgroups': extract_users_from_groups,
            'includeuniversalaccessentities': include_universal_access_entities
        }

        return self._request('GET', url, params)
    
    def get_all_bugtrackers(self):
        url = '/api/v1/bugtrackers'
        return self._request('GET', url)
    
    def get_version_bugtracker(self,project_version_id):
        url = '/api/v1/projectVersions/'+str(project_version_id)+'/bugtracker'
        return self._request('GET', url)
    
    def set_version_bugtracker(self,project_version_id,bugtracker_data):
        url = '/api/v1/projectVersions/'+str(project_version_id)+'/bugtracker'
        return self._request('PUT', url,json=bugtracker_data)

    def _request(self, method, url, params=None, files=None, json=None, data=None, headers=None, stream=False):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        if not headers:
            headers = {
                'Accept': 'application/json'
            }
            if method == 'GET' or method == 'POST' or method == 'PUT':
                headers.update({'Content-Type': 'application/json'})
        headers.update({'User-Agent': self.user_agent})

        try:

            if self.auth_type == 'basic':
                response = requests.request(method=method, url=self.host + url, params=params, files=files,
                                            headers=headers, json=json, data=data,
                                            timeout=self.timeout, verify=self.verify_ssl,
                                            auth=(self.username, self.password), stream=stream)
            elif self.auth_type == 'token':
                response = requests.request(method=method, url=self.host + url, params=params, files=files,
                                            headers=headers, json=json, data=data, timeout=self.timeout, 
                                            verify=self.verify_ssl, auth=FortifyTokenAuth(self.token), stream=stream)
            else:
                response = requests.request(method=method, url=self.host + url, params=params, files=files,
                                            headers=headers, json=json, data=data,
                                            timeout=self.timeout, verify=self.verify_ssl, stream=stream)

            try:
                response.raise_for_status()

                # two flavors of response are successful, GETs return 200, PUTs return 204 with empty response text
                response_code = response.status_code
                success = True if response_code // 100 == 2 else False
                if response.text:
                    try:
                        data = response.json()
                    except ValueError:  # Sometimes the returned data isn't JSON, so return raw
                        data = response.content

                return FortifyResponse(success=success, response_code=response_code, data=data,
                                       headers=response.headers)
            except ValueError as e:
                return FortifyResponse(success=False, message="JSON response could not be decoded {0}.".format(e))
        except requests.exceptions.SSLError as e:
            return FortifyResponse(message='An SSL error occurred. {0}'.format(e), success=False)
        except requests.exceptions.ConnectionError as e:
            return FortifyResponse(message='A connection error occurred. {0}'.format(e), success=False)
        except requests.exceptions.Timeout:
            return FortifyResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.',
                                   success=False)
        except requests.exceptions.RequestException as e:
            return FortifyResponse(
                message='There was an error while handling the request. {0}'.format(e), success=False)


class FortifyTokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'FortifyToken ' + self.token
        return r


class FortifyResponse(object):
    """Container for all Fortify SSC API responses, even errors."""

    def __init__(self, success, message='OK', response_code=-1, data=None, headers=None):
        self.message = message
        self.success = success
        self.response_code = response_code
        self.data = data
        self.headers = headers

    def __str__(self):
        if self.data:
            return str(self.data)
        else:
            return self.message

    def data_json(self, pretty=False):
        """Returns the data as a valid JSON string."""
        if pretty:
            return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.data)
