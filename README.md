# Hevy Workout Analyzer

A powerful data analysis tool for Hevy workout exports that helps you track and visualize your fitness progress. This application connects to your Hevy account, syncs your workout data, and provides comprehensive analytics to help you understand your training patterns and progress over time.

![Hevy Workout Analyzer](https://img.shields.io/badge/Fitness-Analytics-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.43.2-red)

**Live App:** [https://hevyworkoutanalyzer.streamlit.app/](https://hevyworkoutanalyzer.streamlit.app/)

## Features

- **Hevy Account Integration**: Log in with your Hevy credentials to automatically sync your workout data
- **Comprehensive Data Analysis**: Analyze workout trends, patterns, and performance metrics
- **Interactive Visualizations**: View your progress through dynamic charts and graphs
- **Exercise Statistics**: Get detailed statistics for each exercise you perform
- **Personal Records Tracking**: Automatically identify and highlight your personal bests
- **Workout Insights**: Gain insights into your training frequency, volume, and intensity

## Prerequisites

- Python 3.12 or higher
- Required Python packages (listed in `requirements.txt`):
  - pandas (2.2.3)
  - streamlit (1.43.2)
  - plotly (6.0.0)
  - matplotlib (3.10.1)
  - numpy (2.2.3)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/HevyWorkoutAnalyzer.git
cd HevyWorkoutAnalyzer
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

    ```bash
    streamlit run app.py
    ```

2. Log in with your Hevy account credentials when prompted

3. Once logged in, your workout data will be automatically synced

4. Navigate through the different analysis sections in the sidebar:
   - Dashboard Overview
   - Exercise Analysis
   - Workout Trends
   - Personal Records
   - Body Measurements (if available)

5. Use the "Sync Data" button in the sidebar to refresh your workout data at any time

## How It Works

The Hevy Workout Analyzer uses the Hevy API to securely access your workout data. The application:

1. Authenticates with your Hevy credentials
2. Retrieves your workout history
3. Processes and analyzes the data using pandas
4. Generates interactive visualizations with plotly and matplotlib
5. Presents the results in a user-friendly Streamlit interface

All data is stored locally in your browser's session storage for privacy and security.

## Data Analysis Features

- **Workout Frequency Analysis**: See which days of the week you train most frequently
- **Volume Progression Tracking**: Track how your training volume changes over time
- **Exercise Performance Metrics**: Analyze your performance for specific exercises
- **Personal Record Tracking**: Automatically identify and celebrate new personal bests
- **Rest Time Analysis**: Understand your rest patterns between sets
- **Workout Duration Trends**: Track how your workout duration changes over time
- **Muscle Group Balance**: Visualize how you distribute your training across muscle groups

## Project Structure

```text
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── modules/               # Application modules
│   ├── __init__.py        # Package initialization
│   ├── auth.py            # Authentication functionality
│   ├── client_storage.py  # Local data storage management
│   ├── data.py            # Data processing and analysis
│   ├── hevy_api.py        # Hevy API integration
│   ├── ui.py              # User interface components
│   └── visualization.py   # Data visualization functions
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Hevy App](https://www.hevyapp.com/) for providing the workout tracking platform
- Contributors and maintainers of this project
- The Streamlit team for their excellent data app framework
- The Python data science community for the powerful tools that make this analysis possible

## Contact

For questions and feedback, please open an issue in the GitHub repository.
