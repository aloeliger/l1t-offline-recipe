#!/usr/bin/env python3
import argparse
import subprocess
from subprocess import CalledProcessError
import os

currentRecipe = {
    'release': 'CMSSW_12_5_2_patch1',
    'repo': ('cms-l1t-offline', 'https://github.com/cms-l1t-offline/cmssw.git'),
    'integrationBranch': 'phase2-l1t-integration-1252patch1',
    'dataExternals': {
        'L1Trigger-Phase2L1ParticleFlow' : 'https://github.com/cms-data/L1Trigger-Phase2L1ParticleFlow.git',
        'L1Trigger-TrackFindingTracklet' : 'https://github.com/cms-data/L1Trigger-TrackFindingTracklet.git',
        'L1Trigger-L1TGlobal' : 'https://github.com/cms-data/L1Trigger-L1TGlobal.git',
        'L1Trigger-L1TMuon' : 'https://github.com/cms-data/L1Trigger-L1TMuon.git',
        'L1Trigger-CSCTriggerPrimitives' : 'https://github.com/cms-data/L1Trigger-CSCTriggerPrimitives.git',
        'L1Trigger-TrackTrigger': 'https://github.com/cms-data/L1Trigger-TrackTrigger.git',
        'L1Trigger-L1THGCal': 'https://github.com/cms-data/L1Trigger-L1THGCal.git',
        'L1Trigger-RPCTrigger' : 'https://github.com/cms-data/L1Trigger-RPCTrigger.git',
        'L1Trigger-DTTriggerPhase2' : 'https://github.com/cms-data/L1Trigger-DTTriggerPhase2.git',
        'L1Trigger-TrackFindingTMTT' : 'https://github.com/cms-data/L1Trigger-TrackFindingTMTT.git',
        'L1Trigger-L1TCalorimeter' : 'https://github.com/cms-data/L1Trigger-L1TCalorimeter.git',
    }
}

def getDataExternal(name, url):
    topLevel = './localData'
    packageName = name.split('-')[0]
    subPackageName = name.split('-')[1]

    completePath = f'{topLevel}/{packageName}/{subPackageName}'

    os.makedirs(completePath, exist_ok=True)

    cloneCommand = f'git clone {url} {completePath}/data/'

    externalProc = subprocess.run(
        [cloneCommand],
        shell=True,
        stderr=subprocess.PIPE
    )
    return externalProc

def main(args):
    #
    #Get the initial release
    #
    initialReleaseCommand = f'cmsrel {currentRecipe["release"]}'

    releaseProc = subprocess.run(
        [initialReleaseCommand],
        shell=True,
        stderr = subprocess.PIPE,
    )
    if releaseProc.returncode != 0:
        print('There was an issue attempting to set-up the cms release')
        print('The following error was caught:')
        print(err)
        print('The following is the stderr of the process, and may help debugging')
        print(releaseProc.stderr.decode())
        return 1
    
    #
    #perform the git initialization
    #
    gitSetup = 'cmsenv && git cms-init'

    setupProc = subprocess.run(
        [gitSetup],
        shell=True,
        cwd=f'{currentRecipe["release"]}/src/',
    )
    if setupProc.returncode != 0:
        print('There was an issue attempting to initialize the cms release')
        print('The following error was caught:')
        print(err)
        print('The following is the stderr of the process and may help debugging')
        print(setupProc.stderr.decode())
        return 1

    #
    #rebase the integration branch
    #
    rebaseCommand = f'cmsenv && git cms-rebase-topic -u {currentRecipe["repo"][0]}:{currentRecipe["integrationBranch"]}'
    
    rebaseProc = subprocess.run(
        [rebaseCommand],
        shell=True,
        cwd=f'{currentRecipe["release"]}/src/',
    )
    if rebaseProc.returncode != 0:
        print('There was an issue attempting to rebase the integration branch')
        print('The following error was caught:')
        print(err)
        print('The following is the stderr of the process and may help debugging')
        print(rebaseProc.stderr.decode())
        print('If the error is a result of git merging issues, or is not otherwise software related, please contac the L1T Offline Software team')
        return 1
    
    #
    # setup the data externals
    #
    for name in currentRecipe['dataExternals']:
        finishedProc = getDataExternal(
            name=name,
            url=currentRecipe['dataExternals'][name]
        )
        if finishedProc.returncode != 0:
            print('There was an issue getting a data external')
            print(f'The failed data external was {name}')
            print('The following is the stderr of that process')
            print(finishedProc.stderr.decode())
            return finishedProc.returncode
    #
    #wrap-up
    #
    print('All required packages installed successfully')
    print('Please use the env script to setup your environment')
    print('Or, you can add the localData repo to the FileInPath search path via:\n')
    print(f'cd {currentRecipe["release"]}/src/')
    print('cmsenv')
    print('cd ../../')
    print('export CMSSW_SEARCH_PATH=$PWD/localData/:$CMSSW_SEARCH_PATH')
    print(f'cd {currentRecipe["release"]}/src/\n')
    print('OR\n')
    print('You can run \'source setEnv.sh\' in this repository which will run those steps for you')

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup the l1t-offline software development environment')

    args = parser.parse_args()

    exitCode = main(args)

    exit(exitCode)