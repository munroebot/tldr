#!/bin/bash

# Put sensitive info here, which doesn't get imported into github
source ./secrets.bash

BUILD_DIR=${PWD};
TLDR_VIRTUALENV=".";

echo "Rebuilding Deployment Package...";
cd ${TLDR_VIRTUALENV}/lib/python3.7/site-packages
zip -r9 ${BUILD_DIR}/tldr.zip *
cd ${BUILD_DIR};
zip -d tldr.zip "pip/*";
zip -d tldr.zip "setuptools/*";
zip -g tldr.zip TLDR.py;
zip -g tldr.zip local_config.py;
zip -g tldr.zip email_templates.py;

echo "Pushing to AWS...";
for i in ${functions}; do
    aws lambda update-function-code \
    --region us-east-1 \
    --function-name ${i} \
    --zip-file fileb://./tldr.zip
done

echo "Cleaning up artifact...";
rm -f tldr.zip