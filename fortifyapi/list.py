#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Brandon Spruth (brandon@spruth.co)"
__contributors__ = ["Brandon Spruth"]
__status__ = "Production"
__license__ = "MIT"

from os import environ
from locale import LC_ALL, setlocale
import pandas as pd
from fortifyapi.fortify import FortifyApi

# Set encoding
environ["PYTHONIOENCODING"] = "utf-8"
myLocale = setlocale(category=LC_ALL, locale="en_US.UTF-8")


class ApplicationVersions:
    def __init__(self, host=None, token=None):
        """
        List all Versions of an Application if an Application was specified. If it was not, it will list all
        Applications & Versions.
        :param host: The scheme + host + path of the ssc instance you are using (i.e. http://localhost:8080/ssc)
        :param host: SSC url with context for example http://localhost:8080/ssc
        :param token: An API token and must always be type UnifiedLoginToken
        :return: All application or project versions
        """
        if host and token is None:
            print("No SSC url or API token has been provided! See also host={} token={}".format(host, token))
        if host and token is not None:
            self.host, self.token = host, token
            self.application_version_list()

    def application_version_list(self):
        api = FortifyApi(host=self.host, token=self.token, verify_ssl=False)
        response = api.get_all_project_versions()
        data = response.data['data']
        for version in data:
            print("{},{},{}".format(version['id'], version['project']['name'], version['name']).encode(
                'utf-8', errors='ignore').decode())


class Findings:
    def __init__(self, host=None, token=None):
        if host and token is None:
            print("No SSC url or API token has been provided! See also host={} token={}".format(host, token))
        if host and token is not None:
            self.host, self.token = host, token
            self.findings_list()

    def get_application_and_versions(self):
        api = FortifyApi(host=self.host, token=self.token, verify_ssl=False)
        response = api.get_all_project_versions()
        return response.data['data']

    def get_project_version_issues(self, vid):
        api =  FortifyApi(host=self.host, token=self.token, verify_ssl=False)
        response = api.get_project_version_issues(str(vid))
        return response.data['data']

    def findings_list(self):
        issues = []
        versions = self.get_application_and_versions()
        for v, i in [(version, issue) for version in versions for issue in
                     self.get_project_version_issues(version['id'])]:
                if v['currentState']['analysisResultsExist'] is True and i['displayEngineType'] == 'SCA':
                    dict = {'IssueInstanceId': i['issueInstanceId'],
                            'Project': str(u''.join((v['project']['name'])).encode('utf-8').strip().decode('UTF-8')),
                            'Version': str(u''.join((v['name'])).encode('utf-8').strip().decode('UTF-8')),
                            'Owner': v['owner'],
                            'CreationDate': v['creationDate'][:-18],
                            'LastFprUploadDate': v['currentState']['lastFprUploadDate'][:-18],
                            'Priority': i['friority'],
                            'IssueName': i['issueName'],
                            'Kingdom': i['kingdom'],
                            'Status': i['scanStatus'],
                            'IssueStatus': i['issueStatus'],
                            'FilePath': i['fullFileName'] + ':' + str(i['lineNumber']),
                            'File': i['primaryLocation'] + ':' + str(i['lineNumber']),
                            'PrimaryRuleGuid': i['primaryRuleGuid'],
                            'Analyzer': i['analyzer'],
                            'FoundDate': i['foundDate'][:-18],
                            'IssueUrl': self.host + '/html/ssc/version/' + str(
                                i['projectVersionId']) + '/fix/' + str(
                                i['id']) + '/?engineType=' + i['displayEngineType'] + '&issue=' + str(
                                i['issueInstanceId'])
                            }
                    issues.append(dict)
                    df = pd.DataFrame(issues)
                    print(df.to_csv())

