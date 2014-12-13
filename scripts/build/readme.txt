================================================================================
Build scripts
================================================================================

These scripts help automate configuration and building of the main project as well as third-party libraries. The scripts should be compatible with Python 2.7 and later if possible.


File structure
--------------------------------------------------------------------------------

thirdparty                          Third-party libraries.
    <library name>
        <toolset>.py                Toolset-specific build script.
<main project/library>              Main/Parent project or library.
    <toolset>.py                    Toolset-specific build script.


Building
--------------------------------------------------------------------------------

Microsoft Visual C++
    Toolset: msvc

    1. Open the Developer Command Prompt for Visual Studio.
    2. Run the build script using a command similar to this:
        python thirdparty\<library name>\<toolset>.py
