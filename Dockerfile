# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy and install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the app in a containerized environment
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.headless=true", "--server.enableCORS=false"] 