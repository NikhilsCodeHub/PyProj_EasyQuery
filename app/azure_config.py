"""
Azure File Share Configuration for EasyQuery Application
"""
import os
from pathlib import Path
import logging

class AzureFileShareConfig:
    """Configuration class for Azure file share integration"""
    
    def __init__(self):
        self.data_dir = self._get_mount_path('/mnt/azurefiles/data', 'data')
        self.logs_dir = self._get_mount_path('/mnt/azurefiles/logs', 'logs')
        self.storage_dir = self._get_mount_path('/mnt/azurefiles/storage', 'storage')
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Configure logging to use the appropriate directory
        self._configure_logging()
    
    def _get_mount_path(self, mount_path, fallback):
        """Get the appropriate path for file operations"""
        if os.path.exists(mount_path) and os.path.ismount(mount_path):
            print(f"Using Azure file share: {mount_path}")
            return Path(mount_path)
        else:
            # Create local fallback directory
            local_path = Path(fallback)
            local_path.mkdir(exist_ok=True)
            print(f"Using local directory: {local_path}")
            return local_path
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.data_dir, self.logs_dir, self.storage_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _configure_logging(self):
        """Configure logging to use the appropriate directory"""
        log_file = self.logs_dir / 'easyquery.log'
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured. Log file: {log_file}")
    
    @property
    def database_path(self):
        """Get the database file path"""
        return self.data_dir / 'sample_data.db'
    
    @property
    def uploads_path(self):
        """Get the uploads directory path"""
        uploads_dir = self.storage_dir / 'uploads'
        uploads_dir.mkdir(exist_ok=True)
        return uploads_dir
    
    @property
    def temp_path(self):
        """Get the temporary files directory path"""
        temp_dir = self.storage_dir / 'temp'
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    def get_file_share_status(self):
        """Get the status of file share mounts"""
        status = {
            'data_share': {
                'path': str(self.data_dir),
                'mounted': os.path.ismount('/mnt/azurefiles/data'),
                'exists': self.data_dir.exists(),
                'writable': os.access(self.data_dir, os.W_OK)
            },
            'logs_share': {
                'path': str(self.logs_dir),
                'mounted': os.path.ismount('/mnt/azurefiles/logs'),
                'exists': self.logs_dir.exists(),
                'writable': os.access(self.logs_dir, os.W_OK)
            },
            'storage_share': {
                'path': str(self.storage_dir),
                'mounted': os.path.ismount('/mnt/azurefiles/storage'),
                'exists': self.storage_dir.exists(),
                'writable': os.access(self.storage_dir, os.W_OK)
            }
        }
        return status

# Global configuration instance
azure_config = AzureFileShareConfig()

# Convenience functions
def get_database_path():
    """Get the database file path"""
    return str(azure_config.database_path)

def get_uploads_path():
    """Get the uploads directory path"""
    return str(azure_config.uploads_path)

def get_logs_path():
    """Get the logs directory path"""
    return str(azure_config.logs_dir)

def get_temp_path():
    """Get the temporary files directory path"""
    return str(azure_config.temp_path)

def get_file_share_status():
    """Get the status of all file shares"""
    return azure_config.get_file_share_status()

# Example usage
if __name__ == "__main__":
    print("Azure File Share Configuration")
    print("=" * 40)
    
    config = AzureFileShareConfig()
    
    print(f"Database path: {config.database_path}")
    print(f"Uploads path: {config.uploads_path}")
    print(f"Logs path: {config.logs_dir}")
    print(f"Temp path: {config.temp_path}")
    
    print("\nFile Share Status:")
    status = config.get_file_share_status()
    for share_name, share_info in status.items():
        print(f"\n{share_name}:")
        for key, value in share_info.items():
            print(f"  {key}: {value}")
