# Use a base image that includes Python 3.11 (or your desired version)
FROM python:3.11-slim-buster

# Install system dependencies for Chrome/Chromium and ChromeDriver
RUN apt-get update && \
    apt-get install -y \
    chromium-browser \
    chromium-chromedriver \ # Install ChromeDriver from apt
    libnss3 \
    libgconf-2-4 \
    libatk1.0-0 \
    libgtk-3-0 \
    libasound2 \
    libxshm4 \
    libxrandr2 \
    libcups2 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Verify Chrome and ChromeDriver versions
RUN chromium-browser --version
RUN chromedriver --version

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt ./

# Install Python dependencies (reduced for testing)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Streamlit app
COPY . /app

# Expose the Streamlit port (default 8501)
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "Code/Dashboard.py"]
