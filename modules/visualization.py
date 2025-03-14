import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_workout_frequency_chart(workout_days):
    """
    Create a bar chart showing workout frequency by day of week
    
    Args:
        workout_days (pd.DataFrame): DataFrame containing workout days
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    workout_days = workout_days.copy()
    workout_days.loc[:, 'day_of_week'] = workout_days['start_time'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = workout_days['day_of_week'].value_counts().reindex(day_order).fillna(0)
    
    fig = px.bar(x=day_counts.index, y=day_counts.values, 
                labels={'x': 'Day of Week', 'y': 'Number of Workouts'},
                color=day_counts.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    
    return fig

def create_workout_duration_chart(workout_duration_df):
    """
    Create a line chart showing workout duration trend or volume trend
    
    Args:
        workout_duration_df (pd.DataFrame): DataFrame containing workout durations or volumes
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    # Check if the DataFrame has workout_duration column
    if 'workout_duration' in workout_duration_df.columns:
        y_column = 'workout_duration'
        y_label = 'Duration (minutes)'
    # If not, check if it has volume column (for muscle group progress)
    elif 'volume' in workout_duration_df.columns:
        y_column = 'volume'
        y_label = 'Total Volume (kg)'
    else:
        raise ValueError("DataFrame must contain either 'workout_duration' or 'volume' column")
    
    # Check if title column exists for color grouping
    if 'title' in workout_duration_df.columns:
        fig = px.line(workout_duration_df, x='workout_date', y=y_column, color='title',
                    labels={'workout_date': 'Date', y_column: y_label, 'title': 'Workout Type'},
                    markers=True)
    else:
        fig = px.line(workout_duration_df, x='workout_date', y=y_column,
                    labels={'workout_date': 'Date', y_column: y_label},
                    markers=True)
    
    fig.update_layout(height=400)
    
    return fig

def create_workout_type_pie_chart(filtered_df):
    """
    Create a pie chart showing workout type distribution
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    workout_type_counts = filtered_df['title'].value_counts()
    fig = px.pie(values=workout_type_counts.values, names=workout_type_counts.index, hole=0.4)
    fig.update_layout(height=400)
    
    return fig

def create_exercise_frequency_chart(filtered_df, limit=15):
    """
    Create a bar chart showing most common exercises
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        limit (int): Number of exercises to show
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    exercise_counts = filtered_df['exercise_title'].value_counts().head(limit)
    fig = px.bar(x=exercise_counts.index, y=exercise_counts.values,
                labels={'x': 'Exercise', 'y': 'Count'},
                color=exercise_counts.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500, xaxis_tickangle=-45)
    
    return fig

def create_exercise_volume_chart(filtered_df, limit=15):
    """
    Create a bar chart showing exercise volume by type
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        limit (int): Number of exercises to show
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    exercise_volume = filtered_df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(limit)
    fig = px.bar(x=exercise_volume.index, y=exercise_volume.values,
                labels={'x': 'Exercise', 'y': 'Total Volume (kg)'},
                color=exercise_volume.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500, xaxis_tickangle=-45)
    
    return fig

def create_exercise_rpe_chart(filtered_df, limit=15):
    """
    Create a bar chart showing average RPE by exercise
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        limit (int): Number of exercises to show
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object or None if no RPE data
    """
    rpe_df = filtered_df[filtered_df['rpe'].notna()]
    if not rpe_df.empty:
        avg_rpe = rpe_df.groupby('exercise_title')['rpe'].mean().sort_values(ascending=False).head(limit)
        fig = px.bar(x=avg_rpe.index, y=avg_rpe.values,
                    labels={'x': 'Exercise', 'y': 'Average RPE'},
                    color=avg_rpe.values,
                    color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=500, xaxis_tickangle=-45)
        return fig
    return None

def create_progress_charts(progress_df):
    """
    Create progress tracking charts for a specific exercise
    
    Args:
        progress_df (pd.DataFrame): DataFrame containing exercise progress data
        
    Returns:
        tuple: (weight_fig, volume_fig, reps_fig) - Plotly figure objects or None
    """
    progress_df = progress_df.sort_values('start_time')
    
    # Filter for normal sets only (exclude warmup, etc.)
    normal_sets = progress_df[progress_df['set_type'] == 'normal']
    
    weight_fig = None
    volume_fig = None
    reps_fig = None
    
    if not normal_sets.empty and normal_sets['weight_kg'].notna().any():
        # Group by date and get max weight
        max_weight_by_date = normal_sets.groupby('workout_date')['weight_kg'].max().reset_index()
        
        weight_fig = px.line(max_weight_by_date, x='workout_date', y='weight_kg',
                    labels={'workout_date': 'Date', 'weight_kg': 'Max Weight (kg)'},
                    markers=True)
        weight_fig.update_layout(height=400)
        
        # Volume progression (weight * reps)
        volume_by_date = normal_sets.groupby('workout_date')['volume'].sum().reset_index()
        
        volume_fig = px.line(volume_by_date, x='workout_date', y='volume',
                    labels={'workout_date': 'Date', 'volume': 'Total Volume (kg)'},
                    markers=True)
        volume_fig.update_layout(height=400)
        
        # Rep progression
        max_reps_by_date = normal_sets.groupby('workout_date')['reps'].max().reset_index()
        
        reps_fig = px.line(max_reps_by_date, x='workout_date', y='reps',
                    labels={'workout_date': 'Date', 'reps': 'Max Reps'},
                    markers=True)
        reps_fig.update_layout(height=400)
    
    return weight_fig, volume_fig, reps_fig

def create_muscle_volume_chart(filtered_df):
    """
    Create a bar chart showing volume by muscle group
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    muscle_volume = filtered_df.groupby('muscle_group')['volume'].sum().sort_values(ascending=False)
    
    # Clean up muscle group names for display
    muscle_volume.index = muscle_volume.index.map(lambda x: x.replace('_', ' ').title())
    
    fig = px.bar(x=muscle_volume.index, y=muscle_volume.values,
                labels={'x': 'Muscle Group', 'y': 'Total Volume (kg)'},
                color=muscle_volume.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    
    return fig

def create_muscle_frequency_chart(filtered_df):
    """
    Create a bar chart showing workout frequency by muscle group
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    muscle_freq = filtered_df.groupby(['workout_date', 'muscle_group']).size().reset_index(name='count')
    muscle_count = muscle_freq.groupby('muscle_group').size().sort_values(ascending=False)
    
    # Clean up muscle group names for display
    muscle_count.index = muscle_count.index.map(lambda x: x.replace('_', ' ').title())
    
    fig = px.bar(x=muscle_count.index, y=muscle_count.values,
                labels={'x': 'Muscle Group', 'y': 'Number of Workouts'},
                color=muscle_count.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    
    return fig

def create_muscle_balance_chart(filtered_df):
    """
    Create a pie chart showing muscle balance analysis
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    # Group opposing muscle groups for balance analysis
    opposing_pairs = {
        'Push': ['chest', 'shoulders', 'triceps'],
        'Pull': ['lats', 'upper_back', 'biceps'],
        'Lower': ['quadriceps', 'hamstrings', 'calves'],
        'Core': ['abdominals', 'lower_back']
    }
    
    # Calculate volume for each group
    group_volumes = {}
    for group, muscles in opposing_pairs.items():
        group_volumes[group] = filtered_df[filtered_df['muscle_group'].isin(muscles)]['volume'].sum()
    
    # Create pie chart for muscle balance
    fig = px.pie(values=list(group_volumes.values()), names=list(group_volumes.keys()),
                title='Training Volume Distribution by Muscle Group Category',
                hole=0.4)
    fig.update_layout(height=500)
    
    return fig

def create_equipment_volume_chart(filtered_df):
    """
    Create a bar chart showing volume by equipment type
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    equipment_volume = filtered_df.groupby('equipment_category')['volume'].sum().sort_values(ascending=False)
    
    # Clean up equipment names for display
    equipment_volume.index = equipment_volume.index.map(lambda x: x.replace('_', ' ').title())
    
    fig = px.bar(x=equipment_volume.index, y=equipment_volume.values,
                labels={'x': 'Equipment Type', 'y': 'Total Volume (kg)'},
                color=equipment_volume.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    
    return fig

def create_equipment_exercise_chart(filtered_df):
    """
    Create a bar chart showing exercise count by equipment type
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame containing workout data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    equipment_exercises = filtered_df.groupby(['equipment_category', 'exercise_title']).size().reset_index(name='count')
    equipment_exercise_count = equipment_exercises.groupby('equipment_category').size().sort_values(ascending=False)
    
    # Clean up equipment names for display
    equipment_exercise_count.index = equipment_exercise_count.index.map(lambda x: x.replace('_', ' ').title())
    
    fig = px.bar(x=equipment_exercise_count.index, y=equipment_exercise_count.values,
                labels={'x': 'Equipment Type', 'y': 'Number of Exercises'},
                color=equipment_exercise_count.values,
                color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    
    return fig