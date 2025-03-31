@echo off

cd ..

REM Run build_image.bat for python_app_add_01
echo ==================================
echo 🚀 Running build for python_app_add_01
echo ==================================
cd python_app_add_01
call build_image.bat
cd ..

REM Run build_image.bat for python_app_add_02
echo ==================================
echo 🚀 Running build for python_app_add_02
echo ==================================
cd python_app_add_02
call build_image.bat
cd ..

REM Run build_image.bat for python_app_div_01
echo ==================================
echo 🚀 Running build for python_app_div_01
echo ==================================
cd python_app_div_01
call build_image.bat
cd ..

REM Run build_image.bat for python_app_div_02
echo ==================================
echo 🚀 Running build for python_app_div_02
echo ==================================
cd python_app_div_02
call build_image.bat
cd ..

REM Run build_image.bat for python_app_mul_01
echo ==================================
echo 🚀 Running build for python_app_mul_01
echo ==================================
cd python_app_mul_01
call build_image.bat
cd ..

REM Run build_image.bat for python_app_mul_02
echo ==================================
echo 🚀 Running build for python_app_mul_02
echo ==================================
cd python_app_mul_02
call build_image.bat
cd ..

REM Run build_image.bat for python_app_sub_01
echo ==================================
echo 🚀 Running build for python_app_sub_01
echo ==================================
cd python_app_sub_01
call build_image.bat
cd ..

REM Run build_image.bat for python_app_sub_02
echo ==================================
echo 🚀 Running build for python_app_sub_02
echo ==================================
cd python_app_sub_02
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
