#!/bin/bash
#проверять и удалять старый образ
old_vicontrol=$(docker image ls | grep vicontrol)

if [ -n  "$old_vicontrol" ]; then
   docker image rm vicontrol --force
fi

docker build -t vicontrol . < Dockerfile
