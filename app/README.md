# FastAPI Test Case Generator

## Description
This is a FastAPI application that generates test cases using a CREW AI Agent. It provides an API endpoint to generate test cases based on predefined templates.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install fastapi uvicorn requests
   ```

4. Set up logging configuration (if needed):
   Ensure you have a `logging.ini` file in the root directory for logging configuration.

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API at `http://127.0.0.1:8000`.

## API Endpoints

### Root Endpoint
- **GET** `/`
  - Returns a welcome message.

### Generate Test Cases
- **GET** `/generate_testcases`
  - Generates test cases based on the provided templates.
  - Returns a JSON object containing the generated test cases.

## Environment Variables
- `GENAI_RETRY_COUNT`: Number of retries for generating test cases (default is 3).

## Logging
The application uses logging to track events. Configure the logging settings in `logging.ini`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.