import asyncio
# from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Depends
import sys
import os
import logging
from .generate_testcases import create_testcases, convert_test_cases_to_json_format, get_gpt_response, find_json_string
import json
import requests

app = FastAPI()
# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/generate_testcases")
async def generate_test_cases():
    try:
        final_test_cases = create_testcases()
        formatted_test_cases = " ".join(final_test_cases.raw.replace('"', '').replace("'", "").strip().splitlines())
        template = convert_test_cases_to_json_format(formatted_test_cases)
        testcases = {}
        for _retry in range(int(os.getenv('GENAI_RETRY_COUNT', 3))):  # Retry up to 3 times
            res = get_gpt_response(template)
            if res.status_code == 200:
                res = res.json()
                choices = res.get('choices', [])
                if len(choices):
                    testcases = choices[0].get('message', {}).get('content', '[]')
                    testcases = find_json_string(testcases)
                    testcases = json.loads(testcases)
                break
        return {"testcases": testcases}
    except Exception as e:
        return {"message": str(e)}