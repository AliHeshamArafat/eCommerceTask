# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /eCommerceTask

# Copy the requirements file into the container
COPY requirements.txt /eCommerceTask/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /eCommerceTask
COPY . /eCommerceTask/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=myproject.settings
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
