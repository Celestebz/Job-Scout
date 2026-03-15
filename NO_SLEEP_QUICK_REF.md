# MacBook 合盖运行 Job Scout - 快速参考

## 🚀 一键部署（合盖运行版）

```bash
cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout
./scripts/quick_deploy_no_sleep.sh
```

## ✅ 技术原理

```
每天 18:00
    ↓
launchd 触发定时任务
    ↓
caffeinate -d -t 900 (阻止休眠15分钟)
    ↓
执行 /job-scout 命令
    ↓
生成报告 + 更新数据库
    ↓
自动恢复休眠
```

## 📋 工作流程

1. **17:59** - 系统准备执行任务
2. **18:00** - caffeinate 自动启动，阻止系统休眠
3. **18:00-18:15** - Job Scout 执行搜索（最多15分钟）
4. **18:15** - 任务完成，caffeinate 自动释放，系统可休眠

## ⚠️ 重要提示

### 必须条件
- ✅ MacBook 已接通电源
- ✅ 定时任务已加载
- ✅ caffeinate 命令可用（macOS 内置）

### 注意事项
- 🔥 **散热**: 合盖时散热受限，建议使用散热支架
- 🔋 **电量**: 每次执行消耗约 2-3% 电量
- 💾 **备份**: 建议定期备份数据

## 🔍 验证清单

### 部署后验证

```bash
# 1. 检查任务状态
launchctl list | grep job-scout

# 2. 手动测试（重要！）
./scripts/run_job_scout_no_sleep.sh

# 3. 查看日志
tail -f logs/scheduler.log

# 4. 验证 caffeinate 可用
which caffeinate
# 应该输出: /usr/bin/caffeinate
```

### 合盖测试

```bash
# 1. 启动手动测试
./scripts/run_job_scout_no_sleep.sh

# 2. 立即合上 MacBook 盖子

# 3. 等待 5-10 分钟

# 4. 打开盖子，检查:
ls -lt result/job_scout_*.xlsx | head -1
cat logs/scheduler.log | tail -20

# 应该看到新的报告和执行日志
```

## 🛠️ 常用命令

```bash
# 查看任务状态
launchctl list | grep job-scout

# 查看实时日志
tail -f logs/scheduler.log

# 停止任务
launchctl stop com.user.job-scout.daily

# 启动任务
launchctl start com.user.job-scout.daily

# 手动测试（推荐首次使用）
./scripts/run_job_scout_no_sleep.sh

# 检查 caffeinate 进程
ps aux | grep caffeinate
```

## 📊 监控和维护

### 每日检查

```bash
# 检查今天是否执行
grep "$(date '+%Y-%m-%d')" logs/scheduler.log

# 查看最新报告
ls -lt result/job_scout_*.xlsx | head -1

# 检查岗位数量
python3 -c "import json; print(json.load(open('job_history.json'))['total_jobs'])"
```

### 每周维护

```bash
# 查看执行统计
echo "成功次数: $(grep "✅" logs/scheduler.log | wc -l)"
echo "失败次数: $(grep "❌" logs/scheduler.log | wc -l)"

# 清理旧日志（保留7天）
find logs -name "*.log" -mtime +7 -delete

# 归档旧报告
mkdir -p result/archived
ls -t result/job_scout_*.xlsx | tail -n +8 | xargs -I {} mv {} result/archived/
```

## 🔧 高级配置

### 修改执行时间

编辑 `com.user.job-scout.daily.plist`:

```bash
nano ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 修改时间（例如改为 20:00）
<key>Hour</key>
<integer>20</integer>
<key>Minute</key>
<integer>0</integer>

# 重新加载
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist
```

### 调整 caffeinate 时长

如果任务需要更长时间，修改脚本中的 `-t` 参数:

```bash
# 编辑脚本
nano scripts/run_job_scout_no_sleep.sh

# 找到 caffeinate 行，修改时长（秒）
# 900 = 15分钟
# 1800 = 30分钟
# 3600 = 60分钟
```

### 添加桌面通知

在 `scripts/run_job_scout_no_sleep.sh` 末尾添加:

```bash
# 任务完成后发送通知
osascript -e 'display notification "✅ 岗位搜索完成，报告已生成" with title "Job Scout 每日任务"'
```

## ⚠️ 故障排查

### 问题1: 任务未执行

**检查**:
```bash
# 1. 确认任务已加载
launchctl list | grep job-scout

# 2. 查看错误日志
cat logs/stderr.log

# 3. 手动测试
./scripts/run_job_scout_no_sleep.sh

# 4. 检查 caffeinate
which caffeinate
```

### 问题2: 合盖后任务停止

**原因**: caffeinate 未正常工作

**解决方案**:
```bash
# 验证 caffeinate 功能
caffeinate -d -t 10 echo "测试成功"

# 如果失败，可能需要:
# - 重启系统
# - 检查系统设置
```

### 问题3: MacBook 过热

**解决方案**:
- ✅ 使用散热支架
- ✅ 放在硬质表面
- ✅ 避免在床、沙发使用
- ✅ 监控温度: `sudo powermetrics --samplers cpu_power -i 1000`

### 问题4: 电量消耗过快

**解决方案**:
- ✅ 确保连接电源
- ✅ 减少合盖使用时间
- ✅ 考虑使用定时唤醒方案（见完整文档）

## 🎯 优化建议

### 1. 添加智能唤醒

如果希望更省电，可以使用定时唤醒方案：

```bash
# 参考 NO_SLEEP_GUIDE.md 中的"方案3: launchd 定时唤醒"
```

### 2. 使用第三方工具

如果需要图形界面控制：

```bash
# 安装 Amphetamine（Mac App Store 免费）
# 或
brew install --cask keepingyouawake
```

### 3. 监控系统健康

```bash
# 查看电源状态
pmset -g

# 查看电池健康
system_profiler SPPowerDataType | grep -i "condition"

# 监控温度
sudo powermetrics --samplers cpu_power -i 1000
```

## 📚 完整文档

详细技术方案和配置说明，请查看:
- `NO_SLEEP_GUIDE.md` - 完整指南
- `SCHEDULED_EXECUTION_GUIDE.md` - 定时任务原理

## 🆘 获取帮助

```bash
# 查看完整文档
cat NO_SLEEP_GUIDE.md

# 查看快速参考
cat SCHEDULER_QUICK_REF.md

# 重新部署
./scripts/quick_deploy_no_sleep.sh
```

---

## ✅ 快速测试命令

```bash
# 一键测试（推荐首次使用）
cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout
./scripts/run_job_scout_no_sleep.sh && \
echo "✅ 测试成功！" && \
ls -lt result/job_scout_*.xlsx | head -1
```

---

**技术支持**:
- 完整文档: `NO_SLEEP_GUIDE.md`
- 配置文件: `com.user.job-scout.daily.plist`
- 执行脚本: `scripts/run_job_scout_no_sleep.sh`
