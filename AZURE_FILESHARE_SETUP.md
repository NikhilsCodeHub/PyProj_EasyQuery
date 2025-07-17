# Azure File Share Setup for Container Apps

This document provides instructions for setting up Azure file share mounting in your Azure Container App environment.

## Prerequisites

- Azure Storage Account created
- File shares created in the storage account
- Azure Container App environment configured

## Environment Variables Configuration

Configure the following environment variables in your Azure Container App:

### Required Variables

```bash
# Azure Storage Account credentials
AZURE_STORAGE_ACCOUNT=your_storage_account_name
AZURE_STORAGE_KEY=your_storage_account_key
```

### Optional File Share Variables

Configure these based on your file share names:

```bash
# Data file share (for database files, persistent data)
AZURE_FILE_SHARE_DATA=data-share

# Logs file share (for application logs)
AZURE_FILE_SHARE_LOGS=logs-share

# General storage file share (for uploads, temp files)
AZURE_FILE_SHARE_STORAGE=storage-share

# Custom file share with custom mount point
AZURE_FILE_SHARE_CUSTOM=custom-share
AZURE_FILE_SHARE_CUSTOM_MOUNT=/mnt/azurefiles/custom
```

## Azure CLI Commands

### 1. Create Storage Account (if not exists)
```bash
az storage account create \
    --name mystorageaccount \
    --resource-group myResourceGroup \
    --location eastus \
    --sku Standard_LRS
```

### 2. Get Storage Account Key
```bash
STORAGE_KEY=$(az storage account keys list \
    --resource-group myResourceGroup \
    --account-name mystorageaccount \
    --query '[0].value' \
    --output tsv)
```

### 3. Create File Shares
```bash
# Create data file share
az storage share create \
    --name data-share \
    --account-name mystorageaccount \
    --account-key $STORAGE_KEY

# Create logs file share
az storage share create \
    --name logs-share \
    --account-name mystorageaccount \
    --account-key $STORAGE_KEY

# Create storage file share
az storage share create \
    --name storage-share \
    --account-name mystorageaccount \
    --account-key $STORAGE_KEY
```

### 4. Configure Container App Environment Variables
```bash
az containerapp update \
    --name mycontainerapp \
    --resource-group myResourceGroup \
    --set-env-vars \
        AZURE_STORAGE_ACCOUNT=mystorageaccount \
        AZURE_STORAGE_KEY=$STORAGE_KEY \
        AZURE_FILE_SHARE_DATA=data-share \
        AZURE_FILE_SHARE_LOGS=logs-share \
        AZURE_FILE_SHARE_STORAGE=storage-share
```

## Container App YAML Configuration

Alternatively, you can configure using YAML:

```yaml
properties:
  configuration:
    secrets:
      - name: storage-key
        value: your_storage_account_key
  template:
    containers:
      - name: myapp
        image: myregistry.azurecr.io/myapp:latest
        env:
          - name: AZURE_STORAGE_ACCOUNT
            value: mystorageaccount
          - name: AZURE_STORAGE_KEY
            secretRef: storage-key
          - name: AZURE_FILE_SHARE_DATA
            value: data-share
          - name: AZURE_FILE_SHARE_LOGS
            value: logs-share
          - name: AZURE_FILE_SHARE_STORAGE
            value: storage-share
```

## Mount Points

The startup script will create and mount the following directories:

- `/mnt/azurefiles/data` - For persistent data files
- `/mnt/azurefiles/logs` - For application logs
- `/mnt/azurefiles/storage` - For general storage needs

## Application Integration

### Update Database Path
If you want to store your SQLite database on the file share:

```python
# In your application code
import os

# Use mounted file share for database if available
if os.path.exists('/mnt/azurefiles/data'):
    DATABASE_PATH = '/mnt/azurefiles/data/sample_data.db'
else:
    DATABASE_PATH = 'data/sample_data.db'  # fallback to local
```

### Configure Logging
```python
import logging
import os

# Configure logging to use mounted file share
log_dir = '/mnt/azurefiles/logs' if os.path.exists('/mnt/azurefiles/logs') else 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=f'{log_dir}/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Troubleshooting

### Check Mount Status
```bash
# Inside the container
mount | grep cifs
df -h | grep azurefiles
```

### Common Issues

1. **Permission Denied**: Ensure the storage account key is correct
2. **Mount Failed**: Check if cifs-utils is installed (included in Dockerfile)
3. **File Share Not Found**: Verify the file share name and storage account

### Debug Mode
Set environment variable for debugging:
```bash
DEBUG_MOUNT=true
```

## Security Considerations

1. **Storage Key**: Store as a secret in Container App environment
2. **Network Access**: Configure storage account firewall if needed
3. **Access Control**: Use appropriate file/directory permissions
4. **Backup**: Regularly backup important data in file shares

## Performance Tips

1. **Regional Proximity**: Keep storage account in same region as Container App
2. **File Share Tier**: Use Premium tier for better performance if needed
3. **Caching**: Consider application-level caching for frequently accessed files
4. **Connection Pooling**: Reuse connections when possible

## Monitoring

Monitor file share usage through:
- Azure Storage metrics
- Container App logs
- Application performance monitoring

## Example Usage in Application

```python
import os
from pathlib import Path

class FileShareConfig:
    def __init__(self):
        self.data_dir = self._get_mount_path('/mnt/azurefiles/data', 'data')
        self.logs_dir = self._get_mount_path('/mnt/azurefiles/logs', 'logs')
        self.storage_dir = self._get_mount_path('/mnt/azurefiles/storage', 'storage')
    
    def _get_mount_path(self, mount_path, fallback):
        if os.path.exists(mount_path):
            return Path(mount_path)
        else:
            # Create local fallback directory
            local_path = Path(fallback)
            local_path.mkdir(exist_ok=True)
            return local_path

# Usage
config = FileShareConfig()
database_path = config.data_dir / 'sample_data.db'
log_file = config.logs_dir / 'app.log'
