# This script can be used with Visual C++ to build all the configurations we may use.
# Run this script using Python 2.7 or later.

# Name of the library to build (must match directory- and file names)
libName = "XboxInternals"

import os, subprocess, re, codecs, multiprocessing, time
from collections import deque

class BuildProcessDetails:
    def __init__(self, configName):
        self.configName = configName
        self.process = None
        self.logFile = None
        self.logFilePath = ""

scriptDir = os.path.split(os.path.abspath(__file__))[0]
libDir = os.path.realpath(os.path.join(scriptDir, os.path.join("../../../{0}".format(libName))))
os.chdir(libDir)

# The build configurations
buildConfigs = {
    "debug_shared": {},
    "debug_static_md": {},
    "debug_static_mt": {},
    "release_shared": {},
    "release_static_md": {},
    "release_static_mt": {}
}

# Clean the repository
#subprocess.check_call("git reset --hard")
#subprocess.check_call("git clean -d -x -f")

# Prepare configs for building
print("")
print("Configuring...")
for configName, config in buildConfigs.items():
    os.chdir(libDir)

    # Upgrade solution and projects
    # Disabled because there's no real need for this; however, it might be useful for future versions of VC++.
    '''
    returnCode = subprocess.check_call([
            "devenv",
            os.path.join(libDir, "{0}.sln".format(configName)),
            "/Upgrade"
        ]
    )

    if returnCode != 0:
        print("Configuring \"{0}\" failed (exit code {1}).".format(configName, returnCode))
    '''

# Build each config
# This runs builds in parallel to speed things up
print("Running builds...")
buildJobQueue = deque(buildConfigs.items())
maxActiveBuilds = multiprocessing.cpu_count()
activeBuilds = set()
while len(buildJobQueue) > 0 or len(activeBuilds) > 0:
    # Process finished builds
    for build in activeBuilds.copy():
        if build.process.poll() == None:
            # Build is still running
            continue

        # Build has finished
        activeBuilds.remove(build)
        build.logFile.close()
        if build.process.returncode != 0:
            print("Building \"{0}\" failed (exit code {1}). See log: {2}".format(build.configName, build.process.returncode, build.logFilePath))

    # If we don't have more jobs, we must still wait for the active ones to finish
    # Otherwise, we must wait for a worker to become available
    workerIsAvailable = len(activeBuilds) < maxActiveBuilds
    haveMoreJobs = len(buildJobQueue) > 0
    if not haveMoreJobs or not workerIsAvailable:
        time.sleep(1)
        continue

    # Run a new build
    (configName, config) = buildJobQueue.popleft()
    print("Building config: {0}".format(configName))

    os.chdir(libDir)

    newBuild = BuildProcessDetails(configName)
    newBuild.logFilePath = os.path.join(libDir, "build.{0}.log".format(configName))
    newBuild.logFile = codecs.open(newBuild.logFilePath, "w+", encoding="utf-8")
    newBuild.process = subprocess.Popen([
            "msbuild",
            os.path.join(libDir, "{0}.sln".format(libName)),
            "/nologo", "/t:Rebuild", "/p:Configuration={0}".format(configName)
        ], stdout=newBuild.logFile)
    activeBuilds.add(newBuild)

print("Done!")
