@echo off
setlocal
cd /d "%~dp0"

rem ==========================================================
rem  Lab 4 / task 4 - HttpUnit memory leak: before/after demo
rem  Just run this file. Nothing else is needed.
rem ==========================================================

set "JAVAC=javac"
set "JAVA=java"
set "JARTOOL=jar"

where javac >nul 2>nul
if errorlevel 1 (
  if exist "C:\Program Files\Java\jdk-17\bin\javac.exe" (
    set "JAVAC=C:\Program Files\Java\jdk-17\bin\javac.exe"
    set "JAVA=C:\Program Files\Java\jdk-17\bin\java.exe"
    set "JARTOOL=C:\Program Files\Java\jdk-17\bin\jar.exe"
  ) else (
    echo [ERROR] javac not found. Add JDK bin to PATH or edit this file.
    pause
    exit /b 1
  )
)

set N=10000

echo.
echo === [1/3] preparing java.xml patch module ===
if not exist patch mkdir patch
pushd patch
"%JARTOOL%" xf ..\lib\xerces-2.4.0.jar org/w3c/dom/ls
popd

echo === [2/3] compiling ORIGINAL sources (with the bug) ===
if not exist build\classes-before mkdir build\classes-before
"%JAVAC%" -encoding UTF-8 --patch-module java.xml=patch -cp "lib\*" -d build\classes-before src\HelloWorld.java src\Main.java tools\Diag.java
if errorlevel 1 goto :err

echo === [3/3] compiling FIXED sources ===
if not exist build\classes-after mkdir build\classes-after
"%JAVAC%" -encoding UTF-8 --patch-module java.xml=patch -cp "lib\*" -d build\classes-after src-fixed\HelloWorld.java src-fixed\Main.java tools\Diag.java
if errorlevel 1 goto :err

echo.
echo ==============================================================
echo  [1] BEFORE FIX - original servlet, no cleanup
echo      expected: used memory grows, scriptErrors grows
echo ==============================================================
"%JAVA%" --patch-module java.xml=patch -Xmx256m -cp "build\classes-before;lib\*" Diag %N%

echo.
echo ==============================================================
echo  [2] FIX #1 - same buggy servlet + clearScriptErrorMessages()
echo      expected: memory flat, scriptErrors = 0
echo ==============================================================
"%JAVA%" --patch-module java.xml=patch -Xmx256m -cp "build\classes-before;lib\*" Diag %N% fix

echo.
echo ==============================================================
echo  [3] FIX #2 - servlet fixed (document.write)
echo      expected: memory flat, scriptErrors = 0
echo ==============================================================
"%JAVA%" --patch-module java.xml=patch -Xmx256m -cp "build\classes-after;lib\*" Diag %N%

echo.
echo === done ===
pause
exit /b 0

:err
echo.
echo [ERROR] compilation failed, see messages above.
pause
exit /b 1
