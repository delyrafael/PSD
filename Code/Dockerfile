FROM python:3.11-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    chromium-browser \
    libnss3 \
    libgconf-2-4 \
    libatk1.0-0 \
    libgtk-3-0 \
    libasound2 \
    libxshm4 \
    libxrandr2 \
    libcups2 \
    libfontconfig1 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Download and install ChromeDriver (specific version for Chromium)
# You might need to adjust the ChromeDriver version based on your Chromium version
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver

# Verify versions
RUN chromium-browser --version
RUN chromedriver --version

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . /app

# Expose port
EXPOSE 8501

CMD ["streamlit", "run", "Code/Dashboard.py"]
