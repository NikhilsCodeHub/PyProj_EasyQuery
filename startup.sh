#!/bin/bash

# Azure File Share Mounting Script for Container Apps
# This script handles mounting Azure file shares in Azure Container Apps environment

echo "Starting Azure File Share mounting process..."

# Function to mount Azure file share
mount_azure_fileshare() {
    local mount_point=$1
    local share_name=$2
    
    if [ ! -z "$AZURE_STORAGE_ACCOUNT" ] && [ ! -z "$AZURE_STORAGE_KEY" ]; then
        echo "Mounting Azure file share: $share_name to $mount_point"
        
        # Ensure mount point exists
        mkdir -p "$mount_point"
        
        # Create credentials file
        echo "username=$AZURE_STORAGE_ACCOUNT" > /tmp/azure-creds
        echo "password=$AZURE_STORAGE_KEY" >> /tmp/azure-creds
        chmod 600 /tmp/azure-creds
        
        # Mount the file share
        mount -t cifs //$AZURE_STORAGE_ACCOUNT.file.core.windows.net/$share_name $mount_point \
            -o credentials=/tmp/azure-creds,dir_mode=0755,file_mode=0644,serverino,nosharesock,actimeo=30
        
        if [ $? -eq 0 ]; then
            echo "Successfully mounted $share_name to $mount_point"
            ls -la "$mount_point"
        else
            echo "Failed to mount $share_name to $mount_point"
            echo "Mount point will be available as local directory"
        fi
        
        # Clean up credentials file
        rm -f /tmp/azure-creds
    else
        echo "Azure storage credentials not provided, using local directory for $mount_point"
        mkdir -p "$mount_point"
    fi
}

# Mount Azure file shares based on environment variables
# You can configure these in your Container App environment

# Data file share (for database, uploads, etc.)
if [ ! -z "$AZURE_FILE_SHARE_DATA" ]; then
    mount_azure_fileshare "/mnt/azurefiles/data" "$AZURE_FILE_SHARE_DATA"
fi

# Logs file share
if [ ! -z "$AZURE_FILE_SHARE_LOGS" ]; then
    mount_azure_fileshare "/mnt/azurefiles/logs" "$AZURE_FILE_SHARE_LOGS"
fi

# General storage file share
if [ ! -z "$AZURE_FILE_SHARE_STORAGE" ]; then
    mount_azure_fileshare "/mnt/azurefiles/storage" "$AZURE_FILE_SHARE_STORAGE"
fi

# Custom file share (configurable)
if [ ! -z "$AZURE_FILE_SHARE_CUSTOM" ] && [ ! -z "$AZURE_FILE_SHARE_CUSTOM_MOUNT" ]; then
    mount_azure_fileshare "$AZURE_FILE_SHARE_CUSTOM_MOUNT" "$AZURE_FILE_SHARE_CUSTOM"
fi

echo "File share mounting completed."

# Update application to use mounted directories if they exist
if [ -d "/mnt/azurefiles/data" ]; then
    echo "Data directory available at: /mnt/azurefiles/data"
    # You can symlink or update your app config to use this path
    # Example: ln -sf /mnt/azurefiles/data/sample_data.db /app/data/sample_data.db
fi

if [ -d "/mnt/azurefiles/logs" ]; then
    echo "Logs directory available at: /mnt/azurefiles/logs"
    # Configure your app to write logs here
fi

echo "Starting the application..."

# Start the FastAPI application
exec python3 -m uvicorn service.api_main:app --host 0.0.0.0 --port 80
