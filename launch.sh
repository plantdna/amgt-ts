#!/bin/bash

# Keep all running information to log file.
TIME_STR=`date +"%Y%m%d%H%M%S"`
LOG_FILE=run_$TIME_STR.log
touch $LOG_FILE
SCRIPT_DIR=/mnt/diskc/gitlab/amgt-ts/
ENV_FILE=$SCRIPT_DIR/subtools/profiles-maizedna-1.sh
#METHOD=broad
METHOD=precise
PROJECT_DIR=/mnt/diskc/gitlab/amgt-ts
$SCRIPT_DIR/amgt-ts.sh --script=$SCRIPT_DIR --environment=$ENV_FILE --method=$METHOD --project=$PROJECT_DIR 2>&1 | tee -a $LOG_FILE
