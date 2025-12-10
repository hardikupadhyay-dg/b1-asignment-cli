import json
import os
import boto3
from datetime import datetime

# DynamoDB table name from environment variable (for flexibility)
TABLE_NAME = os.environ.get("TABLE_NAME", "Emp_Master")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def build_response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body_dict)
    }


def handle_post_employee(event):
    """
    POST /employee
    Body JSON: { "Emp_Id", "First_Name", "Last_Name", "Date_Of_Joining" }
    """
    if event.get("body") is None:
        return build_response(400, {"error": "Missing request body"})

    # HTTP API / REST API (proxy) often send body as string
    try:
        body = json.loads(event["body"])
    except json.JSONDecodeError:
        return build_response(400, {"error": "Invalid JSON body"})

    required_fields = ["Emp_Id", "First_Name", "Last_Name", "Date_Of_Joining"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        return build_response(400, {"error": f"Missing fields: {', '.join(missing)}"})

    item = {
        "Emp_Id": body["Emp_Id"],
        "First_Name": body["First_Name"],
        "Last_Name": body["Last_Name"],
        "Date_Of_Joining": body["Date_Of_Joining"],
    }

    # Put item into DynamoDB
    table.put_item(Item=item)
    print(f"Inserted item: {item}")  # goes to CloudWatch Logs

    return build_response(201, {"message": "Employee created", "item": item})


def handle_get_employee(event):
    """
    GET /employee?emp_id=<id>
    """
    query_params = event.get("queryStringParameters") or {}
    emp_id = query_params.get("emp_id")

    if not emp_id:
        return build_response(400, {"error": "emp_id query parameter is required"})

    resp = table.get_item(Key={"Emp_Id": emp_id})
    item = resp.get("Item")

    if not item:
        return build_response(404, {"error": "Employee not found"})

    print(f"Retrieved item: {item}")  # goes to CloudWatch Logs
    return build_response(200, {"item": item})


def lambda_handler(event, context):
    """
    Main Lambda handler. Works with API Gateway HTTP API / REST API (proxy integration).
    """
    # For local testing we may pass 'method' ourselves
    method = None
    raw_path = event.get("rawPath") or event.get("path") or ""

    # HTTP API v2.0
    if "requestContext" in event and "http" in event["requestContext"]:
        method = event["requestContext"]["http"]["method"]
    # REST API
    elif "httpMethod" in event:
        method = event["httpMethod"]
    # Local testing fallback
    elif "method" in event:
        method = event["method"]

    if raw_path.endswith("/employee") or raw_path == "/employee" or raw_path == "":
        if method == "POST":
            return handle_post_employee(event)
        elif method == "GET":
            return handle_get_employee(event)
        else:
            return build_response(405, {"error": "Method not allowed"})
    else:
        return build_response(404, {"error": "Not found"})


# Simple local test entrypoint
if __name__ == "__main__":
    # Example local POST test
    test_event_post = {
        "method": "POST",
        "path": "/employee",
        "body": json.dumps({
            "Emp_Id": "E001",
            "First_Name": "Alice",
            "Last_Name": "Brown",
            "Date_Of_Joining": "2024-07-01"
        })
    }

    print(lambda_handler(test_event_post, None))
