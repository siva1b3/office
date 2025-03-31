@echo off

cd ..

REM Run build_image.bat for python_app_add
echo ==================================
echo 🚀 Running build for python_app_add
echo ==================================
cd python_app_add
call build_image.bat
cd ..


REM Run build_image.bat for python_app_div
echo ==================================
echo 🚀 Running build for python_app_div
echo ==================================
cd python_app_div
call build_image.bat
cd ..


REM Run build_image.bat for python_app_mul
echo ==================================
echo 🚀 Running build for python_app_mul
echo ==================================
cd python_app_mul
call build_image.bat
cd ..


REM Run build_image.bat for python_app_sub
echo ==================================
echo 🚀 Running build for python_app_sub
echo ==================================
cd python_app_sub
call build_image.bat
cd ..

REM Run build_image.bat for express_app
echo ==================================
echo 🚀 Running build for express_app
echo ==================================
cd express_app
call build_image.bat
cd ..

echo ==================================
echo 🎯 All build processes completed
echo ==================================
pause
