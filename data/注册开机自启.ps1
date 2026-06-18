$action = New-ScheduledTaskAction `
    -Execute "C:\Users\Administrator\AppData\Local\Python\bin\pythonw.exe" `
    -Argument "C:\Users\Administrator\Desktop\日报监控触发器.py" `
    -WorkingDirectory "C:\Users\Administrator\Desktop"

$trigger = New-ScheduledTaskTrigger -AtLogon

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName "日报监控触发器_开机自启" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host "开机自启任务已注册成功！" -ForegroundColor Green