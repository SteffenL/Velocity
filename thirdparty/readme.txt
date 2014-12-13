================================================================================
Third-party libraries
================================================================================

The source code of third-party libraries can be bundled to make the main project more self-contained.

If a third-party library has an official Git repository, we can add it as a submodule (preferably after forking it); otherwise, the files can be added into the main repository.


File structure
--------------------------------------------------------------------------------

<library name>                  Source code of a library.
<toolset>                       Toolset-specific libraries.
    <library name>              Source code of a library.
