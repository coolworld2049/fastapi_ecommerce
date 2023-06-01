#!/bin/bash

# Set the following variables with your Velero configuration
VELERO_NAMESPACE="velero"
BUCKET_NAME="my-backup-bucket"
BACKUP_NAME="my-backup"

# Backup function
function backup {
  # Create Velero backup
  velero backup create $BACKUP_NAME --include-namespaces fastapi-ecommerce \
  --include-resources pv,pvc\

  # Wait for the backup to complete
  velero backup wait $BACKUP_NAME
}

# Restore function
function restore {
  # Restore Velero backup

  velero restore create --from-backup $BACKUP_NAME

  # Wait for the restore to complete
  velero restore wait $BACKUP_NAME
}

# Help function
function show_help {
  echo "Usage: $0 [backup|restore]"
  echo "Options:"
  echo "  backup    Backup PVCs and PVs"
  echo "  restore   Restore PVCs and PVs"
  echo "  --help    Show this help message"
  exit 0
}

# Main script
case "$1" in
"backup")
  backup
  ;;
"restore")
  restore
  ;;
"--help")
  show_help
  ;;
*)
  echo "Invalid option: $1"
  show_help
  ;;
esac
