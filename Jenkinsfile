pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        S3_BUCKET = 'dg-emp-lambda-bucket-yourname'
        S3_KEY = 'lambda/lambda_package.zip'
        LAMBDA_FUNCTION_NAME = 'employee-api-func'
        LAMBDA_ROLE_ARN = 'arn:aws:iam::147060631436:role/lambda-employee-exec-role'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Package Lambda') {
            steps {
                sh '''
                    ls
                    zip -r lambda_package.zip lambda-app/lambda_function.py
                '''
            }
        }

        stage('Upload to S3') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                                 usernameVariable: 'AWS_ACCESS_KEY_ID',
                                                 passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        export AWS_DEFAULT_REGION=$AWS_REGION

                        aws s3 cp lambda_package.zip s3://$S3_BUCKET/$S3_KEY
                    '''
                }
            }
        }

        stage('Deploy Lambda') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                                 usernameVariable: 'AWS_ACCESS_KEY_ID',
                                                 passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        set -e
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        export AWS_DEFAULT_REGION=$AWS_REGION

                        if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME > /dev/null 2>&1; then
                            echo "Updating existing Lambda function..."
                            aws lambda update-function-code \
                                --function-name $LAMBDA_FUNCTION_NAME \
                                --s3-bucket $S3_BUCKET \
                                --s3-key $S3_KEY
                        else
                            echo "Creating new Lambda function..."
                            aws lambda create-function \
                                --function-name $LAMBDA_FUNCTION_NAME \
                                --runtime python3.11 \
                                --role $LAMBDA_ROLE_ARN \
                                --handler lambda_function.lambda_handler \
                                --code S3Bucket=$S3_BUCKET,S3Key=$S3_KEY \
                                --environment Variables="{TABLE_NAME=Emp_Master}"
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
        }
    }
}
