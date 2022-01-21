import requests
import json
import sys
import signal
import getpass
import collections
from os import environ
from locale import LC_ALL, setlocale
from fortifyapi.fortify import FortifyApi
from sys import exit

#Loads settings for authentication from "settings.json"
print("Reading settings file...")
try:
    f = open('settings.json')
    settings = json.load(f)
    f.close()
except Exception as e:
    print(e)
    print("Error reading settings file")
    sys.exit(0)

print("Please enter your FortifySSC credentials:\n")

username = input("Username:")
password = getpass.getpass()


 # Authenticate and retrieve token
def token_creation():
     api = FortifyApi(host=url, username=username, password=password, verify_ssl=False)
     response = api.get_token(description=description)
     if(response.success == False):
        print("Incorrect credentials, please try again.")
        exit()
     else:
        #tokenId = response.data['data']['id']
        return [response.data['data']['token'], response.data['data']['id']]



# Set vars for connection
url = settings['SSC_URL']
user = username
password = password
description = settings['description']
token_dict = token_creation()
token = token_dict[0]
tokenId = token_dict[1]
print(token_dict)



 # Re-use token in all requests
def api():
     api = FortifyApi(host=url, token=token, verify_ssl=False)
     return api
     
# Creates a api object with basic authentication to be used for deleting tokens associated with the user     
def api_delete_token():
    delete_token_api = FortifyApi(host=url, username=username, password=password, verify_ssl=False)
   
    return delete_token_api
    
 # List ID, Project/application Version
#def list():
     #response = api().get_all_project_versions()
     #data = response.data['data']
     #for version in data:
         #print("{0:8} project versionid {1:30} {2:30}".format(version['id'], version['project']['name'], version['name']).encode(
             #'utf-8', errors='ignore').decode())
             
#Deletes an individual token based on tokenId
def delete_singular_token(token_Id):
    delete_response = api_delete_token().delete_token(token_Id)
    if(delete_response.message == 'OK'):
        print("Token has been deleted.")
    else:
        print("There was an error. Please check FortifySSC to ensure the token has been deleted")
    

#Deletes an LDAP user
def delete_user():
    query = input("Enter the username or email to be deleted (Ex: asrey): " )
    #Checks for empty string, empty string causes errors
    if(query == ''):
        print("Error! Empty string detected. Please retry.")
        main()
    
    #Gets LDAP user JSON object
    user_id_response = api().get_ldap_user(query)
    count = user_id_response.data['count']
  
    if(count == 0):
        print("User not found. Please try again.")
        main()
        
    elif(count == 1):
        #Deletes the user
        firstName = user_id_response.data['data'][0]['firstName']
        lastName = user_id_response.data['data'][0]['lastName']
        userId = user_id_response.data['data'][0]['id']
        print(userId)
        name = user_id_response.data['data'][0]['name']
        role_name = user_id_response.data['data'][0]['roles'][0]['name']
        
        while True:
        #Double checks to ensure the correct user is being deleted.
            print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
            print("Current role: " + role_name + "\n")
            print("Is this the user you would like to delete? Please select the number with the desired choice.\n")
            print("1. Yes")
            print("2. No\n")
            user_choice = input()
            if(user_choice == "1"):
                response = api().delete_ldap_user(userId)   
                print("Success! User: " +name +" has been deleted.")
                main()
            elif(user_choice == "2"):
                print("Returning you to the main menu. Please retry.")
                main()
            elif(user_choice == 'quit'):
                print("Returning to the main menu...")
                main()
            else:
                print("Invalid choice. Please retry. Type 'quit' to return to the main menu.")
            
    elif(count > 1):
        #If non-unique information is passed in the user is prompted with all the found users and asked to try again
        count_users = 0
        multiple_user_response = user_id_response.data['data']
        print("These users were found: ")
        for names in multiple_user_response:
            print(user_id_response.data['data'][count_users]['name'] + 
            " (" + user_id_response.data['data'][count_users]['firstName'] + " " 
            + user_id_response.data['data'][count_users]['lastName'] +")" ) 
            count_users+=1
        print("Please retry and enter the unique email.")
        main()
    else:
        print("Error. Please ensure the credentials are correct.")
        main()
   
#Adds LDAP user
def adds_ldap_user():
    #Prompts user for ID and desired role
    query = input("Enter the username or email (Ex: asrey): ")
    role_list = api().get_roles_list()
    role_data = role_list.data['data']
    role_count = 1
    if(query == ''):
        print("Error! Empty string detected. Please retry.")
        main()
    if(query == 'quit'):
        print("Returning to the main menu...")
        main()
    for names in role_data:
        print(str(role_count) + ". " + names['name'])
        role_count += 1
    newRole = input("Enter the new role (Ex: Developer): ")
    
    if(newRole == 'quit'):
        print("Returning to the main menu...")
        main()
        
    role_id = -1
    
    #Queries Active Directory through API endpoint to collect information for the creation of a LDAP User object
    user_data_response = api().get_unregistered_user(query)
    
   

    if(user_data_response.data['count'] == 1):
    #Stores all the necessary variables for the updated json object
        distinguishedName = user_data_response.data['data'][0]['distinguishedName']
        userId = user_data_response.data['data'][0]['id']
        email = user_data_response.data['data'][0]['email']
        firstName = user_data_response.data['data'][0]['firstName']
        lastName = user_data_response.data['data'][0]['lastName']
        ldapType = user_data_response.data['data'][0]['ldapType']
        name = user_data_response.data['data'][0]['name']
        
        print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
        #print("Current role: " + role_name)
           
    
    
       
    elif(user_data_response.data['count'] > 1):
    #If non-unique information is passed in the user is prompted with all the found users and asked to try again
        count = 0
        multiple_user_response = user_data_response.data['data']
        print("These were the first 200 users found: ")
        for names in multiple_user_response:
            print(user_data_response.data['data'][count]['name'] + 
            " (" + user_data_response.data['data'][count]['firstName'] + " " 
            + user_data_response.data['data'][count]['lastName'] +")" ) 
            count+=1
        print("Please retry and enter the unique ID or email.")
        main()
        
    else:
        print("An error occurred, the user could not be found or already exists.")
        main()
    
    roles_response =  api().get_roles_list()
    role_data = roles_response.data['data']
  
  #Finds the role id associated with the role name passed in
    for names in role_data:
        if(names['name'].lower() == newRole.lower()):
            role_id = names['id']
            role_name = names['name']
            role_description = names['description']
            break
            
    if(role_id == -1):
        print("Error! Role not found.")
        main()
        
    final_response = api().add_ldap_user(distinguishedName, email, firstName, lastName, 
    ldapType, name, role_description, role_id, role_name) 
    
    #Double checks to ensure that the update was sucessful and the database has the correct role saved
    
    #This check has been commented out for speed purposes (querying the test environment is very slow), may be added back later
    
    #successCheck = api().get_ldap_user(query)
    #successCheck_data = successCheck.data['data'][0]['roles'][0]['name']
    #if(successCheck_data == newRole):
    print("Success! " + name + " has been added to the LDAP user database. Please verify on FortifySSC that the changes have been made.")
    main()
    #else:
        #print("An error occurred. Please retry the request and ensure the input is correct.")

def update_ldap_version():
    
    while True:
        query = input("Enter the username or email (Ex: asrey): ")
        if(query == ''):
            print("Error! Empty string detected. Please retry.")
            main()
        if(query == 'quit'):
            print("Returning to the main menu...")
            main()
        user_data_response = api().get_ldap_user(query)
        #If only one user is found, userId of that user is stored
        if(user_data_response.data['count'] == 1):
            firstName = user_data_response.data['data'][0]['firstName']
            lastName = user_data_response.data['data'][0]['lastName']
            role_name = user_data_response.data['data'][0]['roles'][0]['name']
            name = user_data_response.data['data'][0]['name']
            print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
            print("Current role: " + role_name)
            userId = user_data_response.data['data'][0]['id']
            response = api().get_ldap_user_versions(userId)
            idx = 0
            project_names_list = response.data['data']
             
    
            print("Current Versions:")
            for names in project_names_list:
                print(response.data['data'][idx]['project']['name'] + " - " + response.data['data'][idx]['name'])
                idx+=1
            print("\n")
            break
        
        elif(user_data_response.data['count'] > 1):
        #If non-unique information is passed in the user is prompted with all the found users and asked to try again
            count = 0
            multiple_user_response = user_data_response.data['data']
            print("These users were found: ")
            for names in multiple_user_response:
                print(user_data_response.data['data'][count]['name'] + 
                " (" + user_data_response.data['data'][count]['firstName'] + " " 
                + user_data_response.data['data'][count]['lastName'] +")" ) 
                count+=1
            print("Please retry and enter the unique ID or email.")
            
        else:
            print("An error occurred, the user could not be found. Please retry with the correct credentials")
          
    
    while True:
    #Prompts user for desired Application Name
        application_name = input("Enter Application Name (Ex: AU-AA): ")
        #Typing quit allows the user to return to the main menu
        if(application_name == 'quit'):
            print("Returning to the main menu...")
            main()
        project_name = api().get_project_versions(application_name)
        
        #If project could not be found, user is prompted to try again
        if(project_name.data['count'] == 0):
            project_list = api().get_projects(application_name)
            print("Error! Specific project could not be found or application does not have any active versions.")
        #Prints all the found applications based on the users query    
            idx = 0
            project_names_list = project_list.data['data']
            for names in project_names_list:
                print(project_list.data['data'][idx]['name'])
                idx+=1
                
            print("Please view the search results and try entering the application name again.")
       
        else:
            count = 1
            idx = 0
            multiple_project_response = project_name.data['data']
            #Finds and prints the versions associated with the application
            print("These project versions were found: ")
            select_dict = {}
            for names in multiple_project_response:
                select_dict.update({count: project_name.data['data'][idx]['currentState']['id']})
                print(str(count) + ". " + project_name.data['data'][idx]['name'])
                count+=1
                idx+=1
            print(str(count) +". " + "Provision access to all listed application versions.")
            break
            
            if(count == 1):
                print("No applications could be found.")
        
    while True:
        
        all_access = count
    #Prompts user to choose a project version
        version_choice =  input("Please select the number associated with the desired project version: ")
        
        if(version_choice == ''):
            print("Invalid choice. Please try again.")
        elif(version_choice == 'quit'):
            print("Returning to main menu...")
            main()
        else:
            try:
                version_choice = int(version_choice)
            except ValueError:
                print("Not a valid integer. Please try again.")
                
            if((version_choice not in select_dict) and (all_access is not version_choice)):
                print("Invalid choice. Please try again.")
            else:
                if(version_choice == all_access):
                    
                    for versions in select_dict:
                        add_version = api().add_project_version(userId, select_dict.get(versions))
                        
                    print("All associated versions have been added! Please verify the changes on FortifySSC.")
                else:
                    add_version = api().add_project_version(userId, select_dict.get(version_choice))
                    print("Success! Please ensure the change has been made on SSC.")
                while True:
                    print("Would you like to provision access to another version?")
                    print("1. Yes")
                    print("2. No")
                    choice = input()
                    if(choice == "1"):
                        update_ldap_version_again(name)
                    elif(choice == "2"):
                        print("Returning you to the main menu...")
                        main()
                    else:
                        print("Invalid choice. Please try again.")
    
def update_ldap_version_again(name):
    
    while True:
 
        user_data_response = api().get_ldap_user(name)
        #If only one user is found, userId of that user is stored
        if(user_data_response.data['count'] == 1):
            firstName = user_data_response.data['data'][0]['firstName']
            lastName = user_data_response.data['data'][0]['lastName']
            role_name = user_data_response.data['data'][0]['roles'][0]['name']
            name = user_data_response.data['data'][0]['name']
            userId = user_data_response.data['data'][0]['id']
            print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
            print("Current role: " + role_name)
            response = api().get_ldap_user_versions(userId)
            idx = 0
            project_names_list = response.data['data']
 
            print("Current Versions:")
            for names in project_names_list:
                print(response.data['data'][idx]['project']['name'] + " - " + response.data['data'][idx]['name'])
                idx+=1
            print("\n")
            break
       
         
       
            
        elif(user_data_response.data['count'] > 1):
        #If non-unique information is passed in the user is prompted with all the found users and asked to try again
            count = 0
            multiple_user_response = user_data_response.data['data']
            print("These users were found: ")
            for names in multiple_user_response:
                print(user_data_response.data['data'][count]['name'] + 
                " (" + user_data_response.data['data'][count]['firstName'] + " " 
                + user_data_response.data['data'][count]['lastName'] +")" ) 
                count+=1
            print("Please retry and enter the unique ID or email.")
            
        else:
            print("An error occurred, the user could not be found. Please retry with the correct credentials")    
            main()
        
            
        
    
    while True:
    #Prompts user for desired Application Name
        application_name = input("Enter Application Name (Ex: AU-AA): ")
        #Typing quit allows the user to return to the main menu
        if(application_name == 'quit'):
            print("Returning to the main menu...")
            main()
        project_name = api().get_project_versions(application_name)
        
        #If project could not be found, user is prompted to try again
        if(project_name.data['count'] == 0):
            project_list = api().get_projects(application_name)
            print("Error! Specific project could not be found or application does not have any active versions.")
        #Prints all the found applications based on the users query    
            idx = 0
            project_names_list = project_list.data['data']
            for names in project_names_list:
                print(project_list.data['data'][idx]['name'])
                idx+=1
                
            print("Please view the search results and try entering the application name again.")
       
        else:
            
            count = 1
            idx = 0
            multiple_project_response = project_name.data['data']
            #Finds and prints the versions associated with the application
            print("These project versions were found: ")
            select_dict = {}
            for names in multiple_project_response:
                select_dict.update({count: project_name.data['data'][idx]['currentState']['id']})
                print(str(count) + ". " + project_name.data['data'][idx]['name'])
                count+=1
                idx+=1
            print(str(count) +". " + "Provision access to all listed application versions.")
            break
            
            
            if(count == 1):
                print("No applications could be found.")
        
    while True:
    
        all_access = count
    #Prompts user to choose a project version
        version_choice =  input("Please select the number associated with the desired project version: ")
        
        if(version_choice == ''):
            print("Invalid choice. Please try again.")
        elif(version_choice == 'quit'):
            print("Returning to main menu...")
            main()
        else:
            try:
                version_choice = int(version_choice)
            except ValueError:
                print("Not a valid integer. Please try again.")
               
            if((version_choice not in select_dict) and (all_access is not version_choice)):
                print("Invalid choice. Please try again.")
            else:
                if(version_choice == all_access):
                    for versions in select_dict:
                        add_version = api().add_project_version(userId, select_dict.get(versions))
                        
                    print("All associated versions have been added! Please verify the changes on FortifySSC.")
                else:
                    add_version = api().add_project_version(userId, select_dict.get(version_choice))
                    print("Success! Please ensure the change has been made on SSC.")
                while True:
                    print("Would you like to provision access to another version?")
                    print("1. Yes")
                    print("2. No")
                    choice = input()
                    if(choice == "1"):
                        update_ldap_version_again(name)
                    elif(choice == "2"):
                        print("Returning you to the main menu...")
                        main()
                    else:
                        print("Invalid choice. Please try again.")
        
                
                
def update_ldap_user_role():
# Prompts the user for username and desired new role
    query = input("Enter the username or email (Ex: asrey): ")
    
    if(query == ''):
        print("Error! Empty string detected. Please retry.")
        main()
    if(query == 'quit'):
        print("Returning to main menu...")
        main()
        
    new_role_id = -1
    user_data_response = api().get_ldap_user(query)
    
    if(user_data_response.success == False):
        print(user_data_response)
        print("An error occurred. Please ensure the userId is correct.")
        main()
    
    if(user_data_response.data['count'] == 1):
    #Stores all the necessary variables for the updated json object
        distinguishedName = user_data_response.data['data'][0]['distinguishedName']
        userId = user_data_response.data['data'][0]['id']
        email = user_data_response.data['data'][0]['email']
        firstName = user_data_response.data['data'][0]['firstName']
        lastName = user_data_response.data['data'][0]['lastName']
        ldapType = user_data_response.data['data'][0]['ldapType']
        name = user_data_response.data['data'][0]['name']
        role_name = user_data_response.data['data'][0]['roles'][0]['name']
        role_description = user_data_response.data['data'][0]['roles'][0]['description']
        objectVersion = user_data_response.data['data'][0]['roles'][0]['objectVersion']
        publishVersion = user_data_response.data['data'][0]['roles'][0]['publishVersion']
        
        print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
        print("Current role: " + role_name)
         
        role_list = api().get_roles_list()
        role_data = role_list.data['data']
   
        role_count = 1
        for names in role_data:
            print(str(role_count) + ". " + names['name'])
            role_count += 1
        newRole = input("Enter the new role (Ex: MF Developer): ")
        
        if(newRole == 'quit'):
            print("Returning to the main menu...")
            main()
    
    elif(user_data_response.data['count'] > 1):
    #If non-unique information is passed in the user is prompted with all the found users and asked to try again
        count = 0
        multiple_user_response = user_data_response.data['data']
        print("These users were found: ")
        for names in multiple_user_response:
            print(user_data_response.data['data'][count]['name'] + 
            " (" + user_data_response.data['data'][count]['firstName'] + " " 
            + user_data_response.data['data'][count]['lastName'] +")" ) 
            count+=1
        print("Please retry and enter the unique ID or email.")
        main()
        
    else:
        print("An error occurred, the user could not be found.")
        main()
        
    roles_response =  api().get_roles_list()
    role_data = roles_response.data['data']
  
  #Finds the role id associated with the role name passed in
    for names in role_data:
        if(names['name'].lower() == newRole.lower()):
           new_role_id = names['id']
           break
           
    if(new_role_id == -1):
        print("Error! Role not found.")
        main()
        
    final_response = api().update_ldap_user_role(userId, distinguishedName, email, firstName, 
    lastName, ldapType, name, role_description, new_role_id, newRole, objectVersion, publishVersion) 
    
    print("Success! " + name + " has been updated to the " + '"' + newRole + '" ' + "role.")
    main()
    

def delete_all_tokens():
    response = api_delete_token().delete_all_user_tokens()
    if(response.message == 'OK'):
        print("Tokens have been deleted.")
    else:
        print("There was an issue trying to delete the tokens. Please ensure the tokens have been deleted on FortifySSC.")

def get_project_versions():
    response = api().get_all_project_versions()
    print(response.data_json(pretty = True))

     
def add_multiple_users():
    
    user_input = list(map(str, input("Enter multiple users separated by spaces (Ex: asrey abacon abhinmishra): ").split()))
    if(len(user_input) == 0):
        print("Empty string detected. Please try again.")
        main()
    user_idx = 0
    for users in user_input:
        user_data_response = api().get_unregistered_user(user_input[user_idx])
        user_idx += 1
        if(user_data_response.data['count'] == 0):
            print("One or more of the ID's is incorrect. Please retry and ensure that each credential is correct.")
            main()
        elif(user_data_response.data['count'] > 1):
            print("One or more of the ID's was not unique. Please retry.")
            main()
        
    role_input = []
    role_list = api().get_roles_list()
    role_data = role_list.data['data']
   
    role_count = 1
    for names in role_data:
        print(str(role_count) + ". " + names['name'])
        role_count += 1
        
    
    for username in user_input:
        count = 1
        idx = 0
        
        select_dict = {}
        for roles in role_data:   
            #multiple_project_response = role_list.data['data']
            #Finds and prints the versions associated with the application
            #for names in multiple_project_response:
            select_dict.update({count: role_list.data['data'][idx]['name']})
         
            count+=1
            idx+=1
         #break
        while True:
            role_choice =  input("Please select the number associated with the desired role for " + username + ":")
       
            if(role_choice == ''):
                print("Invalid choice. Please try again.")
            elif(role_choice == 'quit'):
                print("Returning to main menu...")
                main()
            
            else:
                try:
                    role_choice = int(role_choice)
                except ValueError:
                    print("Not a valid integer. Please try again.")
                    
                role_input.append(select_dict.get(role_choice))
                #print(role_input)
                break
            
# using zip()
# to convert lists to dictionary
    res_dict = dict(zip(user_input, role_input))
  
# Printing resultant dictionary 
    #print ("Resultant dictionary is : " +  str(res_dict))           
                
    role_id = -1
   
    roles_response =  api().get_roles_list()
    role_data = roles_response.data['data']
    user_idx = 0
    
    for names in res_dict:
        user_data_response = api().get_unregistered_user(user_input[user_idx])
  #Finds the role id associated with the role name passed 
        
        if(user_data_response.data['count'] == 1):
    #Stores all the necessary variables for the updated json object
                distinguishedName = user_data_response.data['data'][0]['distinguishedName']
       
                userId = user_data_response.data['data'][0]['id']
             
                email = user_data_response.data['data'][0]['email']
            
                firstName = user_data_response.data['data'][0]['firstName']
               
                lastName = user_data_response.data['data'][0]['lastName']
          
                ldapType = user_data_response.data['data'][0]['ldapType']

                name = user_data_response.data['data'][0]['name']
   
                print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
               
                user_idx += 1
                
        elif(user_data_response.data['count'] > 1):
        #If non-unique information is passed in the user is prompted with all the found users and asked to try again
            count = 0
            multiple_user_response = user_data_response.data['data']
            print("These users were found: ")
            for names in multiple_user_response:
                print(user_data_response.data['data'][count]['name'] + 
                " (" + user_data_response.data['data'][count]['firstName'] + " " 
                + user_data_response.data['data'][count]['lastName'] +")" ) 
                count+=1
            print("Please retry and enter the unique ID or email.")
            
        else:
            print("An error occurred, the user could not be found. Please retry with the correct credentials")
            
        for role_name in role_data:

            if(role_name['name'] == res_dict.get(names)):
                role_id = role_name['id']

                rolename = role_name['name']

                role_description = role_name['description']

                break        
        final_response = api().add_ldap_user(distinguishedName, email, firstName, lastName, 
    ldapType, name, role_description, role_id, rolename)
     
        print("Success! " + name + " has been added to the LDAP user database.")
    
    print("Please ensure the users have been added on SSC.")
    main()
def get_ldap_user_project_versions():
    while True:
        query = input("Enter the username or email (Ex: asrey): ")
        if(query == ''):
            print("Error! Empty string detected. Please retry.")
            main()
        if(query == 'quit'):
            print("Returning to main menu...")
            main()
            
        user_data_response = api().get_ldap_user(query)
         
        #If only one user is found, userId of that user is stored
        if(user_data_response.data['count'] == 1):
            firstName = user_data_response.data['data'][0]['firstName']
            lastName = user_data_response.data['data'][0]['lastName']
            role_name = user_data_response.data['data'][0]['roles'][0]['name']
            name = user_data_response.data['data'][0]['name']
            print("User found: " + name + " " + "(" + firstName + ", " + lastName + ")")
            print("Current role: " + role_name + "\n")
            userId = user_data_response.data['data'][0]['id']
            response = api().get_ldap_user_versions(userId)
            idx = 0
            project_names_list = response.data['data']
             
            #print(response.data_json(pretty = True))
            #print(project_names_list)
            for names in project_names_list:
                print(response.data['data'][idx]['project']['name'] + " - " + response.data['data'][idx]['name'])
                idx+=1
            print("\n")
            
            if(idx == 0):
                print("No project versions were found!")
            break
            
            
        elif(user_data_response.data['count'] > 1):
        #If non-unique information is passed in the user is prompted with all the found users and asked to try again
            count = 0
            multiple_user_response = user_data_response.data['data']
            print("These users were found: ")
            for names in multiple_user_response:
                print(user_data_response.data['data'][count]['name'] + 
                " (" + user_data_response.data['data'][count]['firstName'] + " " 
                + user_data_response.data['data'][count]['lastName'] +")" ) 
                count+=1
            print("Please retry and enter the unique ID or email.")
            
        else:
            print("An error occurred, the user could not be found. Please retry with the correct credentials")
                 
    main()

def main():
    
    try:
        print("\nPlease press the associated number for the desired action: \n")
        print("1. Update an LDAP User role\n")
        print("2. Delete a LDAP User\n")
        print("3. Add a project version to a LDAP User\n")
        print("4. Look up the project versions associated with a LDAP User\n")
        print("5. Add a LDAP User\n")
        print("6. Quit and delete token\n")
        print("7. Add multiple LDAP Users\n")
        
        query = input()
     
        if(query == "1"):
            update_ldap_user_role()
        elif(query == "2"):
            delete_user()
        elif(query == "3"):
            update_ldap_version()
        elif(query == "4"):
            get_ldap_user_project_versions()
        elif(query == "5"):
            adds_ldap_user()
        elif(query == "6"):
            delete_singular_token(tokenId)
            exit()
        elif(query == "7"):
            add_multiple_users()
        else:
            print("Please try again with a valid choice.")
            main()
    
    except KeyboardInterrupt:
        print('\nInterrupted')
        exit()
        
if __name__ == '__main__':
    main()
    