#!/bin/bash

# Display a start message to indicate the beginning of the Docker build process
echo "=================================="
echo "🚀 Starting Docker Build Process..."
echo "=================================="

# Run the Docker build command with the appropriate context and Dockerfile
# -t specifies the image name and tag (node_express:latest)
# -f specifies the Dockerfile to be used for the build (Dockerfile.deps)
# The build context is set to the current directory (.)
docker build -t node_express:latest -f Dockerfile.deps .  # <-- Add the build context (.)

# Check if the build was successful by checking the exit status of the last command ($?)
if [ $? -eq 0 ]; then
    # If the build was successful, print a success message
    echo "✅ Docker image 'node_express:latest' built successfully!"
else
    # If the build failed, print a failure message
    echo "❌ Docker build failed. Check the logs for details."
fi

# Display a completion message indicating that the build process is finished
echo "=================================="
echo "🎯 Build Process Completed"
echo "=================================="
