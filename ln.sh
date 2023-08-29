#! /bin/bash

# usage: ln.sh <from> <to>
# example: ln.sh exact/B01.00-n256 B01.00-n256-cont

# to remove dead symlinks in current dir: `find . -xtype l -delete`

ln -s /mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/$1/*.bp /mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/$2
ln -s /mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/$1/*.h5 /mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/$2