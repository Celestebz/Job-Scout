# Job Scout 定时任务 - 快速参考卡

## 🚀 一键部署

```bash
cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout
./scripts/deploy_scheduler.sh
```

## 📊 任务状态检查

```bash
# 查看任务是否运行
launchctl list | grep job-scout

# 查看执行日志
tail -f logs/scheduler.log

# 检查今天是否执行
grep "$(date '+%Y-%m-%d')" logs/scheduler.log
```

## 🛠️ 常用命令

```bash
# 手动测试执行
./scripts/run_job_scout.sh

# 停止定时任务
launchctl stop com.user.job-scout.daily

# 启动定时任务
launchctl start com.user.job-scout.daily

# 重新加载配置（修改后）
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 完全卸载
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist
rm ~/Library/LaunchAgents/com.user.job-scout.daily.plist
```

## ⚠️ 故障排查

### 问题1: 任务没有执行

**检查清单**:
```bash
# 1. 确认任务已加载
launchctl list | grep job-scout

# 2. 查看错误日志
cat logs/stderr.log

# 3. 检查脚本权限
ls -l scripts/run_job_scout.sh

# 4. 手动测试
./scripts/run_job_scout.sh
```

### 问题2: WebSearch 失败

**原因**: 网络问题或配额限制

**解决方案**:
- 检查网络连接
- 查看日志中的错误信息
- 等待配额重置（通常1小时）

### 问题3: Claude CLI 找不到

**原因**: PATH 环境变量问题

**解决方案**:
```bash
# 查找 claude 路径
which claude

# 在脚本中使用完整路径
# 编辑 scripts/run_job_scout.sh
# 将 claude 改为 /usr/local/bin/claude
```

## 📁 日志说明

| 日志文件 | 内容 |
|---------|------|
| `logs/scheduler.log` | 主日志（执行记录） |
| `logs/stdout.log` | 标准输出 |
| `logs/stderr.log` | 错误输出 |

## 🔄 修改执行时间

编辑 `com.user.job-scout.daily.plist`:

```xml
<!-- 修改为 19:30 -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>19</integer>
    <key>Minute</key>
    <integer>30</integer>
</dict>
```

然后重新加载:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist
```

## 📱 通知提醒（可选）

如需桌面通知，在 `scripts/run_job_scout.sh` 末尾添加:

```bash
# macOS 桌面通知
osascript -e 'display notification "Job Scout 岗位搜索完成" with title "✅ 每日岗位报告已生成"'
```

## 📊 性能监控

查看执行历史:
```bash
# 最近7次执行记录
grep "===" logs/scheduler.log | tail -14

# 统计成功率
grep "✅" logs/scheduler.log | wc -l
grep "❌" logs/scheduler.log | wc -l
```

## 🔐 安全建议

1. **定期清理日志**（保留30天）:
```bash
find logs -name "*.log" -mtime +30 -delete
```

2. **备份重要数据**:
```bash
# 备份岗位数据库
cp job_history.json "backups/job_history_$(date +%Y%m%d).json"
```

3. **监控磁盘空间**:
```bash
# 查看报告文件大小
du -sh result/
```

## 📞 获取帮助

- 完整文档: `SCHEDULED_EXECUTION_GUIDE.md`
- 官方文档: https://code.claude.com/docs/en/scheduled-tasks
- 问题反馈: GitHub Issues

---

**快速部署命令**:
```bash
cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout && ./scripts/deploy_scheduler.sh
```
