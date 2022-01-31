class DefaultVersionTemplate:

    def generate(self, api, project_version_id):
        self.api = api
        self.project_version_id = project_version_id

        return [
            self.attributes(),
            self.responsibilities(),
            self.copy_from_partial(),
            self.copy_project_version_state(),
            self.configure_processing_rules(),
            self.commit_project_version()
        ]

    def attributes(self):
        return self.api.construct_request('PUT', f"/api/v1/projectVersions/{self.project_version_id}/attributes", [
            {
                "attributeDefinitionId": 5,
                "values": [
                    {
                        "guid": "New"
                    }
                ],
                "value": None
            },
            {
                "attributeDefinitionId": 6,
                "values": [
                    {
                        "guid": "Internal"
                    }
                ],
                "value": None
            },
            {
                "attributeDefinitionId": 7,
                "values": [
                    {
                        "guid": "internalnetwork"
                    }
                ],
                "value": None
            },
            {
                "attributeDefinitionId": 1,
                "values": [
                    {
                        "guid": "High"
                    }
                ],
                "value": None
            },
        ])

    def responsibilities(self):
        return self.api.construct_request('PUT', f"/api/v1/projectVersions/{self.project_version_id}/responsibilities", [
            {
                "responsibilityGuid": "projectmanager",
                "userId": None
            },
            {
                "responsibilityGuid": "securitychampion",
                "userId": None
            },
            {
                "responsibilityGuid": "developmentmanager",
                "userId": None
            }
        ])

    def copy_from_partial(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_FROM_PARTIAL",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": -1,
                    "copyAnalysisProcessingRules": True,
                    "copyBugTrackerConfiguration": True,
                    "copyCurrentStateFpr": False,
                    "copyCustomTags": True
                }
            }
        ])

    def commit_project_version(self):
        return self.api.construct_request('PUT', f"/api/v1/projectVersions/{self.project_version_id}", {
            'committed': True
        })

    def copy_project_version_state(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_CURRENT_STATE",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": -1,
                    "copyCurrentStateFpr": False
                }
            }
        ])

    def configure_processing_rules(self):
        return self.api.construct_request('PUT', f"/api/v1/projectVersions/{self.project_version_id}/resultProcessingRules", [
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
        ])


class CloneVersionTemplate(DefaultVersionTemplate):

    def __init__(self, previous_version_id):
        self.previous_version_id = previous_version_id

    def copy_from_partial(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_FROM_PARTIAL",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": self.previous_version_id,
                    "copyAnalysisProcessingRules": True,
                    "copyBugTrackerConfiguration": True,
                    #"copyCurrentStateFpr": True, # didn't see this in 21.1?
                    "copyCustomTags": True,
                    "copyUserAccessSettings": True,
                    "copyVersionAttributes": True
                }
            }
        ])

    def copy_project_version_state(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_CURRENT_STATE",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": self.previous_version_id
                }
            }
        ])


