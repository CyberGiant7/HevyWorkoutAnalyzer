import pandas as pd
import os
import json
import glob
from datetime import datetime
import streamlit as st

@st.cache_data
def load_workout_data(user_folder):
    """
    Load workout data from client-side storage
    
    Args:
        user_folder (str): Path to the user's folder (kept for compatibility)
        
    Returns:
        pd.DataFrame: DataFrame containing workout data
    """
    # Get data from client-side storage
    from modules import client_storage
    
    all_workout_data = []
    
    # Get all workout data from client storage
    workout_data_dict = client_storage.get_workout_data()
    
    if not workout_data_dict:
        return pd.DataFrame()
    
    # Process each workout in the dictionary
    for workout_id, workout in workout_data_dict.items():
        try:
            # Basic workout info
            workout_title = workout.get('name', 'Untitled')
            workout_start = workout.get('start_time', 0)
            workout_end = workout.get('end_time', 0)
            workout_description = workout.get('description', '')
            
            # Convert timestamps to datetime
            start_time = datetime.fromtimestamp(workout_start)
            end_time = datetime.fromtimestamp(workout_end)
            
            # Process exercises
            for exercise in workout.get('exercises', []):
                exercise_title = exercise.get('title', 'Unknown Exercise')
                superset_id = exercise.get('superset_id', None)
                exercise_notes = exercise.get('notes', '')
                muscle_group = exercise.get('muscle_group', 'other')
                other_muscles = exercise.get('other_muscles', [])
                exercise_type = exercise.get('exercise_type', 'weight_reps')
                equipment_category = exercise.get('equipment_category', 'other')
                
                # Process sets
                for i, set_data in enumerate(exercise.get('sets', [])):
                    set_type = set_data.get('indicator', 'normal')
                    weight = set_data.get('weight_kg', None)
                    reps = set_data.get('reps', None)
                    distance = set_data.get('distance_meters', None)
                    duration = set_data.get('duration_seconds', None)
                    rpe = set_data.get('rpe', None)
                    
                    # Create a row for this set
                    row = {
                        'title': workout_title,
                        'start_time': start_time.strftime('%d %b %Y, %H:%M'),
                        'end_time': end_time.strftime('%d %b %Y, %H:%M'),
                        'description': workout_description,
                        'exercise_title': exercise_title,
                        'superset_id': superset_id,
                        'exercise_notes': exercise_notes,
                        'muscle_group': muscle_group,
                        'other_muscles': other_muscles,
                        'exercise_type': exercise_type,
                        'equipment_category': equipment_category,
                        'set_index': i,
                        'set_type': set_type,
                        'weight_kg': weight,
                        'reps': reps,
                        'distance_km': distance,
                        'duration_seconds': duration,
                        'rpe': rpe
                    }
                    all_workout_data.append(row)
        except Exception as e:
            st.error(f"Error processing workout {workout_id}: {e}")
    
    if not all_workout_data:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(all_workout_data)
    
    # Convert date columns to datetime
    df['start_time'] = pd.to_datetime(df['start_time'], format='%d %b %Y, %H:%M')
    df['end_time'] = pd.to_datetime(df['end_time'], format='%d %b %Y, %H:%M')
    
    # Calculate workout duration in minutes
    df['workout_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    
    # Extract date only for grouping
    df['workout_date'] = df['start_time'].dt.date
    
    # Calculate volume (weight * reps) where applicable
    df['volume'] = df['weight_kg'] * df['reps']
    
    return df

def filter_data(df, date_range=None, workout_types=None, exercises=None):
    """
    Filter workout data based on date range, workout types, and exercises
    
    Args:
        df (pd.DataFrame): DataFrame containing workout data
        date_range (list): List containing start and end date
        workout_types (list): List of workout types to include
        exercises (list): List of exercises to include
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Apply date range filter
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['start_time'].dt.date >= start_date) & 
                                (filtered_df['start_time'].dt.date <= end_date)]
    
    # Apply workout type filter
    if workout_types and len(workout_types) > 0:
        filtered_df = filtered_df[filtered_df['title'].isin(workout_types)]
    
    # Apply exercise filter
    if exercises and len(exercises) > 0:
        filtered_df = filtered_df[filtered_df['exercise_title'].isin(exercises)]
    
    return filtered_df