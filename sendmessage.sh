#!/bin/bash
source /home/pi/vigilante/keys
if [ ! -z "$1" ]
then
	URL="https://api.telegram.org/bot$TOKEN/sendMessage"
	curl -s -X POST $URL -d chat_id=$CHANNEL -d text="$1" >/dev/null 2>&1
fi
