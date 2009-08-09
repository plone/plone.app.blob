#!/bin/bash

cd $( dirname $0 )
bin/buildout -Nqc test-bbb.cfg
bin/instance test --nowarn -s Products.CMFPlone
bin/instance test --nowarn -s Products.ATContentTypes
bin/instance test --nowarn -s plone.app.linkintegrity
cat test-patches/* | patch -REsp0 --no-backup-if-mismatch
find extras/ -name \*.orig -o -name \*.rej | xargs rm
bin/buildout -Nq
