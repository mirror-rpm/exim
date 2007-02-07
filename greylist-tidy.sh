#!/bin/bash

if [ -r /var/spool/exim/db/greylist.db ]; then
    sqlite /var/spool/exim/db/greylist.db <<EOF
.timeout 5000
DELETE FROM greylist WHERE expire < $((`date +%s` - 604800));
EOF
fi
