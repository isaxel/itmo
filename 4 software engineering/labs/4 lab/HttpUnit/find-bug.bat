@echo off
setlocal
cd /d "%~dp0"

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

rem --- which servlet to compile against ---
set "SRCHW=src\HelloWorld.java"
set "OUTDIR=build\classes-demo"
set "GCLOG=gc.log"
set "LABEL=ORIGINAL - servlet with the document.wr typo"
set "EXPECT=heap floor climbs 1MB -^> 14MB, GC starts thrashing"

if /I "%~1"=="fixed" (
  set "SRCHW=src-fixed\HelloWorld.java"
  set "OUTDIR=build\classes-demo-fixed"
  set "GCLOG=gc-fixed.log"
  set "LABEL=FIXED - servlet uses document.write"
  set "EXPECT=heap floor stays flat around 4MB"
)

if not exist patch mkdir patch
pushd patch
"%JARTOOL%" xf ..\lib\xerces-2.4.0.jar org/w3c/dom/ls
popd

if not exist "%OUTDIR%" mkdir "%OUTDIR%"
"%JAVAC%" -encoding UTF-8 --patch-module java.xml=patch -cp "lib\*" -d "%OUTDIR%" src-demo\Main.java %SRCHW%
if errorlevel 1 (
  echo [ERROR] compilation failed
  pause
  exit /b 1
)

echo.
echo  %LABEL%
echo  expected: %EXPECT%
echo.
echo  GC log -^> %GCLOG%
echo  Attach VisualVM to process "Main", then:
echo    Monitor -^> Heap, Perform GC (twice, 30s apart)
echo    Sampler -^> Memory
echo  Ctrl+C to stop.
echo.

"%JAVA%" --patch-module java.xml=patch -Xmx16m -Xlog:gc:file=%GCLOG% -cp "%OUTDIR%;lib\*" Main
