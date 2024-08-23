# Use Python base image
FROM python:3.12-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory
WORKDIR /app/

# Copy the requirements.txt file to the working directory
COPY requirements.txt /app/

# Install the dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# Install dlib from source
RUN pip install dlib

RUN pip install tf-keras

RUN pip install django-cors-headers

# Copy the rest of the application code to the working directory
COPY . /app/

# List all files in the working directory for verification
RUN ls -R /app/

# Set environment variable for Django
ENV PYTHONUNBUFFERED 1

# Expose port 8000 for the Django application
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]