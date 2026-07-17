FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd -m appuser

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files, owned by the non-root user (needed by e.g. the /reload route)
COPY --chown=appuser:appuser . .

# Set port for Docker
ENV PORT=8080
EXPOSE 8080

USER appuser

# Command to run the Flask app
CMD ["python", "app.py"]
