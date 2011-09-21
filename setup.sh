#!/bin/sh
#
# simple setup script to drop rpmmacros and build dir links
#


# find where this script lives
Bin="$( readlink -f -- "${0%/*}" )"

if [ -e  ~/.rpmmacros ] ; then 
  echo "looks like you already have a ~/.rpmmacros file. Remove it and re-run this script if you want our version"
else
  cp -v $Bin/rpmmacros ~/.rpmmacros
fi 


if [ -e ~/rpm_build ]  ; then 
  echo "~/rpm_build seems to exist so we wont try to recreate"
else
  ln -vs  $Bin  ~/rpm_build 
fi
