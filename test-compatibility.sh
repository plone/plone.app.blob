#!/bin/bash

cd $( dirname $0 )
bin/buildout -Nqc test-bbb.cfg
cat test-patches/* | patch -Nsp0
bin/instance test --nowarn -s Products.CMFPlone
bin/instance test --nowarn -s Products.ATContentTypes
cat test-patches/* | patch -Rsp0
find extras/ -name \*.orig | xargs rm
bin/buildout -Nq
