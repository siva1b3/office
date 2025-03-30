#!/bin/bash

echo "=================================="
echo "🚀 Starting Docker Build Process..."
echo "=================================="

# Run the Docker build command with the correct context
docker build -t python_app_sub:latest -f Dockerfile .  # <-- Add the build context (.)

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker image 'express-deps:latest' built successfully!"
else
    echo "❌ Docker build failed. Check the logs for details."
fi

echo "=================================="
echo "🎯 Build Process Completed"
echo "=================================="
