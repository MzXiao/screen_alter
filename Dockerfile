
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the backend requirements file
COPY screen_alter_backend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt 

# Copy the backend code
COPY screen_alter_backend ./screen_alter_backend

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
# We run from /app so that the module 'screen_alter_backend' is importable
CMD ["uvicorn", "screen_alter_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
