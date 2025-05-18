import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import cdsapi
    print("Successfully imported cdsapi")
except ImportError as e:
    print(f"Error importing cdsapi: {str(e)}")
    print("Please run: pip install cdsapi")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("Successfully imported python-dotenv")
except ImportError as e:
    print(f"Error importing python-dotenv: {str(e)}")
    print("Please run: pip install python-dotenv")
    sys.exit(1)

def test_copernicus_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if API key is set
        api_key = os.getenv("COPERNICUS_API_KEY")
        if not api_key:
            print("Error: COPERNICUS_API_KEY not found in environment variables")
            return False
            
        print("Initializing CDS API client...")
        c = cdsapi.Client()
        
        print("Making test request to Copernicus CDS API...")
        result = c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': '2m_temperature',
                'year': '2023',
                'month': '12',
                'day': '01',
                'time': '12:00',
                'area': [
                    40,
                    -74,
                    39,
                    -73,
                ],
                'format': 'netcdf',
            }
        )
        
        print("Successfully connected to Copernicus CDS API!")
        return True
    except Exception as e:
        print(f"Error connecting to Copernicus CDS API: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if you have a valid API key in your .cdsapirc file")
        print("2. Verify your internet connection")
        print("3. Make sure you have accepted the terms of use for the dataset")
        return False

if __name__ == "__main__":
    print("Starting Copernicus API connection test...")
    test_copernicus_connection() 