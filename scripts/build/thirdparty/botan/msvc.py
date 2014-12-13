# This script can be used with Visual C++ to build all the configurations we may use.
# Run this script using Python 2.7 when building Botan 1.10.5, because the configure-script fails with later versions of Python.
# Build output resides in the library directory, in a sub-directory named after the build config.

# Name of the library to build (must match directory- and file names)
libName = "botan"

import os, subprocess, re, codecs, multiprocessing, time
from collections import deque

class BuildProcessDetails:
    def __init__(self, configName):
        self.configName = configName
        self.process = None
        self.logFile = None
        self.logFilePath = ""

scriptDir = os.path.split(os.path.abspath(__file__))[0]
libDir = os.path.realpath(os.path.join(scriptDir, os.path.join("../../../../thirdparty/{0}".format(libName))))
buildOutputRootDir = os.path.realpath(os.path.join(libDir, "bin"))
os.chdir(libDir)

# The build configurations
buildConfigs = {
    "DebugLib": {
        "botan": ["--disable-shared", "--enable-debug"],
        "compiler": {
            "cxx": ""
        }
    },
    "DebugDll": {
        "botan": ["--enable-shared", "--enable-debug"],
        "compiler": {
            "cxx": ""
        }
    },
    "ReleaseLib": {
        "botan": ["--disable-shared", "--disable-debug"],
        "compiler": {
            "cxx": ""
        }
    },
    "ReleaseLibMT": {
        "botan": ["--disable-shared", "--disable-debug"],
        "compiler": {
            "cxx": "cl /MT"
        }
    },
    "ReleaseDll": {
        "botan": ["--enable-shared", "--disable-debug"],
        "compiler": {
            "cxx": ""
        }
    }
}

# Clean the repository
subprocess.check_call("git reset --hard")
subprocess.check_call("git clean -d -x -f")

# Prepare configs for building
print("")
print("Configuring...")
for configName, config in buildConfigs.items():
    outputDir = os.path.join(buildOutputRootDir, configName)
    os.makedirs(outputDir)
    os.chdir(outputDir)
    config["_outputDir"] = outputDir

    returnCode = subprocess.check_call([
            "python",
            os.path.join(libDir, "configure.py"),
            "--quiet", "--cpu", "x86", "--cc", "msvc"
        ]
        + config["botan"]
    )

    if returnCode != 0:
        print("Configuring \"{0}\" failed (exit code {1}).".format(configName, returnCode))

    # Modify makefile
    with codecs.open("Makefile", "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        if config["compiler"]["cxx"]:
            content = re.sub(r"^(CXX\s*=\s*).*$", "\\1" + config["compiler"]["cxx"], content, 1, re.MULTILINE)
        f.write(content)

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

    outputDir = config["_outputDir"]
    os.chdir(outputDir)

    newBuild = BuildProcessDetails(configName)
    newBuild.logFilePath = os.path.join(outputDir, "build.log")
    newBuild.logFile = codecs.open(newBuild.logFilePath, "w+", encoding="utf-8")
    newBuild.process = subprocess.Popen(["nmake", "/NOLOGO"], stdout=newBuild.logFile)
    activeBuilds.add(newBuild)

print("Done!")
