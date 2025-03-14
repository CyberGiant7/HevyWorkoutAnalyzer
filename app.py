import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from modules import auth, data, ui, visualization, hevy_api

# Set up the app
ui.set_page_config()
ui.apply_custom_css()
ui.display_header()

# Main app logic
is_logged_in, user_folder = auth.check_login_status()

if not is_logged_in:
    # Login form
    username, password, submit_button = ui.display_login_form()
    
    if submit_button:
        if username and password:
            with st.spinner("Logging in..."):
                status_code = auth.login(username, password)
                if status_code == 200:
                    st.success("Login successful! Your workouts have been synced.")
                    st.rerun()
                else:
                    st.error(f"Login failed with status code: {status_code}")
        else:
            st.warning("Please enter both username and password")
    
    # Display information about the app
    ui.display_about_section()

else:
    # User is logged in, show the main interface
    
    # Sidebar with sync button and logout option
    sync_clicked, logout_clicked = ui.display_sidebar_data_management()
    
    if sync_clicked:
        with st.spinner("Syncing workouts..."):
            success, message = auth.sync_data()
            if success:
                st.success(message)
                # Clear cache to reload data
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(message)
    
    if logout_clicked:
        if auth.logout():
            st.success("Logged out successfully!")
            st.rerun()
        else:
            st.error("Error logging out")
    
    # Load data
    try:
        df = data.load_workout_data(user_folder)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please make sure you have synced your workout data from Hevy.")
        df = pd.DataFrame()
    
    if not df.empty:
        # Get data for filters
        workout_types = df['title'].unique()
        exercises = df['exercise_title'].unique()
        min_date = df['start_time'].min().date()
        max_date = df['start_time'].max().date()
        
        # Sidebar filters
        date_range, selected_workout_types, selected_exercises = ui.display_sidebar_controls(
            workout_types, exercises, min_date, max_date
        )
        
        # Apply filters
        filtered_df = data.filter_data(df, date_range, selected_workout_types, selected_exercises)
        
        # Main content
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Exercise Analysis", "Progress Tracking", "Workout Details", "Muscle Analysis", "Equipment Analysis"])
        
        with tab1:
            st.markdown('<h2 class="sub-header">Workout Overview</h2>', unsafe_allow_html=True)
            
            # Summary metrics
            total_workouts = filtered_df['workout_date'].nunique()
            total_exercises = filtered_df['exercise_title'].nunique()
            avg_duration = filtered_df.groupby('workout_date')['workout_duration'].first().mean()
            total_volume = filtered_df['volume'].sum()
            
            ui.display_summary_metrics(total_workouts, total_exercises, avg_duration, total_volume)
            
            # Workout frequency by day of week
            st.markdown('<h3>Workout Frequency by Day of Week</h3>', unsafe_allow_html=True)
            workout_days = filtered_df.drop_duplicates('workout_date')
            fig = visualization.create_workout_frequency_chart(workout_days)
            st.plotly_chart(fig, use_container_width=True)
            
            # Workout duration trend
            st.markdown('<h3>Workout Duration Trend</h3>', unsafe_allow_html=True)
            workout_duration_df = filtered_df.drop_duplicates('workout_date')[['workout_date', 'workout_duration', 'title']]
            fig = visualization.create_workout_duration_chart(workout_duration_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Workout type distribution
            st.markdown('<h3>Workout Type Distribution</h3>', unsafe_allow_html=True)
            fig = visualization.create_workout_type_pie_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown('<h2 class="sub-header">Exercise Analysis</h2>', unsafe_allow_html=True)
            
            # Filter by selected exercises if any
            if selected_exercises:
                exercise_df = filtered_df[filtered_df['exercise_title'].isin(selected_exercises)]
            else:
                exercise_df = filtered_df
            
            # Most common exercises
            st.markdown('<h3>Most Common Exercises</h3>', unsafe_allow_html=True)
            fig = visualization.create_exercise_frequency_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Exercise volume by type
            st.markdown('<h3>Exercise Volume by Type</h3>', unsafe_allow_html=True)
            fig = visualization.create_exercise_volume_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Average RPE by exercise
            st.markdown('<h3>Average RPE by Exercise</h3>', unsafe_allow_html=True)
            fig = visualization.create_exercise_rpe_chart(filtered_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No RPE data available in the selected date range.")
        
        with tab3:
            st.markdown('<h2 class="sub-header">Progress Tracking</h2>', unsafe_allow_html=True)
            
            # Select exercise for progress tracking
            progress_exercises = filtered_df['exercise_title'].unique()
            selected_progress_exercise = st.selectbox(
                "Select Exercise to Track Progress",
                options=progress_exercises
            )
            
            if selected_progress_exercise:
                progress_df = filtered_df[filtered_df['exercise_title'] == selected_progress_exercise].copy()
                
                # Create progress charts
                weight_fig, volume_fig, reps_fig = visualization.create_progress_charts(progress_df)
                
                if weight_fig:
                    # Weight progression
                    st.markdown('<h3>Weight Progression</h3>', unsafe_allow_html=True)
                    st.plotly_chart(weight_fig, use_container_width=True)
                    
                    # Volume progression
                    st.markdown('<h3>Volume Progression</h3>', unsafe_allow_html=True)
                    st.plotly_chart(volume_fig, use_container_width=True)
                    
                    # Rep progression
                    st.markdown('<h3>Rep Progression</h3>', unsafe_allow_html=True)
                    st.plotly_chart(reps_fig, use_container_width=True)
                else:
                    st.info(f"No weight data available for {selected_progress_exercise} in the selected date range.")
        
        with tab4:
            st.markdown('<h2 class="sub-header">Workout Details</h2>', unsafe_allow_html=True)
            
            # Group by workout date and title
            workout_dates = filtered_df[['workout_date', 'title']].drop_duplicates().sort_values('workout_date', ascending=False)
            workout_dates['display_date'] = workout_dates['workout_date'].astype(str) + ' - ' + workout_dates['title']
            
            selected_workout = st.selectbox(
                "Select Workout",
                options=workout_dates['display_date'].tolist()
            )
            
            if selected_workout:
                selected_date_str, selected_title = selected_workout.split(' - ', 1)
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                
                workout_detail = filtered_df[(filtered_df['workout_date'] == selected_date) & 
                                            (filtered_df['title'] == selected_title)]
                
                # Workout summary
                start_time = workout_detail['start_time'].min()
                end_time = workout_detail['end_time'].max()
                duration = (end_time - start_time).total_seconds() / 60
                
                st.markdown(f"<h3>Workout Summary</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Date:** {selected_date}")
                with col2:
                    st.markdown(f"**Duration:** {duration:.0f} minutes")
                with col3:
                    st.markdown(f"**Exercises:** {workout_detail['exercise_title'].nunique()}")
                
                # Exercise details
                st.markdown(f"<h3>Exercise Details</h3>", unsafe_allow_html=True)
                
                for exercise in workout_detail['exercise_title'].unique():
                    exercise_data = workout_detail[workout_detail['exercise_title'] == exercise]
                    
                    st.markdown(f"**{exercise}**")
                    
                    # Create a table for sets
                    set_data = []
                    for _, row in exercise_data.iterrows():
                        set_type = row['set_type'].capitalize() if pd.notna(row['set_type']) else ''
                        weight = f"{row['weight_kg']:.1f} kg" if pd.notna(row['weight_kg']) else '-'
                        reps = f"{row['reps']}" if pd.notna(row['reps']) else '-'
                        distance = f"{row['distance_km']/1000:.2f} km" if pd.notna(row['distance_km']) else '-'
                        duration = f"{row['duration_seconds']} sec" if pd.notna(row['duration_seconds']) else '-'
                        rpe = f"{row['rpe']}" if pd.notna(row['rpe']) else '-'
                        
                        set_data.append([f"Set {row['set_index']+1}", set_type, weight, reps, distance, duration, rpe])
                    
                    if set_data:
                        set_df = pd.DataFrame(set_data, columns=['Set', 'Type', 'Weight', 'Reps', 'Distance', 'Duration', 'RPE'])
                        st.dataframe(set_df, use_container_width=True)
                    
                    st.markdown("---")
        
        with tab5:
            st.markdown('<h2 class="sub-header">Muscle Analysis</h2>', unsafe_allow_html=True)
            
            # Summary metrics for muscles
            col1, col2 = st.columns(2)
            
            with col1:
                muscle_count = filtered_df['muscle_group'].nunique()
                st.metric("Muscle Groups Trained", muscle_count)
            
            with col2:
                most_trained = filtered_df['muscle_group'].value_counts().idxmax()
                st.metric("Most Trained Muscle", most_trained.replace('_', ' ').title())
            
            # Volume by muscle group
            st.markdown('<h3>Volume by Muscle Group</h3>', unsafe_allow_html=True)
            fig = visualization.create_muscle_volume_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Workout frequency by muscle group
            st.markdown('<h3>Workout Frequency by Muscle Group</h3>', unsafe_allow_html=True)
            fig = visualization.create_muscle_frequency_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Muscle balance analysis
            st.markdown('<h3>Muscle Balance Analysis</h3>', unsafe_allow_html=True)
            fig = visualization.create_muscle_balance_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Progress over time for selected muscle group
            st.markdown('<h3>Muscle Group Progress Over Time</h3>', unsafe_allow_html=True)
            
            # Get unique muscle groups
            muscle_groups = sorted(filtered_df['muscle_group'].unique())
            muscle_groups = [m.replace('_', ' ').title() for m in muscle_groups]
            
            # Select muscle group for progress tracking
            selected_muscle = st.selectbox(
                "Select Muscle Group to Track Progress",
                options=muscle_groups
            )
            
            if selected_muscle:
                # Convert back to original format for filtering
                original_muscle = selected_muscle.lower().replace(' ', '_')
                muscle_df = filtered_df[filtered_df['muscle_group'] == original_muscle].copy()
                
                if not muscle_df.empty:
                    # Group by date and calculate total volume
                    volume_by_date = muscle_df.groupby('workout_date')['volume'].sum().reset_index()
                    
                    fig = visualization.create_workout_duration_chart(volume_by_date)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No data available for {selected_muscle} in the selected date range.")
        
        with tab6:
            st.markdown('<h2 class="sub-header">Equipment Analysis</h2>', unsafe_allow_html=True)
            
            # Summary metrics for equipment
            col1, col2 = st.columns(2)
            
            with col1:
                equipment_count = filtered_df['equipment_category'].nunique()
                st.metric("Equipment Types Used", equipment_count)
            
            with col2:
                most_used = filtered_df['equipment_category'].value_counts().idxmax()
                st.metric("Most Used Equipment", most_used.replace('_', ' ').title())
            
            # Volume by equipment type
            st.markdown('<h3>Volume by Equipment Type</h3>', unsafe_allow_html=True)
            fig = visualization.create_equipment_volume_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Exercise count by equipment type
            st.markdown('<h3>Exercise Count by Equipment Type</h3>', unsafe_allow_html=True)
            fig = visualization.create_equipment_exercise_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
    
    # Display help in sidebar
    ui.display_sidebar_help()
    
    # Add footer
    ui.display_footer()