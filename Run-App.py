import sys
import os
from streamlit.web import cli as stcli

def main():
    """Run the Streamlit app"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to your Streamlit app
    app_path = os.path.join(script_dir, 'app.py')
    
    # Configure Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
        # Add more options as needed:
        # "--server.headless=true",  # Run without opening browser
        # "--theme.base=dark",       # Dark theme
        # "--server.maxUploadSize=200",  # Max upload size in MB
    ]
    
    # Run Streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()