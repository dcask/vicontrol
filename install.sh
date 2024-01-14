#!/bin/bash


ssh_secret_label=$(docker secret ls -q --filter label=VICONTROL_SSH_AUTH)

#if there're no secrets 

if [[ -z "${ssh_secret_label}" ]]; then
  #ssh_user_password="$(mktemp -u XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)"
  #echo -n ${ssh_user_password} | docker secret create -l VOCONTROL_SSH_AUTH=ssh_password SSH_AUTH_PASSWORD -
  echo -n vicontrol | docker secret create -l VOCONTROL_SSH_AUTH=ssh_user SSH_AUTH_USER -
  useradd vicontrol -d /home/vicontrol -m -s/bin/bash
  usermod -a -G sudo vicontrol
  #change password
  #mkdir /home/vicontrol
  #mkdir /home/vicontrol/.ssh
  usermod -aG docker vicontrol
  ssh-keygen -t rsa -q -f "home/vicontrol/.ssh/id_rsa" -N ""
  cat id_rsa.pub >> /home/vicontrol/.ssh/authorized_keys
  #check id external.yml is default
  if ! grep -Fxq "service" /var/lib/visiology/scripts/v2/external.yml;
    then
      sed -i "/version/r./insertheader" /var/lib/visiology/scripts/v2/external.yml
  fi
  #inject vicontrol service
  sed -i "/service/r./insertservice" /var/lib/visiology/scripts/v2/external.yml
  #inject secrets at the eof
  cat insertsecrets >> /var/lib/visiology/scripts/v2/external.yml
  #inject to nginx.conf
  sed -i '/grafana:3000;/a         set $vicontrol_url http:\/\/vicontrol;' /docker-volume/proxy/nginx.conf
  sed -i '/\/regular-reporting {/i             location ~* ^\/control {\n            proxy_pass $vicontrol_url;\n        }\n' /docker-volume/proxy/nginx.conf
fi

#build the image

source ./build.sh