@echo off
cd /d "C:\Users\Administrator\Desktop"
start "日报监控" /min "C:\Users\Administrator\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\Users\Administrator\Desktop\日报监控触发器.py"
echo 监控已启动，日志见桌面日报运行日志.txt
timeout /t 3