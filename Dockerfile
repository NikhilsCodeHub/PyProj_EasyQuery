# Dockerfile

# Stage 1: Build Stage (install dependencies)
FROM python:3.12-slim-bookworm AS builder

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's cache
COPY requirements.txt .

RUN pip install --upgrade pip
# Install dependencies. The --no-cache-dir option saves space.
# The --compile-bytecode false --no-warn-script-location options are good for containers.
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage (copy application code and run)
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN pip install --upgrade pip

# Copy the application code
COPY . .

# Expose the port that Uvicorn will listen on
EXPOSE 8123

# Command to run the application using Uvicorn
# The --host 0.0.0.0 is crucial for Docker
# The --port 8000 matches the EXPOSE instruction
#CMD ["uvicorn", "service.api_main:app", "--host", "0.0.0.0", "--port", "8123"]
CMD ["bash"]
