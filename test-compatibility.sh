#!/bin/bash

cd $( dirname $0 )
cat test-patches/* | patch -Nsp0 
bin/instance test --nowarn -s Products.CMFPlone
bin/instance test --nowarn -s Products.ATContentTypes
cat test-patches/* | patch -Rsp0 
