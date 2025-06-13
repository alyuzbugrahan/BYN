@echo off
echo Starting BYN Frontend with Remote API Configuration...
echo.
echo API Configuration:
echo - Remote Server: http://3.65.227.81/api
echo - Debug Mode: Enabled
echo.
echo Make sure to:
echo 1. Check if the remote server is accessible
echo 2. Verify CORS settings on the backend
echo 3. Check browser console for detailed logs
echo.
pause
cd /d "c:\Users\ubora\Desktop\BYN\frontendNew"
npm run dev
