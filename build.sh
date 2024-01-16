#!/bin/bash
#проверять и удалять старый образ
old_vicontrol=$(docker image ls | grep vicintrol)
if [[!-z $old_vicontrol]]; then
docker image rm vicontrol
fi
docker build -t vicontrol . < Dockerfile
