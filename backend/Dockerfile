# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Command to run the application
CMD ["uvicorn", "rag:app", "--host", "0.0.0.0", "--port", "8001"]
