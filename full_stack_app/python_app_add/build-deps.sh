#!/bin/bash

echo "=================================="
echo "🚀 Starting Docker Build Process..."
echo "=================================="

# Run the Docker build command with the correct context
docker build -t python-pika-jupyter:latest -f Dockerfile.deps .  # <-- Add the build context (.)

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker image 'express-deps:latest' built successfully!"
else
    echo "❌ Docker build failed. Check the logs for details."
fi

echo "=================================="
echo "🎯 Build Process Completed"
echo "=================================="
