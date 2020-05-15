#!/bin/bash

# Keep all running information to log file.
TIME_STR=`date +"%Y%m%d%H%M%S"`
LOG_FILE=run_$TIME_STR.log
touch $LOG_FILE
SCRIPT_DIR=/mnt/diskc/gitlab/mets/
ENV_FILE=$SCRIPT_DIR/subtools/profiles-maizedna-1.sh
#METHOD=broad
METHOD=precise
./mets.sh --script=$SCRIPT_DIR --environment=$ENV_FILE --method=$METHOD 2>&1 | tee -a $LOG_FILE
