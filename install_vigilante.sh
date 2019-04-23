#!/bin/bash
echo Making systemd user directory
mkdir -p ~/.config/systemd/user
echo Copying service and timer
cp vigilante.service ~/.config/systemd/user/
cp vigilante.timer ~/.config/systemd/user/
