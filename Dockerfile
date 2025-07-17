# Dockerfile

# Stage 1: Build Stage (install dependencies)
FROM mcr.microsoft.com/azurelinux/base/python:3.12 AS builder

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's cache
COPY requirements.txt .

#RUN pip install --upgrade pip
# Install dependencies. The --no-cache-dir option saves space.
# The --compile-bytecode false --no-warn-script-location options are good for containers.
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage (copy application code and run)
FROM mcr.microsoft.com/azurelinux/base/python:3.12

# Install required packages for Azure file share mounting : File Share Related
# RUN tdnf update -y && \
#     tdnf install -y cifs-utils util-linux && \
#     tdnf clean all

# Set the working directory in the container
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/lib/python3.12/site-packages /usr/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create mount point directories for Azure file shares : File Share Related
# RUN mkdir -p /mnt/azurefiles/data && \
#     mkdir -p /mnt/azurefiles/logs && \
#     mkdir -p /mnt/azurefiles/storage && \
#     chmod 755 /mnt/azurefiles

# Copy the application code
COPY . .

# Copy and set permissions for the startup script : File Share Related
# COPY startup.sh /app/startup.sh
# RUN chmod +x /app/startup.sh

# Expose the port that Uvicorn will listen on
EXPOSE 80

# Use the startup script as the entry point : File Share Related
# CMD ["/app/startup.sh"]

CMD ["python3", "-m","uvicorn", "service.api_main:app", "--host", "0.0.0.0", "--port", "80"]
