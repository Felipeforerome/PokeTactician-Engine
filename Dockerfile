# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.12.1
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    python3-dev \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050


# Run app.py when the container launches
CMD ["python", "./dash_app/app.py"]
