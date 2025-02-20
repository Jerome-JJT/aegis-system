#!/bin/bash

#wlr-randr --output "HDMI-A-1" --mode 720x480
#wlr-randr --output "HDMI-A-1" --off
#wlr-randr --output "HDMI-A-1" --on
export XDG_RUNTIME_DIR=/run/user/1000

if [[ $1 = "off" ]]; then
	echo "going off"
	wlr-randr --output "HDMI-A-1" --off
	#dtparam hdmi="off"
else
	echo "going on"
	wlr-randr --output "HDMI-A-1" --on --transform 270
	#dtparam hdmi="on"
fi
