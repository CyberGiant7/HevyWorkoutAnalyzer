import streamlit as st
from modules import client_storage, hevy_api

def check_login_status():
    """
    Check if user is logged in to Hevy
    
    Returns:
        tuple: (is_logged_in, user_folder) - Boolean indicating login status and user folder path if logged in
    """
    # Check client-side storage
    auth_token, user_id = client_storage.get_auth_data()
    if auth_token and user_id:
        # Create a virtual user_folder path for compatibility with existing code
        virtual_user_folder = f"virtual_user_{user_id}"
        return True, virtual_user_folder
    
    return False, None

def login(username, password):
    """
    Login to Hevy with username and password
    
    Args:
        username (str): Hevy username or email
        password (str): Hevy password
        
    Returns:
        int: Status code (200 for success)
    """
    # Call the Hevy API login function
    status_code = hevy_api.login(username, password)
    
    # If login successful, store auth data in client-side storage
    if status_code == 200:
        # Get auth token and user ID from the API response
        login_status = hevy_api.is_logged_in()
        if login_status[0]:
            auth_token = login_status[2]
            user_id = login_status[1].split('_')[-1] if login_status[1] else ''
            
            # Store in client-side storage
            client_storage.store_auth_data(auth_token, user_id)
            
            # Also store account data if available
            try:
                account_data = hevy_api.update_generic("account")
                if isinstance(account_data, dict) and "data" in account_data:
                    client_storage.store_account_data(account_data["data"], account_data.get("Etag", ""))
                
                # Store workout count data
                workout_count = hevy_api.update_generic("workout_count")
                if isinstance(workout_count, dict) and "data" in workout_count:
                    client_storage.store_workout_count(workout_count["data"], workout_count.get("Etag", ""))
                    
                # Automatically sync workout data after successful login
                with st.spinner("Syncing your workouts..."):
                    sync_success, sync_message = sync_data()
                    if not sync_success:
                        st.warning(f"Could not sync workout data: {sync_message}")
                    # Clear cache to reload data
                    if 'cache_data' in dir(st) and callable(getattr(st, 'cache_data', {}).get('clear', None)):
                        st.cache_data.clear()
            except Exception as e:
                st.warning(f"Could not retrieve all account data: {e}")
    
    return status_code

def logout():
    """
    Logout from Hevy
    
    Returns:
        bool: True if logout successful
    """
    # Clear all client-side storage
    client_storage.clear_all_data()
    return True

def sync_data():
    """
    Sync workout data from Hevy
    
    Returns:
        tuple: (success, message) - Boolean indicating success and status message
    """
    # First try to get any new workouts in a loop until there are no more new workouts
    has_more_workouts = True
    while has_more_workouts:
        status, has_new = hevy_api.batch_download()
        if status != 200:
            return False, f"Error syncing workouts: {status}"
        # If no new workouts were found, exit the loop
        if not has_new:
            has_more_workouts = False
    
    # Then check for updates to existing workouts in a loop until there are no more updates
    has_more_updates = True
    while has_more_updates:
        update_status, need_more = hevy_api.workouts_sync_batch()
        if update_status != 200:
            return False, f"Error syncing workout updates: {update_status}"
        # If no more updates are needed, exit the loop
        if not need_more:
            has_more_updates = False
    
    # Also sync routines in a loop until there are no more routine updates
    has_more_routines = True
    while has_more_routines:
        routine_status, routine_more = hevy_api.routines_sync_batch()
        if routine_status != 200:
            return False, f"Error syncing routines: {routine_status}"
        # If no more routine updates are needed, exit the loop
        if not routine_more:
            has_more_routines = False
    
    return True, "All workout data synced successfully!"