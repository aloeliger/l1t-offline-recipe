#!/usr/bin/env bash
cd CMSSW_12_5_2_patch1/src/
cmsenv
cd ../../
export CMSSW_SEARCH_PATH=$PWD/localData/:$CMSSW_SEARCH_PATH
cd CMSSW_12_5_2_patch1/src/