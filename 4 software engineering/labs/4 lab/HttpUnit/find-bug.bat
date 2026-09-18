@echo off
setlocal
cd /d "%~dp0"

rem ==========================================================
rem  Lab 4 / task 4 - LIVE DEMO under VisualVM
rem
rem    find-bug.bat          -> ORIGINAL servlet (the leak)
rem    find-bug.bat fixed    -> FIXED servlet, same speed
rem
rem  The accelerated copy of Main is GENERATED from src\Main.java
rem  into build\gen\ (one substitution: sleep 200 -> sleep 0).
rem  Nothing under src\ or src-fixed\ is modified.
rem
rem  Attach VisualVM: Window -> Applications -> Local -> Main
rem  Stop with Ctrl+C
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

if not exist "src\Main.java" (
  echo [ERROR] src\Main.java not found. Run this script from the HttpUnit folder.
  pause
  exit /b 1
)
if not exist "%SRCHW%" (
  echo [ERROR] %SRCHW% not found.
  pause
  exit /b 1
)

rem --- generate the accelerated Main from the ORIGINAL source ---
rem     single substitution: Thread.sleep(200) -> Thread.sleep(0)
if not exist build\gen mkdir build\gen
powershell -NoProfile -Command "$s=[IO.File]::ReadAllText('src\Main.java'); $s=$s.Replace('Thread.sleep(200)','Thread.sleep(0)'); [IO.File]::WriteAllText('build\gen\Main.java',$s,(New-Object Text.UTF8Encoding($false)))"
findstr /C:"Thread.sleep(0)" build\gen\Main.java >nul
if errorlevel 1 (
  echo [ERROR] could not generate the accelerated Main from src\Main.java
  echo         expected to find the text  Thread.sleep^(200^)  there.
  pause
  exit /b 1
)

rem --- patch module java.xml (old xerces clashes with JDK 9+) ---
if not exist patch mkdir patch
pushd patch
"%JARTOOL%" xf ..\lib\xerces-2.4.0.jar org/w3c/dom/ls
popd

if not exist "%OUTDIR%" mkdir "%OUTDIR%"
"%JAVAC%" -encoding UTF-8 --patch-module java.xml=patch -cp "lib\*" -d "%OUTDIR%" build\gen\Main.java %SRCHW%
if errorlevel 1 (
  echo [ERROR] compilation failed
  pause
  exit /b 1
)

echo.
echo ==========================================================
echo  %LABEL%
echo  expected: %EXPECT%
echo.
echo  GC log -^> %GCLOG%
echo  Attach VisualVM to process "Main", then:
echo    Monitor -^> Heap, Perform GC (twice, 30s apart)
echo    Sampler -^> Memory
echo  Ctrl+C to stop.
echo ==========================================================
echo.

"%JAVA%" --patch-module java.xml=patch -Xmx16m -Xlog:gc:file=%GCLOG% -cp "%OUTDIR%;lib\*" Main
