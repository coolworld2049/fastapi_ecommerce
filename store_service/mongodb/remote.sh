#! /bin/bash -x

sudo ufw allow from "$TRUSTED_MACHINE_IP" to any port 27017