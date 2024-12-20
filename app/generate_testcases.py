import os
import requests
import json
import logging
from crewai import Agent, Task, Crew, Process
from typing import Optional, List, Mapping, Any
from dotenv import load_dotenv


load_dotenv()

# Define agents
test_case_generator = Agent(
    role="Software Test Engineer",
    goal="Generate comprehensive test cases based on Jira ticket information",
    backstory="You are an experienced test engineer skilled in creating thorough test cases.",
    allow_delegation=False,
    verbose=True,
)

test_case_reviewer = Agent(
    role="QA Lead",
    goal="Review and improve test cases to increase coverage",
    backstory="You are a detail-oriented QA lead with a keen eye for identifying gaps in test coverage.",
    allow_delegation=False,
    verbose=True,
)

test_case_enhancer = Agent(
    role="Product Analyst",
    goal="Enhance test cases with additional product scenarios",
    backstory="You are a seasoned product analyst with deep understanding of business processes and use cases.",
    allow_delegation=False,
    verbose=True,
)

user_story = """
Title:
As a user, I want to register with a secure and verified account so that I can safely access the application features.

Description:
The user registration process must ensure compliance with password security policies, validate phone numbers based on country code, 
and verify postal codes for accuracy. These measures are designed to improve security and data integrity during the registration process.

Acceptance Criteria:

Password Policy Enforcement:

Password must:
Be at least 8 characters long.
Include at least one uppercase letter, one lowercase letter, one digit, and one special character (e.g., @, #, $).
Not contain the user’s first name, last name, or email address.
Provide real-time feedback on password strength during registration.
Display a user-friendly error message if the password fails validation.

Phone Number Validation:
The phone number field must:
Accept numbers only in a valid format based on the user’s selected country code.
Provide country code options via a dropdown or auto-detection based on IP.
Use a backend service or library to validate the phone number format (e.g., libphonenumber).
Display an appropriate error message if the phone number is invalid.

Postal Code Validation:
The postal code field must:
Validate the format according to the user's selected country.
Provide real-time validation feedback.
Display an error message if the postal code is invalid or mismatched with the country.
General Registration Flow:

Required Fields:
First Name
Last Name
Email Address
Password
Phone Number
Country
Postal Code
Optional Fields:
Middle Name
Alternative Phone Number
Registration will only proceed if all validations pass.

User Experience:
If any validation fails, the corresponding field should be highlighted, and an actionable error message should be displayed.
Allow users to reattempt corrections without re-entering all data.
Tasks:

Frontend Development:
Implement UI for the registration form with all required fields.
Add real-time validation for password, phone number, and postal code fields.

Backend Development:
Create APIs to handle user registration, including validation of password, phone number, and postal code.
Integrate third-party libraries/services for phone number and postal code validation.

Testing:
Unit test password policy validation.
Test phone number validation for various countries.
Validate postal codes for accuracy across different countries.
Perform end-to-end testing of the registration flow.

Documentation:
Provide clear instructions for users regarding password rules and format expectations for phone numbers and postal codes.

Notes:
Ensure compliance with GDPR or other data protection regulations as applicable.
Consider localization for error messages and field descriptions to enhance usability in different regions.https://console.aws.amazon.com/console/home
Plan for scalability to accommodate additional validation rules in the future."""


def create_testcases():

    task_generate = Task(
        description=f"Generate initial test cases based on this Jira ticket: {user_story}",
        agent=test_case_generator,
        expected_output="A list of comprehensive test cases based on the Jira ticket information."
    )

    task_review = Task(
        description="Review and improve the generated test cases. Consider existing test cases and identify areas to increase coverage.",
        agent=test_case_reviewer,
        expected_output="A reviewed and improved set of test cases with identified coverage improvements."
    )

    task_enhance = Task(
        description=f"Enhance the reviewed test cases by comparing against the knowledge base and adding any missing product scenarios.",
        agent=test_case_enhancer,
        expected_output="Enhanced test cases including additional product scenarios and edge cases."
    )

    crew = Crew(
        agents=[test_case_generator, test_case_reviewer, test_case_enhancer],
        tasks=[task_generate, task_review, task_enhance],
        verbose=True,
        process=Process.sequential,
    )

    result = crew.kickoff()

    return result

def convert_test_cases_to_json_format(final_test_cases):
    """
    Converts final test cases into a JSON format.

    Parameters:
    - final_test_cases (str): The final test cases to be formatted.

    Returns:
    - str: A template for the JSON formatted test cases.
    """
    template = f"""You are a helpful assistant that formats
            test cases based on {final_test_cases}. \n
            Generate a list of dictionaries in JSON format with 
            key-value pairs only for
            test scenario (can't be blank) key as 
                test_scenario should contain only text, 
            test case (can't be blank) key as 
                test_case should contain only text,
            category (UI, Functional,
                Database, API, Security, Regression) 
            (can't be blank) key as category,
            labels value as 'Gen AI' key as labels,
            action value as 'New' key as action should contain only text,
            priority (P0, P1, P2, P3, P4) (can't be blank) key as priority,
            Test data key as test_data should contain only text,
            preconditions key as preconditions should contain only text,
            automation (Automatable) key as automation should contain only text,
            steps (can't be blank) key as steps should contain only text,
            and expected results 
            (can't be blank) key as expected results should contain only text."""
    return template

def get_gpt_response(content):
    """
    Sends a request to the GPT API with the specified content and returns the response.

    Parameters:
    - content (str): The text content to be sent to the GPT model for processing.

    Returns:
    requests.Response: The response object received from the GPT API. 
                       This object includes the status code, response headers, and the response
                       content from the GPT model.
    """
    url = os.getenv('CHATGPT_URL')
    headers = {
        'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}",
        'x-timeout': '50000',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending request to GPT API: {e}")
        return None
    
def find_json_string(content):
    """
    Extracts a JSON string from the provided content.

    This method searches the given content for
    the first occurrence of a 
    '[' character and the last occurrence of a ']' character, 
    and extracts
    the substring between these two indices, inclusive.
    This substring is expected to be a valid JSON string
    representing an array.

    Parameters:
    - content (str): The string content from
        which to extract the JSON string.

    Returns:
    str: The extracted JSON string. If the '[' or ']'
    characters are not found,
    this method returns an empty string.

    Example:
    ```python
    content = "Some text before [\"item1\", \"item2\", \"item3\"]
    some text after"
    json_str = find_json_string(content)
    print(json_str)  # Output: ["item1", "item2", "item3"]
    ```
    """
    # Extract JSON string
    json_start = content.find("[")
    json_end = content.rfind("]") + 1
    json_str = content[json_start:json_end]
    return json_str