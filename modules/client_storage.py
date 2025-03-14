import streamlit as st
import json
import base64

# Define storage keys
AUTH_TOKEN_KEY = "hevy_auth_token"
USER_ID_KEY = "hevy_user_id"
WORKOUT_DATA_KEY = "hevy_workout_data"
ACCOUNT_DATA_KEY = "hevy_account_data"
WORKOUT_COUNT_KEY = "hevy_workout_count"
ROUTINE_DATA_KEY = "hevy_routine_data"
PROFILE_IMAGE_KEY = "hevy_profile_image"

def store_auth_data(auth_token, user_id):
    """
    Store authentication data in client-side storage
    
    Args:
        auth_token (str): Authentication token from Hevy API
        user_id (str): User ID from Hevy API
        
    Returns:
        bool: True if storage successful
    """
    try:
        st.session_state[AUTH_TOKEN_KEY] = auth_token
        st.session_state[USER_ID_KEY] = user_id
        return True
    except Exception as e:
        st.error(f"Error storing authentication data: {e}")
        return False

def get_auth_data():
    """
    Retrieve authentication data from client-side storage
    
    Returns:
        tuple: (auth_token, user_id) or (None, None) if not found
    """
    auth_token = st.session_state.get(AUTH_TOKEN_KEY)
    user_id = st.session_state.get(USER_ID_KEY)
    return auth_token, user_id

def clear_auth_data():
    """
    Clear authentication data from client-side storage
    
    Returns:
        bool: True if clearing successful
    """
    try:
        if AUTH_TOKEN_KEY in st.session_state:
            del st.session_state[AUTH_TOKEN_KEY]
        if USER_ID_KEY in st.session_state:
            del st.session_state[USER_ID_KEY]
        return True
    except Exception as e:
        st.error(f"Error clearing authentication data: {e}")
        return False

def store_workout_data(workout_id, workout_data):
    """
    Store workout data in client-side storage
    
    Args:
        workout_id (str): ID of the workout
        workout_data (dict): Workout data to store
        
    Returns:
        bool: True if storage successful
    """
    try:
        # Initialize workout data dictionary if it doesn't exist
        if WORKOUT_DATA_KEY not in st.session_state:
            st.session_state[WORKOUT_DATA_KEY] = {}
        
        # Store workout data with workout ID as key
        st.session_state[WORKOUT_DATA_KEY][workout_id] = workout_data
        return True
    except Exception as e:
        st.error(f"Error storing workout data: {e}")
        return False

def get_workout_data(workout_id=None):
    """
    Retrieve workout data from client-side storage
    
    Args:
        workout_id (str, optional): ID of specific workout to retrieve. If None, returns all workouts.
        
    Returns:
        dict or None: Workout data or None if not found
    """
    try:
        workout_data = st.session_state.get(WORKOUT_DATA_KEY, {})
        if workout_id:
            return workout_data.get(workout_id)
        return workout_data
    except Exception as e:
        st.error(f"Error retrieving workout data: {e}")
        return None

def store_account_data(account_data, etag):
    """
    Store account data in client-side storage
    
    Args:
        account_data (dict): Account data from Hevy API
        etag (str): ETag for data versioning
        
    Returns:
        bool: True if storage successful
    """
    try:
        st.session_state[ACCOUNT_DATA_KEY] = {
            "data": account_data,
            "Etag": etag
        }
        return True
    except Exception as e:
        st.error(f"Error storing account data: {e}")
        return False

def get_account_data():
    """
    Retrieve account data from client-side storage
    
    Returns:
        dict or None: Account data or None if not found
    """
    return st.session_state.get(ACCOUNT_DATA_KEY)

def store_workout_count(workout_count, etag):
    """
    Store workout count data in client-side storage
    
    Args:
        workout_count (dict): Workout count data from Hevy API
        etag (str): ETag for data versioning
        
    Returns:
        bool: True if storage successful
    """
    try:
        st.session_state[WORKOUT_COUNT_KEY] = {
            "data": workout_count,
            "Etag": etag
        }
        return True
    except Exception as e:
        st.error(f"Error storing workout count data: {e}")
        return False

def get_workout_count():
    """
    Retrieve workout count data from client-side storage
    
    Returns:
        dict or None: Workout count data or None if not found
    """
    return st.session_state.get(WORKOUT_COUNT_KEY)

def store_routine_data(routine_id, routine_data):
    """
    Store routine data in client-side storage
    
    Args:
        routine_id (str): ID of the routine
        routine_data (dict): Routine data to store
        
    Returns:
        bool: True if storage successful
    """
    try:
        # Initialize routine data dictionary if it doesn't exist
        if ROUTINE_DATA_KEY not in st.session_state:
            st.session_state[ROUTINE_DATA_KEY] = {}
        
        # Store routine data with routine ID as key
        st.session_state[ROUTINE_DATA_KEY][routine_id] = routine_data
        return True
    except Exception as e:
        st.error(f"Error storing routine data: {e}")
        return False

def get_routine_data(routine_id=None):
    """
    Retrieve routine data from client-side storage
    
    Args:
        routine_id (str, optional): ID of specific routine to retrieve. If None, returns all routines.
        
    Returns:
        dict or None: Routine data or None if not found
    """
    try:
        routine_data = st.session_state.get(ROUTINE_DATA_KEY, {})
        if routine_id:
            return routine_data.get(routine_id)
        return routine_data
    except Exception as e:
        st.error(f"Error retrieving routine data: {e}")
        return None

def store_profile_image(image_data):
    """
    Store profile image in client-side storage
    
    Args:
        image_data (bytes): Profile image data as bytes
        
    Returns:
        bool: True if storage successful
    """
    try:
        # Encode image data as base64 string for storage
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        st.session_state[PROFILE_IMAGE_KEY] = encoded_image
        return True
    except Exception as e:
        st.error(f"Error storing profile image: {e}")
        return False

def get_profile_image():
    """
    Retrieve profile image from client-side storage
    
    Returns:
        bytes or None: Profile image data as bytes or None if not found
    """
    try:
        encoded_image = st.session_state.get(PROFILE_IMAGE_KEY)
        if encoded_image:
            return base64.b64decode(encoded_image)
        return None
    except Exception as e:
        st.error(f"Error retrieving profile image: {e}")
        return None

def clear_all_data():
    """
    Clear all stored data from client-side storage
    
    Returns:
        bool: True if clearing successful
    """
    try:
        keys = [AUTH_TOKEN_KEY, USER_ID_KEY, WORKOUT_DATA_KEY, ACCOUNT_DATA_KEY, 
                WORKOUT_COUNT_KEY, ROUTINE_DATA_KEY, PROFILE_IMAGE_KEY]
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
        return True
    except Exception as e:
        st.error(f"Error clearing all data: {e}")
        return False