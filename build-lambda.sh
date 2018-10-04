#!/bin/bash

# Put sensitive info here, which doesn't get imported into github
source ./secrets.bash

BUILD_DIR=${PWD};
TLDR_VIRTUALENV=".";

echo "Rebuilding Deployment Package...";

rm -f tldr.zip

cd ${TLDR_VIRTUALENV}/lib/python3.7/site-packages
zip -r9 ${BUILD_DIR}/tldr.zip *
cd ${BUILD_DIR};
zip -d tldr.zip "pip/*"
zip -d tldr.zip "setuptools/*"
zip -g tldr.zip TLDR.py
zip -g tldr.zip local_config.py

# echo "Pushing to AWS...";
	
# aws lambda update-function-code \
# --region us-east-1 \
# --function-name TLDR \
# --zip-file fileb://./tldr.zip \
# --role ${AWS_ROLE} \
# --handler TLDR.lambda_handler \
# --runtime python3.6 \
# --timeout 30 \
# --memory-size 1024;