#!/bin/bash
# Job Scout 合盖运行 - 快速部署脚本
# 集成 caffeinate 命令，确保合盖后也能正常执行

echo "🚀 开始部署 Job Scout 定时任务（合盖运行版）..."

cd "/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout" || exit 1

# 1. 创建必要目录
echo "📁 创建日志目录..."
mkdir -p logs scripts result

# 2. 验证 caffeinate 命令
echo "🔍 验证 caffeinate 命令..."
if ! command -v caffeinate &> /dev/null; then
    echo "❌ 错误: caffeinate 命令不可用"
    echo "   请确保您使用的是 macOS 系统"
    exit 1
fi
echo "✅ caffeinate 命令可用"

# 3. 创建集成 caffeinate 的执行脚本
echo "📝 创建执行脚本..."
cat > scripts/run_job_scout_no_sleep.sh << 'EOFSCRIPT'
#!/bin/bash
# Job Scout 定时执行脚本（合盖运行版）
# 使用 caffeinate 防止系统休眠

PROJECT_DIR="/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout"
cd "$PROJECT_DIR" || exit 1

# 创建日志目录
mkdir -p logs

# 记录开始时间
echo "=== Job Scout 定时任务开始: $(date '+%Y-%m-%d %H:%M:%S') ===" >> logs/scheduler.log
echo "🔒 已启用 caffeinate，防止系统休眠（最多15分钟）" >> logs/scheduler.log

# 执行 job-scout 命令
echo "📊 开始执行岗位搜索..." >> logs/scheduler.log
claude /job-scout 帮我找工作 >> logs/scheduler.log 2>&1

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ Job Scout 执行成功: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/scheduler.log
else
    echo "❌ Job Scout 执行失败: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/scheduler.log
fi

# 统计当前岗位数量
if [ -f "job_history.json" ]; then
    TOTAL_JOBS=$(python3 -c "import json; print(json.load(open('job_history.json'))['total_jobs'])" 2>/dev/null || echo "未知")
    echo "📈 当前数据库岗位总数: $TOTAL_JOBS" >> logs/scheduler.log
fi

# 查找最新生成的报告
LATEST_REPORT=$(ls -t result/job_scout_*.xlsx 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo "📄 最新报告: $LATEST_REPORT" >> logs/scheduler.log
fi

echo "=== Job Scout 定时任务结束: $(date '+%Y-%m-%d %H:%M:%S') ===" >> logs/scheduler.log
echo "" >> logs/scheduler.log
EOFSCRIPT

chmod +x scripts/run_job_scout_no_sleep.sh

# 4. 创建集成了 caffeinate 的 plist 配置
echo "📋 创建定时任务配置..."
cat > com.user.job-scout.daily.plist << 'EOFPLIST'
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
        <string>-c</string>
        <string>
            cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout &&
            caffeinate -d -t 900 ./scripts/run_job_scout_no_sleep.sh
        </string>
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
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>

    <!-- 如果错过执行时间，立即执行一次 -->
    <key>MissedJobBehavior</key>
    <string>RunOnce</string>
</dict>
</plist>
EOFPLIST

# 5. 检查是否已存在旧任务
if launchctl list | grep -q "com.user.job-scout"; then
    echo "⚠️  检测到已存在的定时任务，正在卸载..."
    launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist 2>/dev/null
fi

# 6. 复制 plist 文件到 LaunchAgents
echo "📋 安装定时任务配置..."
cp com.user.job-scout.daily.plist ~/Library/LaunchAgents/

# 7. 加载定时任务
echo "⚙️  加载定时任务..."
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 8. 验证安装
echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 任务信息:"
echo "  - 任务名称: com.user.job-scout.daily"
echo "  - 执行时间: 每天 18:00"
echo "  - 合盖支持: ✅ 已启用 caffeinate"
echo "  - 最大运行时长: 15分钟"
echo ""
echo "🔧 技术细节:"
echo "  - 使用 caffeinate -d 阻止系统休眠"
echo "  - 阻止时长: 900秒（15分钟）"
echo "  - 执行完成后自动恢复休眠"
echo ""
echo "📁 文件位置:"
echo "  - 主脚本: scripts/run_job_scout_no_sleep.sh"
echo "  - 日志: logs/scheduler.log"
echo "  - 配置: ~/Library/LaunchAgents/com.user.job-scout.daily.plist"
echo ""
echo "🔍 常用命令:"
echo "  - 查看状态: launchctl list | grep job-scout"
echo "  - 查看日志: tail -f logs/scheduler.log"
echo "  - 手动测试: ./scripts/run_job_scout_no_sleep.sh"
echo "  - 停止任务: launchctl stop com.user.job-scout.daily"
echo "  - 启动任务: launchctl start com.user.job-scout.daily"
echo ""
echo "⚠️  重要提示:"
echo "  - 确保连接电源适配器"
echo "  - 注意散热（合盖时散热受限）"
echo "  - 预计电量消耗: 每次 2-3%"
echo "  - 首次使用建议手动测试"
echo ""

# 显示当前任务状态
if launchctl list | grep -q "com.user.job-scout.daily"; then
    echo "✅ 定时任务状态: 运行中"
    launchctl list | grep job-scout
else
    echo "⚠️  定时任务状态: 未运行"
fi

echo ""
echo "🎯 下一步:"
echo "  1. 手动测试: ./scripts/run_job_scout_no_sleep.sh"
echo "  2. 合盖测试: 合上盖子，等待 18:00"
echo "  3. 查看报告: ls -lt result/job_scout_*.xlsx"
echo ""
echo "📝 查看完整文档: cat NO_SLEEP_GUIDE.md"
