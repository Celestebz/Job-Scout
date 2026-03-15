# Job Scout 定时执行技术方案

## 📊 技术可行性分析

### ✅ 方案一：Claude Code 原生 `/loop` 命令（推荐）

**优势**：
- ✅ 官方支持，稳定可靠
- ✅ 无需额外依赖
- ✅ 直接调用斜杠命令
- ✅ 最多支持 3 天定时

**限制**：
- ⚠️ 定时任务最长只能设置 **3天**
- ⚠️ 需要保持 Claude Code 会话活跃

**适用场景**：短期测试（1-3天）

---

### ✅ 方案二：macOS launchd + Claude CLI（生产推荐）

**优势**：
- ✅ 系统级定时任务，稳定可靠
- ✅ 支持长期定时（每天、每周）
- ✅ 开机自启动
- ✅ 日志记录完善

**实现方式**：
```bash
# 1. 创建执行脚本
# 2. 配置 launchd plist 文件
# 3. 加载定时任务
```

---

## 🎯 推荐方案：launchd + Claude CLI

### 架构设计

```
macOS launchd (每天18:00触发)
    ↓
run_job_scout.sh (执行脚本)
    ↓
claude /job-scout 帮我找工作 (调用斜杠命令)
    ↓
生成 XLSX 报告
    ↓
发送通知（可选）
```

---

## 📝 完整实施方案

### Step 1: 创建执行脚本

```bash
#!/bin/bash
# 文件位置: /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout/scripts/run_job_scout.sh

# 设置项目路径
PROJECT_DIR="/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout"
cd "$PROJECT_DIR" || exit 1

# 记录开始时间
echo "=== Job Scout 定时任务开始: $(date) ===" >> "$PROJECT_DIR/logs/scheduler.log"

# 执行 job-scout 命令
claude /job-scout 帮我找工作 >> "$PROJECT_DIR/logs/scheduler.log" 2>&1

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ Job Scout 执行成功: $(date)" >> "$PROJECT_DIR/logs/scheduler.log"
else
    echo "❌ Job Scout 执行失败: $(date)" >> "$PROJECT_DIR/logs/scheduler.log"
fi

echo "=== Job Scout 定时任务结束: $(date) ===" >> "$PROJECT_DIR/logs/scheduler.log"
echo "" >> "$PROJECT_DIR/logs/scheduler.log"
```

### Step 2: 创建 launchd 配置文件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- 任务标识 -->
    <key>Label</key>
    <string>com.user.job-scout.daily</string>

    <!-- 要执行的程序 -->
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/scripts/run_job_scout.sh</string>
    </array>

    <!-- 定时规则: 每天18:00执行 -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <!-- 标准输出日志 -->
    <key>StandardOutPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/stdout.log</string>

    <!-- 错误输出日志 -->
    <key>StandardErrorPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/stderr.log</string>

    <!-- 环境变量 -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <!-- 如果错过执行时间，立即执行一次 -->
    <key>MissedJobBehavior</key>
    <string>RunOnce</string>
</dict>
</plist>
```

### Step 3: 安装和启动定时任务

```bash
# 1. 创建日志目录
mkdir -p /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout/logs

# 2. 赋予执行脚本权限
chmod +x /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout/scripts/run_job_scout.sh

# 3. 复制 plist 文件到 LaunchAgents
cp com.user.job-scout.daily.plist ~/Library/LaunchAgents/

# 4. 加载定时任务
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 5. 启动定时任务
launchctl start com.user.job-scout.daily

# 6. 查看任务状态
launchctl list | grep job-scout
```

### Step 4: 管理定时任务

```bash
# 停止任务
launchctl stop com.user.job-scout.daily

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 重新加载（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 查看日志
tail -f /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout/logs/scheduler.log
```

---

## ⚠️ 潜在风险和注意事项

### 1. Claude Code 会话限制

**问题**：
- CLI 模式下可能需要处理权限确认
- 如果使用 `--dangerously-skip-permissions`，需确保安全

**解决方案**：
```bash
# 使用已配置的 alias
alias claude='claude --dangerously-skip-permissions'
```

### 2. 网络连接问题

**问题**：
- WebSearch 依赖网络连接
- 18:00 网络高峰期可能超时

**解决方案**：
```bash
# 添加重试机制
#!/bin/bash
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    claude /job-scout 帮我找工作 && break
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 60  # 等待1分钟后重试
done
```

### 3. WebSearch 配额限制

**问题**：
- WebSearch 有速率限制（429 error）
- 每天多次搜索可能触发限制

**解决方案**：
- 控制搜索频率（每天1次相对安全）
- 添加错误处理和日志记录

### 4. 磁盘空间管理

**问题**：
- 日志文件持续增长
- XLSX 报告文件积累

**解决方案**：
```bash
# 添加日志清理任务
# 清理30天前的日志
find /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout/logs -name "*.log" -mtime +30 -delete

# 归档旧报告（保留最近7天的在result目录）
# 创建 archived 目录存放旧报告
```

### 5. 系统休眠影响

**问题**：
- macOS 18:00 可能处于休眠状态
- 笔记本电脑可能关机

**解决方案**：
```xml
<!-- 在 plist 中添加唤醒设置 -->
<key>WakeFromSleep</key>
<true/>
```

或者设置在更合理的时间：
```xml
<!-- 改为 19:00 或 20:00 -->
<key>Hour</key>
<integer>19</integer>
```

### 6. 权限问题

**问题**：
- 脚本执行权限不足
- 文件写入权限问题

**解决方案**：
```bash
# 确保脚本有执行权限
chmod +x scripts/run_job_scout.sh

# 确保目录可写
chmod -R u+w result/ logs/
```

### 7. Claude CLI 路径问题

**问题**：
- launchd 环境变量与用户 shell 不同
- 可能找不到 `claude` 命令

**解决方案**：
```bash
# 使用完整路径
which claude  # 获取完整路径，例如 /usr/local/bin/claude

# 在脚本中使用完整路径
/usr/local/bin/claude /job-scout 帮我找工作
```

---

## 📊 监控和日志

### 日志结构

```
job-scout/
├── logs/
│   ├── scheduler.log       # 主日志（执行记录）
│   ├── stdout.log          # 标准输出
│   ├── stderr.log          # 错误输出
│   └── error_report.txt    # 错误汇总
└── result/
    └── job_scout_*.xlsx    # 生成的报告
```

### 监控脚本

```bash
#!/bin/bash
# check_job_scout.sh - 检查定时任务健康状态

LOG_FILE="/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/scheduler.log"
TODAY=$(date +"%Y-%m-%d")

# 检查今天是否执行过
if grep -q "$TODAY" "$LOG_FILE"; then
    echo "✅ 今日任务已执行"
    # 显示最新执行结果
    grep "$TODAY" "$LOG_FILE" | tail -5
else
    echo "⚠️ 今日任务尚未执行"
    # 显示任务状态
    launchctl list | grep job-scout
fi
```

---

## 🚀 快速开始

### 一键部署脚本

```bash
#!/bin/bash
# deploy_scheduler.sh - 一键部署定时任务

cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout

# 1. 创建必要目录
mkdir -p logs scripts

# 2. 创建执行脚本
cat > scripts/run_job_scout.sh << 'EOF'
#!/bin/bash
PROJECT_DIR="/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout"
cd "$PROJECT_DIR" || exit 1

echo "=== Job Scout 定时任务开始: $(date) ===" >> "$PROJECT_DIR/logs/scheduler.log"
claude /job-scout 帮我找工作 >> "$PROJECT_DIR/logs/scheduler.log" 2>&1
echo "=== Job Scout 定时任务结束: $(date) ===" >> "$PROJECT_DIR/logs/scheduler.log"
EOF

chmod +x scripts/run_job_scout.sh

# 3. 创建 plist 文件
cat > ~/Library/LaunchAgents/com.user.job-scout.daily.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.job-scout.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/scripts/run_job_scout.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/stderr.log</string>
</dict>
</plist>
EOF

# 4. 加载任务
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

echo "✅ 定时任务部署完成！"
echo "📅 每天晚上 18:00 自动执行"
echo "📁 日志位置: logs/scheduler.log"
echo "🔍 查看状态: launchctl list | grep job-scout"
```

---

## 📋 总结

### 推荐方案
✅ **macOS launchd + Claude CLI**

### 优势
- 系统级支持，稳定可靠
- 长期定时无限制
- 开机自启动
- 完善的日志管理

### 关键注意事项
1. ⚠️ 确保网络连接稳定
2. ⚠️ 注意 WebSearch 配额限制
3. ⚠️ 定期清理日志文件
4. ⚠️ 监控任务执行状态
5. ⚠️ 处理错误和重试机制

### 下一步
1. 部署一键部署脚本
2. 测试定时任务执行
3. 监控日志和结果
4. 根据实际情况调整时间

---

**Sources:**
- [Run prompts on a schedule - Claude Code Docs](https://code.claude.com/docs/en/scheduled-tasks)
- [Claude Code Scheduled Tasks Feature Overview - YouTube](https://www.youtube.com/watch?v=LfkeFVXdrIs)
- [Scheduled Tasks: How to Put Claude on Autopilot - atal upadhyay](https://atalupadhyay.wordpress.com/2026/03/02/scheduled-tasks-how-to-put-claude-on-autopilot/)
- [macOS launchd Documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
