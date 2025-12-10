pipeline {
    agent any

    environment {
        AWS_REGION           = 'ap-south-1'
        S3_BUCKET            = 'dg-emp-lambda-bucket-yourname'          // <- change this
        S3_KEY               = 'lambda_package.zip'
        LAMBDA_FUNCTION_NAME = 'employee-api-func'            // <- change this
        LAMBDA_ROLE_ARN      = 'arn:aws:iam::147060631436:role/your-lambda-exec-role' // <- change this
    }

    stages {
        stage('Checkout') {
            steps {
                // Uses the repo where this Jenkinsfile lives
                checkout scm
            }
        }

        stage('Package Lambda') {
            steps {
                sh '''
                  set -e

                  echo "==> Listing workspace"
                  pwd
                  ls -R

                  # Remove any old package
                  rm -f lambda_package.zip

                  # Go into the lambda-app folder and zip everything in it
                  cd lambda-app
                  zip -r ../lambda_package.zip .
                '''
            }
        }

        stage('Upload to S3') {
            steps {
                // Use AWS Credentials-type credential (ID: aws-creds)
                withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
                    sh '''
                      set -e
                      echo "==> Uploading lambda_package.zip to S3"
                      aws s3 cp lambda_package.zip s3://"${S3_BUCKET}"/"${S3_KEY}"
                    '''
                }
            }
        }

        stage('Deploy Lambda') {
            steps {
                withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
                    sh '''
                      set -e

                      echo "==> Checking if Lambda function exists: ${LAMBDA_FUNCTION_NAME}"
                      if aws lambda get-function --function-name "${LAMBDA_FUNCTION_NAME}" > /dev/null 2>&1; then
                        echo "==> Lambda exists, updating code"
                        aws lambda update-function-code \
                          --function-name "${LAMBDA_FUNCTION_NAME}" \
                          --s3-bucket "${S3_BUCKET}" \
                          --s3-key "${S3_KEY}"
                      else
                        echo "==> Lambda does not exist, creating"
                        aws lambda create-function \
                          --function-name "${LAMBDA_FUNCTION_NAME}" \
                          --runtime python3.11 \
                          --role "${LAMBDA_ROLE_ARN}" \
                          --handler lambda_function.lambda_handler \
                          --code S3Bucket="${S3_BUCKET}",S3Key="${S3_KEY}" \
                          --timeout 30 \
                          --memory-size 128
                      fi
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}
