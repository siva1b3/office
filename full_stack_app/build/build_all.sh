#!/bin/bash

# Move up one directory
cd ..

# Function to build images for each application
build_image() {
    echo "=================================="
    echo "🚀 Running build for $1"
    echo "=================================="
    cd "$1" || exit 1
    ./build_image.sh
    cd .. || exit 1
}

# Run build_image.sh for each application
build_image "python_app_add"
build_image "python_app_div"
build_image "python_app_mul"
build_image "python_app_sub"
build_image "express_app"

echo "=================================="
echo "🎯 All build processes completed"
echo "=================================="

# Pause (for manual execution, remove if running in a script)
read -p "Press any key to continue..."
