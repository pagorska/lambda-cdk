FROM public.ecr.aws/lambda/python:3.9

# Copy .env file
COPY .env ${LAMBDA_TASK_ROOT}/

# Copy requirements 
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]