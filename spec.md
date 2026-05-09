Objective

The purpose of this repo is to show how to develop, test, and deploy python and shell scripts as brew packages (formula)
using all the best practices for python, shell scripts, and brew, including dependency and version management. Includes

- usage
    - how a user should discover, install, and update the package
    - for the server component, user should be be able to launch it both normally, and also manage its lifecycle using brew service

- developer setup
    - organizing the repo
    - managing dependencies
    - testing
        - running tests ( using pytest etc
            - unit tests
            - how to test the python client ( against a mock server)
            - how to test the shell script ( against a mock server ) 
        - running the apps as a developer
        - Note that the developer may have installed a previous version of the package. So when running tests, the code
          should always pickup the latest version from the repo
    - deployment
        - deploy using brew
        - Github for formulae https://github.com/Sdaas/homebrew-tap
        - Local Repo ~/dev/homebrew-tap
        - There should be a single release.sh script to manage the entire release process - no manual steps pls

Functional Requirements

to demonstrate this functionality, there are three pieces of code

- server : Thiis is a python server with a REST API
    - /health : returns 200 ok and date time if server is running
    - All request are logged to a file in this repo
    - The user can eitehr launch this "normally" 
    - User should be able to manage lifecycle of this as a brew service 
    - Povide the usual --version --help and --verbose option
    - --port default is 8100

- python client
    - users the request library to ping the /health and print the respose
    - Pevide the usual --version --help and --verbose option
    - --port default is 8100

- shell client
    - uses curl ping the /health and print the respose
    - Pevide the usual --version --help and --verbose option
    - --port default is 8100

Expected Output

- README.md that explains the usage of this ( how to discover, install, run, and update )
- docs/developer-guide.md
    - This shold be a tutorial for a developer to understnad all aspects of 
        - architecture
        - development and testing
        - release and depploy
- docs/brew-packaging-guide : OVerview of how brew packages are released and managed
- docs/python-packaging-guide : Overview of how dependency management is done

Important

- Brew service management should be used wheere applicable
- Developers may already have a brew-installed version - Tests and local runs MUST always use repo-local code.
- Never rely on globally installed binaries during development.