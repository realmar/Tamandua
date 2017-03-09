#!/bin/bash

aptitude update
aptitude -y install python python-apt

# sed 's/env_reset/env_reset\nDefaults        env_keep=SSH_AUTH_SOCK/' /etc/sudoers
#cat /etc/sudoers | uniq > /etc/sudoers

# echo 'Defaults        env_keep+="SSH_AUTH_SOCK"' > ~/newsudoers
# cat /etc/sudoers >> ~/newsudoers
# cat ~/newsudoers > /etc/sudoers
# rm ~/newsudoers
