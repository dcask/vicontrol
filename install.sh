#!/bin/bash

/var/lib/visiology/scripts/run.sh --stop

ssh_secret_label=$(docker secret ls -q --filter label=VICONTROL_SSH_AUTH)

#if there're no secrets 

if [[ -z "${ssh_secret_label}" ]]; then
  
  
  #create vicontrol user
  userdel --remove vicontrol
  useradd vicontrol -d /home/vicontrol -m -s/bin/bash
  #add docker secret for the user
  docker secret rm SSH_AUTH_USER
  echo -n vicontrol | docker secret create -l VICONTROL_SSH_AUTH=ssh_user SSH_AUTH_USER -
  #create group for the user
  groupadd visiology
  usermod -aG visiology vicontrol
  usermod -aG docker vicontrol
  #edit folder and files rights
  chown -R :visiology /var/lib/visiology
  chmod -R g+w /var/lib/visiology/scripts/*.env
  #create ssh authorization key, make the key secret and finnaly remove private key
  mkdir /home/vicontrol/.ssh
  ssh-keygen -t rsa -q -f "/home/vicontrol/.ssh/id_rsa" -N ""
  cat /home/vicontrol/.ssh/id_rsa.pub >> /home/vicontrol/.ssh/authorized_keys
  docker secret create -l VOCONTROL_SSH_AUTH=ssh_password SSH_AUTH_KEY /home/vicontrol/.ssh/id_rsa
  rm -f /home/vicontrol/.ssh/id_rsa
  cp ./wsjs.js /docker-volume/dashboard-viewer/customjs/vicontrol.js
  cp ./my.css /docker-volume/dashboard-viewer/customjs/vicontrol.css
  #check id external.yml is default
  if ! grep -Fq "services:" /var/lib/visiology/scripts/v2/external.yml;
    then
      sed -i "/version/r./insertheader" /var/lib/visiology/scripts/v2/external.yml
  fi
  #inject vicontrol service
  if ! grep -Fq "vicontrol:" /var/lib/visiology/scripts/v2/external.yml;
    then
      #sed -i "/version/r./insertheader" /var/lib/visiology/scripts/v2/external.yml
      sed -i "/^services\:/r./insertservice" /var/lib/visiology/scripts/v2/external.yml
      #inject secrets at the eof
      cat insertsecrets >> /var/lib/visiology/scripts/v2/external.yml
      
  fi
  #inject to nginx.conf have to pass HTTP1.1 reverse and proxy2
  if ! grep -Fq "vicontrol_url" /docker-volume/proxy/nginx.conf;
    then
      sed -i '/grafana:3000;/a         set $vicontrol_url http:\/\/vicontrol;' /docker-volume/proxy/nginx.conf
  fi
  if ! grep -Fq "^\/control" /docker-volume/proxy/nginx.conf;
  # websockets inject
    then
    sed -i "/location.*v3/e cat ./insertreverse" /var/lib/visiology/scripts/configs/nginx.conf
    sed -i "/location.*ssbi/e cat ./insertproxy" /docker-volume/proxy/nginx.conf
    docker config rm reverseproxy
  fi
fi

#build the image

source ./build.sh