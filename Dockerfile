FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set port for Docker
ENV PORT=8088
EXPOSE 8088

# Create a non-root user for security
RUN useradd -m appuser
USER appuser

# Command to run the Flask app
CMD ["python", "app.py"]
