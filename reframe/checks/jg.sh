#!/bin/bash

# 0 * * * * /bin/bash /sysbackup/dwdi/jg/dwdi.git/reframe/checks/jg.sh 1>/dev/null 2>/dev/null

cd /sysbackup/dwdi/jg/dwdi.git/reframe/

# /sysbackup/dwdi/jg/dwdi.git/reframe/reframe.git/bin/reframe -V
 
/sysbackup/dwdi/jg/dwdi.git/reframe/reframe.git/bin/reframe \
 -C ./common_elastic.py \
 -c ./checks/jg.py \
 -r

# --keep-stage-files \
# --report-file=latest.json --failure-stats --performance-report
