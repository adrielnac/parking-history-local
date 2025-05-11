# Parking Query Lambda Function

This AWS Lambda function queries parking lot availability and stores the data in DynamoDB.

## Deployment Instructions

1. Use the provided packaging script:
```bash
./package.sh
```

This will create a `function.zip` file ready for deployment.

2. Create an AWS Lambda function:
   - Runtime: Python 3.9+
   - Handler: query_parking.lambda_handler
   - Memory: 256 MB (increased for better performance)
   - Timeout: 15 seconds (increased to handle network latency)
   - Environment variables:
     - DYNAMODB_TABLE: your-dynamodb-table-name

3. Configure IAM Role with these permissions:
   - AWSLambdaBasicExecutionRole
   - DynamoDB permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/your-dynamodb-table-name"
        }
    ]
}
```

## EventBridge (CloudWatch Events) Schedule

To run the function every 10 minutes:

1. Create a new EventBridge rule:
   - Rule Type: Schedule
   - Schedule pattern: cron(*/10 * * * ? *)
   - Target: Your Lambda function

2. Or use AWS CLI:
```bash
aws events put-rule \
    --name "parking-query-schedule" \
    --schedule-expression "rate(10 minutes)"

aws events put-targets \
    --rule "parking-query-schedule" \
    --targets "Id"="1","Arn"="your-lambda-arn"
```

## Monitoring

- Monitor function execution in CloudWatch Logs
- Set up CloudWatch Alarms for errors
- Use X-Ray for tracing (optional)

# Local Setup

This script can now be run locally without AWS. It uses SQLite for data storage and runs every 10 minutes.

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python query_parking.py
```

The script will scrape parking data and store it in a local SQLite database (`parking_data.db`).
