#!/bin/bash
OUTPUT_FILE="/var/www/vrunoa/webspider/python/logs/requeue/`date +%Y-%m-%d_%T`.html"
OUTPUT_DIR="/var/www/vrunoa/webspider/python/logs/requeue"
URL_REQUEUE="http://localhost/back/cron/requeue"
if [ ! -d $OUTPUT_DIR ]; then
	mkdir $OUTPUT_DIR
fi
wget $URL_REQUEUE --output-document=$OUTPUT_FILE --tries=1
exit
