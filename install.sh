#!/bin/bash


ssh_secret_label=$(docker secret ls -q --filter label=VICONTROL_SSH_AUTH)

#if there're no secrets 

if [[ -z "${ssh_secret_label}" ]]; then
  echo -n vicontrol | docker secret create -l VOCONTROL_SSH_AUTH=ssh_user SSH_AUTH_USER -
  useradd vicontrol -d /home/vicontrol -m -s/bin/bash
  groupadd visiology
  usermod -aG visiology vicontrol
  usermod -aG docker vicontrol
  chown -R :visiology /var/lib/visiology
  chmod -R g+w /var/lib/visiology/scripts/*.env
  #create ssh authorization key, make the key secret
  ssh-keygen -t rsa -q -f "home/vicontrol/.ssh/id_rsa" -N ""
  cat id_rsa.pub >> /home/vicontrol/.ssh/authorized_keys
  docker secret create -l VOCONTROL_SSH_AUTH=ssh_password SSH_AUTH_KEY /home/vicontrol/.ssh/id_rsa
  rm -f /home/vicontrol/.ssh/id_rsa
  
  #check id external.yml is default
  if ! grep -Fxq "service" /var/lib/visiology/scripts/v2/external.yml;
    then
      sed -i "/version/r./insertheader" /var/lib/visiology/scripts/v2/external.yml
  fi
  #inject vicontrol service
  sed -i "/service/r./insertservice" /var/lib/visiology/scripts/v2/external.yml
  #inject secrets at the eof
  cat insertsecrets >> /var/lib/visiology/scripts/v2/external.yml
  #inject to nginx.conf have to pass HTTP1.1 reverse and proxy2
  sed -i '/grafana:3000;/a         set $vicontrol_url http:\/\/vicontrol;' /docker-volume/proxy/nginx.conf
  sed -i '/\/regular-reporting {/i             location ~* ^\/control {\n            proxy_pass $vicontrol_url;\n        }\n' /docker-volume/proxy/nginx.conf
fi

#build the image

source ./build.sh