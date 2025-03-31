@echo off

REM Display a start message to indicate the beginning of the Docker build process
echo ==================================
echo Starting Docker Build Process...
echo ==================================

REM Run the Docker build command with the appropriate context and Dockerfile
REM -t specifies the image name and tag (python-div-02-dep:latest)
REM -f specifies the Dockerfile to be used for the build (Dockerfile.deps)
REM The build context is set to the current directory (.)
docker build -t python-div-02-dep:latest -f Dockerfile.deps .

REM Check if the build was successful by checking the exit status of the last command
IF %ERRORLEVEL% EQU 0 (
    REM If the build was successful, print a success message
    echo Docker image 'python-div-02-dep:latest' built successfully!
) ELSE (
    REM If the build failed, print a failure message
    echo Docker build failed. Check the logs for details.
)

REM Display a completion message indicating that the build process is finished
echo ==================================
echo Build Process Completed
echo ==================================
