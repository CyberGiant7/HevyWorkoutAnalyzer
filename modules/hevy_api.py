"""
Hevy API

Provides the methods for interacting with the Hevy API
"""

import requests
import json
import os
import getpass
import re
import time
import datetime
import shutil

from pathlib import Path
import concurrent.futures 

# Basic headers to use throughout
BASIC_HEADERS = {
	'x-api-key': 'with_great_power',
	'Content-Type': 'application/json',
	'accept-encoding':'gzip'
}

#
# Simple method to provide a login prompt on command line, which is then just passed to login below
#
def login_cli():
	user = input("Please input a username: ")
	password = getpass.getpass()
	
	login(user,password)

#
# Login method taking a username and password
# Logs in and then downloads account.json, the profile pic, and the workout_count
# Returns 200 if all successful
#	
def login(user, password):
	# Try to import client_storage module
	try:
		from modules import client_storage
	except ImportError:
		# Fall back to file-based storage if client_storage is not available
		home_folder = str(Path.home())
		utb_folder = "./utb_folder"

		if not os.path.exists(utb_folder):
			os.makedirs(utb_folder)
			os.makedirs(utb_folder+"/temp")

	headers = BASIC_HEADERS.copy()
	
	# Post username and password to Hevy
	s = requests.Session()
	
	r = s.post('https://api.hevyapp.com/login', data=json.dumps({'emailOrUsername':user,'password':password}), headers=headers)
	if r.status_code == 200:
		json_content = r.json()
		s.headers.update({'auth-token': json_content['auth_token']})
		
		auth_token = json_content['auth_token']
	
		r = s.get("https://api.hevyapp.com/account", headers=headers)
		if r.status_code == 200:
			data = r.json()
			
			account_data = {"data":data, "Etag":r.headers['Etag']}
			user_id = data["id"]
			
			# Store in client-side storage if available
			try:
				from modules import client_storage
				client_storage.store_auth_data(auth_token, user_id)
				client_storage.store_account_data(data, r.headers['Etag'])
				
				# Store profile image if available
				if "profile_pic" in data:
					imageurl = data["profile_pic"]
					response = requests.get(imageurl, stream=True)
					if response.status_code == 200:
						client_storage.store_profile_image(response.raw.read())
						
						# Get workout count
						r = s.get("https://api.hevyapp.com/workout_count", headers=headers)
						if r.status_code == 200:
							data = r.json()
							client_storage.store_workout_count(data, r.headers['Etag'])
							return 200
						return r.status_code
				return 200
			except ImportError:
				# Fall back to file-based storage
				utb_folder = "./utb_folder"
				user_folder = utb_folder + "/user_"+user_id
		
				if not os.path.exists(user_folder):
					os.makedirs(user_folder)
					os.makedirs(user_folder+"/workouts")
					os.makedirs(user_folder+"/routines")
				
				with open(utb_folder+"/session.json", 'w') as f:
					json.dump({"auth-token":auth_token,"user-id":user_id},f)
				
				with open(user_folder+"/account.json", 'w') as f:
					json.dump(account_data, f)
				
				if "profile_pic" in data:
					imageurl = data["profile_pic"]
					response = requests.get(imageurl, stream=True)
					if response.status_code == 200:
						with open(user_folder+"/profileimage", 'wb') as out_file:
							shutil.copyfileobj(response.raw, out_file)
							
						r = s.get("https://api.hevyapp.com/workout_count", headers=headers)
						if r.status_code == 200:
							data = r.json()
							
							workout_count = {"data":data, "Etag":r.headers['Etag']}
							
							with open(user_folder+"/workout_count.json", 'w') as f:
								json.dump(workout_count, f)
								
							return 200
						return r.status_code
				return 200
		else:
			return r.status_code
	else:
    		return r.status_code

#
# Simple method to log out. We'll delete the user id and auth-token from the sessions file
#
def logout():
	# The folder to access/store data files
	home_folder = str(Path.home())
	utb_folder = "./utb_folder"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return True
	del session_data["auth-token"]
	del session_data["user-id"]
	with open(utb_folder+"/session.json", 'w') as f:
		json.dump({},f)
	return True

#
# Simple check to see if we have a current token saved indicating we are logged in
# If logged in return (True, User_Folder, Auth_Token) else (False, None, None)
#
def is_logged_in():
	# Try to get auth data from client-side storage first
	try:
		from modules import client_storage
		auth_token, user_id = client_storage.get_auth_data()
		if auth_token and user_id:
			# Create a virtual user_folder path for compatibility with existing code
			virtual_user_folder = f"virtual_user_{user_id}"
			return True, virtual_user_folder, auth_token
		return False, None, None
	except ImportError:
		# Fall back to file-based login check if client_storage module is not available
		# The folder to access/store data files
		home_folder = str(Path.home())
		utb_folder = "./utb_folder"
		
		session_data = {}
		if os.path.exists(utb_folder+"/session.json"):	
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)
		else:
			return False, None, None
		
		try:
			auth_token = session_data["auth-token"]
			# this is the folder we'll save the data file to
			user_folder = utb_folder + "/user_" + session_data["user-id"]	
			return True, user_folder, auth_token
		except:
			return False, None, None

#
# Updates a local JSON file and returns a http status code indicating success.
# to_update is the API call to be used. Needs to be from pre-determined list as below in lookup dict.
# API returns a 304 if local file is already up-to-date, or a 200 when providing a new file
# We add 404 for when asking for an unknown API call, and 403 when we are not logged in
#
def update_generic(to_update):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# The accessible API calls for this method
	lookup = {"account":"https://api.hevyapp.com/account",
		"user_preferences":"https://api.hevyapp.com/user_preferences",
		"body_measurements":"https://api.hevyapp.com/body_measurements",
		"workout_count":"https://api.hevyapp.com/workout_count",
		"set_personal_records":"https://api.hevyapp.com/set_personal_records",
		"user_subscription":"https://api.hevyapp.com/user_subscription",
		}
	# Fail if to_update is not in the list
	if to_update not in lookup.keys():
		return 404
	
	update_url = lookup[to_update]
	filename = to_update + ".json"

	# Create headers to be used
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Check if the file already exists, if it does we'll send the server the Etag so we only get an update
	update_data = None
	if os.path.exists(user_folder+"/"+filename):	
		with open(user_folder+"/"+filename, 'r') as file:
			update_data = json.load(file)
		headers["if-none-match"] = update_data["Etag"]
	
	# Now finally do the request for the update. If new update then put that in the file and return 200, else return 304
	s = requests.Session()
	r = s.get(update_url, headers=headers)
	if r.status_code == 200:
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		with open(user_folder+"/"+filename, 'w') as f:
			json.dump(new_data, f)
			
			
		# IF ACCOUNT UPDATED WE ALSO WILL RE-FETCH PROFILE IMAGE
		if to_update == "account":
			try:
				if "profile_pic" in data:
					imageurl = data["profile_pic"]
					response = requests.get(imageurl, stream=True)
					if response.status_code == 200:
						with open(user_folder+"/profileimage", 'wb') as out_file:
							shutil.copyfileobj(response.raw, out_file)
					print("updated profile pic")
			except:	
				pass
			
		return 200
	elif r.status_code == 304:
		return 304

#
# Batch downloads JSON workout files
# This should be used when wanting to bulk download workout files.
# It finds the highest Hevy index in existing downloaded files and requests all new files after that index
# Hevy returns a number of workout files. Idea is to keep calling this until Hevy doesn't return anything.
#
def batch_download():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing workout data
	try:
		from modules import client_storage
	except ImportError:
		return 500, False

	# Create the headers to be used
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token	
	
	# Get all workout data from client storage
	workout_data_dict = client_storage.get_workout_data()
	
	startIndex = 0
	# Find the highest index in existing workouts
	if workout_data_dict:
		for workout_id, workout in workout_data_dict.items():
			if "index" in workout:
				temp_index = workout["index"]
				if temp_index >= startIndex:
					startIndex = temp_index + 1 # make the start index one after the largest we have
	
	# Now finally do the request for workout files		
	s = requests.Session()	
	r = s.get("https://api.hevyapp.com/workouts_batch/"+str(startIndex), headers=headers)
	if r.status_code == 200:
		data = r.json()
		
		havesome = False
		for new_workout in data:
			havesome = True
			workout_id = new_workout['id']
			
			# Save to client-side storage
			client_storage.store_workout_data(workout_id, new_workout)
			
			print("new workout", workout_id)

		# return 200 and a boolean indicating whether Hevy returned new files
		return 200, havesome
	else:
		return r.status_code, False

#
# This uploads all local workout ids and when they were last updated, hevy then returns any changes that have been made on server	
# This should be used when just wanting to get the most recent updates
# It seems inefficient when there are lots of workouts, but I guess any file could be updated at any time...
# Hevy returns isMore indicating whether this should be rerun to collect more updates
#
def workouts_sync_batch():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing workout data
	try:
		from modules import client_storage
		from modules.client_storage import WORKOUT_DATA_KEY
		import streamlit as st
	except ImportError:
		return 500, False
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Get all workout data from client storage
	workout_data_dict = client_storage.get_workout_data()
	
	# Go through all workouts and compile the workout ID and when it was updated
	existing_data = {}
	if workout_data_dict:
		for workout_id, workout_data in workout_data_dict.items():
			if 'id' in workout_data and 'updated_at' in workout_data:
				existing_data[workout_data['id']] = workout_data['updated_at']
	
	# Post our existing data that we have compiled, and see what gets returned
	s = requests.Session()
	r = s.post('https://api.hevyapp.com/workouts_sync_batch', data=json.dumps(existing_data), headers=headers)
	json_content = r.json()	

	# Save any updated workouts to client-side storage
	for updated_workout in json_content['updated']:
		workout_id = updated_workout['id']
		client_storage.store_workout_data(workout_id, updated_workout)
		print("updated workout", workout_id)
		
	# Remove any deleted workouts from client-side storage
	for deleted_workout in json_content['deleted']:
		if WORKOUT_DATA_KEY in st.session_state and deleted_workout in st.session_state[WORKOUT_DATA_KEY]:
			del st.session_state[WORKOUT_DATA_KEY][deleted_workout]
			print("deleted workout", deleted_workout)
		
	# Do we need to make this API call again because there is more data available???
	update = False
	if json_content['isMore'] == True:
		update = True	
	
	return (200, update)


#
# Similar to workouts sync batch but for saved routines
#
def routines_sync_batch():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing routine data
	try:
		from modules import client_storage
		from modules.client_storage import ROUTINE_DATA_KEY
		import streamlit as st
	except ImportError:
		return 500, False
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Get all routine data from client storage
	routine_data_dict = client_storage.get_routine_data()
	
	# Go through all routines and compile the routine ID and when it was updated
	existing_data = {}
	if routine_data_dict:
		for routine_id, routine_data in routine_data_dict.items():
			if 'id' in routine_data and 'updated_at' in routine_data:
				existing_data[routine_data['id']] = routine_data['updated_at']
	
	# Post our existing data that we have compiled, and see what gets returned
	s = requests.Session()
	r = s.post('https://api.hevyapp.com/routines_sync_batch', data=json.dumps(existing_data), headers=headers)
	json_content = r.json()	
		
	# Save any updated routines to client-side storage
	for updated_routine in json_content['updated']:
		routine_id = updated_routine['id']
		client_storage.store_routine_data(routine_id, updated_routine)
		print("updated routine", routine_id)
		
	# Remove any deleted routines from client-side storage
	for deleted_routine in json_content['deleted']:
		if ROUTINE_DATA_KEY in st.session_state and deleted_routine in st.session_state[ROUTINE_DATA_KEY]:
			del st.session_state[ROUTINE_DATA_KEY][deleted_routine]
			print("deleted routine", deleted_routine)
		
	# Do we need to make this API call again because there is more data available???
	update = False
	if json_content['isMore'] == True:
		update = True	
	
	return (200, update)

#
# Upload an updated workout
#
def put_routine(the_json, routine_id=None):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	
#	# Workouts subfolder	
#	workouts_folder = user_folder + "/workouts"
#	routines_folder = user_folder + "/routines"
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token

	#return 200
	s = requests.Session()
	#print('https://api.hevyapp.com/routine/'+routine_id)
	#print(the_json)
	
	r = None
	if routine_id == None:
		r = s.post('https://api.hevyapp.com/routine/', data=json.dumps(the_json), headers=headers)
	else:
		r = s.put('https://api.hevyapp.com/routine/'+routine_id, data=json.dumps(the_json), headers=headers)
	return r.status_code
	#return 400

def delete_routine(routine_id):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	s = requests.Session()	
	r = s.delete('https://api.hevyapp.com/routine/'+routine_id, headers=headers)
	return r.status_code, False

#	
# Get the Hevy workout feed starting from workout with given index, returns json data
#
def feed_workouts_paged(start_from):
	print("feed_workouts_paged",start_from)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# workout image stuff, set folder, delete old images
	img_folder = str(Path.home())+ "/.underthebar/temp/"
	if not os.path.exists(img_folder):
		os.makedirs(img_folder)
	# its probably a bit much to do this every time, I'll put it somewhere else.
	#for f in os.listdir(img_folder):
	#	if os.stat(os.path.join(img_folder,f)).st_mtime < time.time() - 14 * 86400:
	#		os.remove(os.path.join(img_folder,f))
			
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/feed_workouts_paged/"
	if start_from != 0:
		url = url + str(start_from)
	
	# Do the request
	s = requests.Session()	
	r = s.get(url, headers=headers)
	if r.status_code == 200:
	
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		
		# this bit is for downloading feed workout images, request in parallel
		img_urls = []
		for workout in data["workouts"]:
			for img_url in workout["image_urls"]:
				img_urls.append(img_url)
		
		#with concurrent.futures.ThreadPoolExecutor() as exector : 
		#	exector.map(download_img, img_urls)
		# above 2 lines waited for threads to complete, this just starts them and carries on.
		exector =  concurrent.futures.ThreadPoolExecutor() 
		exector.map(download_img, img_urls)
				
		return new_data
	
	elif r.status_code == 304:
		return 304


def download_img(img_url):
	try:
		img_folder = str(Path.home())+ "/.underthebar/temp/"
		file_name = img_url.split("/")[-1]
		print("start_img: "+file_name)
		if not os.path.exists(img_folder+file_name):
			response = requests.get(img_url, stream=True)
			with open(img_folder+file_name, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
			del response
		print("end_img: "+file_name)
	except Exception as e:
		print(e)

#	
# Likes, or unlikes, a workout with the given id	
#
def like_workout(workout_id, like_it):
	print("like the workout", workout_id, like_it)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Check if the file already exists, if it does we'll send the server the Etag so we only get an update
	update_data = None
	if os.path.exists(user_folder+"/"+filename):	
		with open(user_folder+"/"+filename, 'r') as file:
			update_data = json.load(file)
		headers["if-none-match"] = update_data["Etag"]
	
	# Now finally do the request for the update. If new update then put that in the file and return 200, else return 304
	s = requests.Session()
	r = s.get(update_url, headers=headers)
	if r.status_code == 200:
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		with open(user_folder+"/"+filename, 'w') as f:
			json.dump(new_data, f)
			
			
		# IF ACCOUNT UPDATED WE ALSO WILL RE-FETCH PROFILE IMAGE
		if to_update == "account":
			try:
				if "profile_pic" in data:
					imageurl = data["profile_pic"]
					response = requests.get(imageurl, stream=True)
					if response.status_code == 200:
						with open(user_folder+"/profileimage", 'wb') as out_file:
							shutil.copyfileobj(response.raw, out_file)
					print("updated profile pic")
			except:	
				pass
			
		return 200
	elif r.status_code == 304:
		return 304

#
# Batch downloads JSON workout files
# This should be used when wanting to bulk download workout files.
# It finds the highest Hevy index in existing downloaded files and requests all new files after that index
# Hevy returns a number of workout files. Idea is to keep calling this until Hevy doesn't return anything.
#
def batch_download():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing workout data
	try:
		from modules import client_storage
	except ImportError:
		return 500, False

	# Create the headers to be used
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token	
	
	# Get all workout data from client storage
	workout_data_dict = client_storage.get_workout_data()
	
	startIndex = 0
	# Find the highest index in existing workouts
	if workout_data_dict:
		for workout_id, workout in workout_data_dict.items():
			if "index" in workout:
				temp_index = workout["index"]
				if temp_index >= startIndex:
					startIndex = temp_index + 1 # make the start index one after the largest we have
	
	# Now finally do the request for workout files		
	s = requests.Session()	
	r = s.get("https://api.hevyapp.com/workouts_batch/"+str(startIndex), headers=headers)
	if r.status_code == 200:
		data = r.json()
		
		havesome = False
		for new_workout in data:
			havesome = True
			workout_id = new_workout['id']
			
			# Save to client-side storage
			client_storage.store_workout_data(workout_id, new_workout)
			
			print("new workout", workout_id)

		# return 200 and a boolean indicating whether Hevy returned new files
		return 200, havesome
	else:
		return r.status_code, False

#
# This uploads all local workout ids and when they were last updated, hevy then returns any changes that have been made on server	
# This should be used when just wanting to get the most recent updates
# It seems inefficient when there are lots of workouts, but I guess any file could be updated at any time...
# Hevy returns isMore indicating whether this should be rerun to collect more updates
#
def workouts_sync_batch():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing workout data
	try:
		from modules import client_storage
		from modules.client_storage import WORKOUT_DATA_KEY
		import streamlit as st
	except ImportError:
		return 500, False
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Get all workout data from client storage
	workout_data_dict = client_storage.get_workout_data()
	
	# Go through all workouts and compile the workout ID and when it was updated
	existing_data = {}
	if workout_data_dict:
		for workout_id, workout_data in workout_data_dict.items():
			if 'id' in workout_data and 'updated_at' in workout_data:
				existing_data[workout_data['id']] = workout_data['updated_at']
	
	# Post our existing data that we have compiled, and see what gets returned
	s = requests.Session()
	r = s.post('https://api.hevyapp.com/workouts_sync_batch', data=json.dumps(existing_data), headers=headers)
	json_content = r.json()	

	# Save any updated workouts to client-side storage
	for updated_workout in json_content['updated']:
		workout_id = updated_workout['id']
		client_storage.store_workout_data(workout_id, updated_workout)
		print("updated workout", workout_id)
		
	# Remove any deleted workouts from client-side storage
	for deleted_workout in json_content['deleted']:
		if WORKOUT_DATA_KEY in st.session_state and deleted_workout in st.session_state[WORKOUT_DATA_KEY]:
			del st.session_state[WORKOUT_DATA_KEY][deleted_workout]
			print("deleted workout", deleted_workout)
		
	# Do we need to make this API call again because there is more data available???
	update = False
	if json_content['isMore'] == True:
		update = True	
	
	return (200, update)


#
# Similar to workouts sync batch but for saved routines
#
def routines_sync_batch():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403, False
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Import client_storage module for storing routine data
	try:
		from modules import client_storage
		from modules.client_storage import ROUTINE_DATA_KEY
		import streamlit as st
	except ImportError:
		return 500, False
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Get all routine data from client storage
	routine_data_dict = client_storage.get_routine_data()
	
	# Go through all routines and compile the routine ID and when it was updated
	existing_data = {}
	if routine_data_dict:
		for routine_id, routine_data in routine_data_dict.items():
			if 'id' in routine_data and 'updated_at' in routine_data:
				existing_data[routine_data['id']] = routine_data['updated_at']
	
	# Post our existing data that we have compiled, and see what gets returned
	s = requests.Session()
	r = s.post('https://api.hevyapp.com/routines_sync_batch', data=json.dumps(existing_data), headers=headers)
	json_content = r.json()	
		
	# Save any updated routines to client-side storage
	for updated_routine in json_content['updated']:
		routine_id = updated_routine['id']
		client_storage.store_routine_data(routine_id, updated_routine)
		print("updated routine", routine_id)
		
	# Remove any deleted routines from client-side storage
	for deleted_routine in json_content['deleted']:
		if ROUTINE_DATA_KEY in st.session_state and deleted_routine in st.session_state[ROUTINE_DATA_KEY]:
			del st.session_state[ROUTINE_DATA_KEY][deleted_routine]
			print("deleted routine", deleted_routine)
		
	# Do we need to make this API call again because there is more data available???
	update = False
	if json_content['isMore'] == True:
		update = True	
	
	return (200, update)

#
# Upload an updated workout
#
def put_routine(the_json, routine_id=None):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	
#	# Workouts subfolder	
#	workouts_folder = user_folder + "/workouts"
#	routines_folder = user_folder + "/routines"
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token

	#return 200
	s = requests.Session()
	#print('https://api.hevyapp.com/routine/'+routine_id)
	#print(the_json)
	
	r = None
	if routine_id == None:
		r = s.post('https://api.hevyapp.com/routine/', data=json.dumps(the_json), headers=headers)
	else:
		r = s.put('https://api.hevyapp.com/routine/'+routine_id, data=json.dumps(the_json), headers=headers)
	return r.status_code
	#return 400

def delete_routine(routine_id):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	s = requests.Session()	
	r = s.delete('https://api.hevyapp.com/routine/'+routine_id, headers=headers)
	return r.status_code, False

#	
# Get the Hevy workout feed starting from workout with given index, returns json data
#
def feed_workouts_paged(start_from):
	print("feed_workouts_paged",start_from)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# workout image stuff, set folder, delete old images
	img_folder = str(Path.home())+ "/.underthebar/temp/"
	if not os.path.exists(img_folder):
		os.makedirs(img_folder)
	# its probably a bit much to do this every time, I'll put it somewhere else.
	#for f in os.listdir(img_folder):
	#	if os.stat(os.path.join(img_folder,f)).st_mtime < time.time() - 14 * 86400:
	#		os.remove(os.path.join(img_folder,f))
			
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/feed_workouts_paged/"
	if start_from != 0:
		url = url + str(start_from)
	
	# Do the request
	s = requests.Session()	
	r = s.get(url, headers=headers)
	if r.status_code == 200:
	
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		
		# this bit is for downloading feed workout images, request in parallel
		img_urls = []
		for workout in data["workouts"]:
			for img_url in workout["image_urls"]:
				img_urls.append(img_url)
		
		#with concurrent.futures.ThreadPoolExecutor() as exector : 
		#	exector.map(download_img, img_urls)
		# above 2 lines waited for threads to complete, this just starts them and carries on.
		exector =  concurrent.futures.ThreadPoolExecutor() 
		exector.map(download_img, img_urls)
				
		return new_data
	
	elif r.status_code == 304:
		return 304


def download_img(img_url):
	try:
		img_folder = str(Path.home())+ "/.underthebar/temp/"
		file_name = img_url.split("/")[-1]
		print("start_img: "+file_name)
		if not os.path.exists(img_folder+file_name):
			response = requests.get(img_url, stream=True)
			with open(img_folder+file_name, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
			del response
		print("end_img: "+file_name)
	except Exception as e:
		print(e)

#	
# Likes, or unlikes, a workout with the given id	
#
def like_workout(workout_id, like_it):
	print("like the workout", workout_id, like_it)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/workout/like/"+workout_id
	if not like_it:
		url = "https://api.hevyapp.com/workout/unlike/"+workout_id
	
	s = requests.Session()	
	r = s.post(url, headers=headers)
	
	return r.status_code
	
	
#
# List of friends, cli only atm
#	
def friends():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/following/lazy_steve"	
	s = requests.Session()	
	r = s.get(url, headers=headers)	
	following_data = r.json()
	following = []
	for datum in following_data:
		following.append(datum['username'])
	
	url = "https://api.hevyapp.com/followers/lazy_steve"	
	r = s.get(url, headers=headers)	
	followers_data = r.json()
	follower = []
	for datum in followers_data:
		follower.append(datum['username'])
	
	mutual_friend = []
	follow_only = []
	not_follow = []
	for follow in following:
		if follow in follower:
			mutual_friend.append(follow)
		else:
			follow_only.append(follow)
	for follow in follower:
		if follow not in following:
			not_follow.append(follow)
			
	print("Mutual Friends:")
	print(mutual_friend)
	print("\nYou Folllow:")
	print(follow_only)
	print("\nFollowing You:")
	print(not_follow)