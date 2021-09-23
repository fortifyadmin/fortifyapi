class DefaultVersionTemplate:

    def generate(self, api, project_version_id):
        self.api = api
        self.project_version_id = project_version_id

        return [
            self.attributes(),
            self.responsibilities(),
            self.copy_from_partial(),
            self.commit_project_version(),
            self.copy_project_version_state(),
            self.configure_processing_rules()
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
        return self.api.construct_request('POST', f"/api/v1/projectVersions/projectVersions/{self.project_version_id}/action", [
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
            {
                "identifier": "com.fortify.manager.BLL.processingrules.BuildProjectProcessingRule",
                "displayName": "Require approval if the Build Project is different between scans",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.ExternalListVersionProcessingRule",
                "displayName": "Check external metadata file versions in scan against versions on server.",
                "displayable": True,
                "enabled": True
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.FileCountProcessingRule",
                "displayName": "Require approval if file count differs by more than 10%",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.ForceMigrationProcessingRule",
                "displayName": "Perform Force Instance ID migration on upload",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.FortifyAnnotationsProcessingRule",
                "displayName": "Require approval if result has Fortify Java Annotations",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.LOCCountProcessingRule",
                "displayName": "Require approval if line count differs by more than 10%",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.MigrationProcessingRule",
                "displayName": "Automatically perform Instance ID migration on upload",
                "displayable": True,
                "enabled": True
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.NewerEngineVersionProcessingRule",
                "displayName": "Require approval if the engine version of a scan is newer than the engine version of the previous scan",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.QuickScanProcessingRule",
                "displayName": "Ignore SCA Scans performed in QuickScan mode",
                "displayable": True,
                "enabled": True
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.RulePackVersionProcessingRule",
                "displayName": "Require approval if the rulepacks used in the scan do not match the rulepacks used in the previous scan",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.ValidCertificationProcessingRule",
                "displayName": "Require approval if SCA or WebInspect Agent scan does not have valid certification",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.WarningProcessingRule",
                "displayName": "Require approval if result has analysis warnings",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.UnknownOrDisallowedAuditedAttrChecker",
                "displayName": "Warn if audit information includes unknown custom tag",
                "displayable": True,
                "enabled": True
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.AuditedAnalysisRule",
                "displayName": "Require the issue audit permission to upload audited analysis files",
                "displayable": True,
                "enabled": True
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.PendingApprovalChecker",
                "displayName": "Disallow upload of analysis results if there is one pending approval",
                "displayable": True,
                "enabled": False
            },
            {
                "identifier": "com.fortify.manager.BLL.processingrules.VetoCascadingApprovalProcessingRule",
                "displayName": "Disallow approval for processing if an earlier artifact requires approval",
                "displayable": True,
                "enabled": False
            }
        ])


class CloneVersionTemplate(DefaultVersionTemplate):

    def __init__(self, previous_version_id):
        self.project_version_id = previous_version_id

    def copy_from_partial(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_FROM_PARTIAL",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": self.previous_version_id,
                    "copyAnalysisProcessingRules": True,
                    "copyBugTrackerConfiguration": True,
                    "copyCurrentStateFpr": True,
                    "copyCustomTags": True
                }
            }
        ])

    def copy_project_version_state(self):
        return self.api.construct_request('POST', f"/api/v1/projectVersions/{self.project_version_id}/action", [
            {
                "type": "COPY_CURRENT_STATE",
                "values": {
                    "projectVersionId": self.project_version_id,
                    "previousProjectVersionId": self.previous_version_id,
                    "copyCurrentStateFpr": False
                }
            }
        ])
