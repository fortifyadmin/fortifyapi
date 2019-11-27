# Fortify API Documentation

The fortify-api module contains a class that wraps the Fortify RESTful calls in a response object.  The class FortifyApi contains a set of prepared `GET` and `POST` calls.

## Table of Contents
[Constructor](#constructor)

[Response Object](#response-object)

[Methods](#methods)
- [add project version attribute: `add_project_version_attribute`](#add-project-version-attribute)
- [create project version: `create_project_version`](#create-project-version)
- [create new project and version: `create_new_project_version`](#create-new_project-version)
- [download artifact: `download_artifact`](#download-artifact)
- [download artifact scan: `download_artifact_scan`](#download-artifact-scan)
- [get artifact scans: `get_artifact_scans`](#get-artifact-scans)
- [get attribute definition: `get_attribute_definition`](#get-attribute-definition)
- [get attribute definitions: `get_attribute_definitions`](#get-attribute-definitions)
- [get file token: `get_file_token`](#get-file-token)
- [get issue template: `get_issue_template`](#get-issue-template)
- [get project version artifacts: `get_project_version_artifacts`](#get-project-version-artifacts)
- [get project version attributes: `get_project_version_attributes`](#get-project-version-attributes)
- [get project versions: `get_project_versions`](#get-project-versions)
- [get projects: `get_projects`](#get-projects)
- [get token: `get_token`](#get-token)
- [post attribute definition: `post_attribute_definition`](#post-attribute-definition)
- [upload artifact scan: `upload_artifact_scan`](#upload-artifact-scan)


## Constructor
The constructor requires only one value - the host address of the Fortify API. All others are optional.

#### Required parameters
*host* - The address of the Fortify API

#### Optional parameters
*username* - If the API is configured for basic auth, both username and password must be provided.<br>
*password* - If the API is configured for basic auth, both username and password must be provided.<br>
*token* - If an auth token is available (typically having previously called the get_token() method) the token can be used instead of username / password
*verify_ssl* - Defaults to false. To enable verification of an HTTPS connection to the API, set to True.<br>
*user_agent* - User agent for requests.<br>
*timeout* - Time in seconds to wait for a response from the Fortify API.
- - -


## Response object

All calls in this module return an object having the following properties and methods.


### Properties
*success* - a boolean indicating if the call was successful or not. True indicates a successful call, while False indicates an unsuccessful call.<br>
*response_code* - the actual HTTP response code from the call to the Fortify server.<br>
*message* - if the call was successful, message is 'OK'. If the call was not successful, message is descriptive text of the failure. e.g. An SSL error occurred, etc.<br>
*data* - the data (if any) returned from the Fortify API.<br>

### Methods
*data_json()* - Returns object data as JSON. An optional boolean parameter (pretty), if set to True, will return pretty-formatted JSON.

Below is an example of constructing a FortifyAPI class, calling a method, and exploring the response.

```python

>>> from fortifyapi import fortify

>>> api = FortifyApi('https://fortify.example.com', verify_ssl=True, token=token)

>>> response = api.get_projects()

>>> response.success
True

>>> response.response_code
200

>>> response.message
'OK'

>>> print response.data_json(pretty=True)
[
TODO: PUT EXAMPLE HERE
    ...
```
- - -

### Add Project Version Attribute:
Add the specified attribute to the specified project, using the specified value/values

#### Parameters
*project_version_id*<br>
*param attribute_definition_id*<br>
*guid*<br>
*value*<br>
*values*

- - -

### Commit Project Version:
Convenience function to set the 'committed' project version attribute to True

#### Parameters
*project_version_id:*</br>

- - -

### Create Project Version:
Create a new project version under the specified project

#### Parameters
*project_name*</br>
*param project_id*</br>
*param project_template*</br>
*param version_name*</br>

- - -

### Create New Project and Version:
Create a new project and new version under that project

#### Parameters
*project_name*</br>
*param project_template*</br>
*param version_name*</br>

- - -

### Download Artifact:
Download the specified artifact. The returned data is a binary blob of artifact content and file name of the artifact.

#### Parameters
*artifact_id*<br>

#### Example
```python
            api = FortifyApi("https://my-fortify-server:my-port", token=get_token())
            response, file_name = api.download_artifact_scan("my-id")
            if response.success:
                file_content = response.data
                with open('/path/to/some/folder/' + file_name, 'wb') as f:
                    f.write(file_content)
            else:
                print response.message
```
- - -

### Download Artifact Scan:
Download the specified scan. The returned data is a binary blob of scan content and file name of the scan.

#### Parameters
*artifact_id*<br>

#### Example
```python
            api = FortifyApi("https://my-fortify-server:my-port", token=get_token())
            response, file_name = api.download_artifact_scan("my-id")
            if response.success:
                file_content = response.data
                with open('/path/to/some/folder/' + file_name, 'wb') as f:
                    f.write(file_content)
            else:
                print response.message
```
- - -

### Get Artifact Scans:
Download a list of scans for the specified artifact.

#### Parameters
*parent_id*<br>

- - -

### Get Attribute Definition:
Get attribute definitions matching the specified search

#### Parameters
*search_expression*  A Fortify-formatted search expression, e.g. name:"Development Phase"<br>

- - -

### Get Attribute Definitions:
Get all attribute definitions.

#### Parameters
none<br>

- - -

### Get File Token:
Get a token for use in upload or download of a file. Typically for internal use only, but here if needed.

#### Parameters
*purpose* specify if the token is for file 'UPLOAD' or 'DOWNLOAD'<br>

- - -

### Get Issue Template:
Retrieve the specified project/issue template

#### Parameters
*project_template_id* The project/issue template to retrieve.

- - -

### Get Project Version Artifacts
Get all artifacts for the specified project version.

#### Parameters
*parent_id* the id of the project version

- - -

### Get Project Version Attributes
Get all attributes for the specified project version.

#### Parameters
*project_version_id* the id of the project version

- - -

### Get Project Versions
Get all project versions

#### Parameters
none <br>

- - -

### Get Projects
Get all projects

#### Parameters
none <br>

- - -

### Get Token
Get auth token for use in subsequent API calls

#### Parameters
*token_type*(optional)<br>
*ttl*

- - -

### Post Attribute Definition
Post the provided attribute definition

#### Parameters
*attribute_definition*

- - -

### Upload Artifact Scan
Upload the provided scan to the project version

#### Parameters
*file_path* Full path to the file to upload
*project_version_id* Project version id for the project version to which the scan should be uploaded

- - -
