import streamlit as st

def set_page_config():
    """
    Set the page configuration for the Streamlit app
    """
    st.set_page_config(page_title="Hevy Workout Analyzer", page_icon="💪", layout="wide")

def apply_custom_css():
    """
    Apply custom CSS styling to the Streamlit app
    """
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #4B4BFF;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        /* Style for metric cards */
        /* Target the entire metric container element */
        [data-testid="stMetric"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        /* Make sure metric value is properly displayed */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        /* Ensure metric text color */
        [data-testid="stMetricLabel"] {
            color: #333;
        }
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sync-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .sync-button:hover {
            background-color: #45a049;
        }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """
    Display the main header of the app
    """
    st.markdown('<h1 class="main-header">Hevy Workout Analyzer</h1>', unsafe_allow_html=True)

def display_login_form():
    """
    Display the login form for unauthenticated users
    
    Returns:
        tuple: (username, password, submitted) - Form input values and submission status
    """
    # Inject custom CSS
    st.markdown(
        """
        <style>
        /* This targets the container that wraps our content.
           You may need to adjust the selector based on your app's structure. */
        .stContainer > div:first-child {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Use a container to group the login form elements
    with st.container():
        st.subheader("Login to Hevy")
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button(label="Login")
    
    return username, password, submit_button
    
    return username, password, submit_button

def display_about_section():
    """
    Display information about the app for unauthenticated users
    """
    st.markdown("---")
    st.markdown("""
    ## About Hevy Workout Analyzer
    
    This app allows you to analyze your Hevy workout data. Login with your Hevy account to get started.
    
    Features:
    - Sync your workout data directly from Hevy
    - Analyze workout trends and progress
    - Track exercise performance over time
    - View detailed workout statistics
    """)

def display_sidebar_controls(workout_types, exercises, min_date, max_date):
    """
    Display sidebar filters and controls
    
    Args:
        workout_types (list): List of available workout types
        exercises (list): List of available exercises
        min_date (datetime.date): Minimum date in the dataset
        max_date (datetime.date): Maximum date in the dataset
        
    Returns:
        tuple: (date_range, selected_workout_types, selected_exercises) - Selected filter values
    """
    st.sidebar.markdown('## Filters')
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Workout type filter
    selected_workout_types = st.sidebar.multiselect(
        "Workout Types",
        options=workout_types,
        default=workout_types
    )
    
    # Exercise filter
    selected_exercises = st.sidebar.multiselect(
        "Exercises",
        options=exercises,
        default=[]
    )
    
    return date_range, selected_workout_types, selected_exercises

def display_sidebar_data_management():
    """
    Display data management controls in the sidebar
    
    Returns:
        tuple: (sync_clicked, logout_clicked) - Button click states
    """
    st.sidebar.markdown("## Data Management")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        sync_clicked = st.button("Sync Workouts", key="sync_button")
    
    with col2:
        logout_clicked = st.button("Logout", key="logout_button")
    
    return sync_clicked, logout_clicked

def display_sidebar_help():
    """
    Display help information in the sidebar
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("## How to Use")
    st.sidebar.markdown("""
    1. **Sync Workouts**: Click to download your latest workout data from Hevy
    2. **Overview**: See general workout statistics and trends
    3. **Exercise Analysis**: Analyze exercise frequency, volume, and intensity
    4. **Progress Tracking**: Track progress for specific exercises over time
    5. **Workout Details**: View detailed information for each workout session
    """)

def display_summary_metrics(total_workouts, total_exercises, avg_duration, total_volume):
    """
    Display summary metrics in cards
    
    Args:
        total_workouts (int): Total number of workouts
        total_exercises (int): Total number of unique exercises
        avg_duration (float): Average workout duration in minutes
        total_volume (float): Total workout volume in kg
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Workouts", total_workouts)
    
    with col2:
        st.metric("Unique Exercises", total_exercises)
    
    with col3:
        st.metric("Avg. Workout Duration (min)", f"{avg_duration:.1f}")
    
    with col4:
        st.metric("Total Volume (kg)", f"{total_volume:,.0f}")

def display_footer():
    """
    Display the footer of the app
    """
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
        Hevy Workout Analyzer | Created with Streamlit | Powered by Hevy API
    </div>
    """, unsafe_allow_html=True)