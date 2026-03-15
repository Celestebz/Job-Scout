#!/bin/bash
# Job Scout 定时任务一键部署脚本

echo "🚀 开始部署 Job Scout 定时任务..."

# 进入项目目录
cd "/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout" || exit 1

# 1. 创建必要目录
echo "📁 创建日志目录..."
mkdir -p logs scripts result

# 2. 赋予执行脚本权限
echo "🔑 设置脚本权限..."
chmod +x scripts/run_job_scout.sh

# 3. 检查是否已存在旧的定时任务
if launchctl list | grep -q "com.user.job-scout"; then
    echo "⚠️  检测到已存在的定时任务，正在卸载..."
    launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist 2>/dev/null
fi

# 4. 复制 plist 文件到 LaunchAgents
echo "📋 安装定时任务配置..."
cp com.user.job-scout.daily.plist ~/Library/LaunchAgents/

# 5. 加载定时任务
echo "⚙️  加载定时任务..."
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 6. 验证安装
echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 任务信息:"
echo "  - 任务名称: com.user.job-scout.daily"
echo "  - 执行时间: 每天 18:00"
echo "  - 执行命令: /job-scout 帮我找工作"
echo ""
echo "📁 文件位置:"
echo "  - 脚本: scripts/run_job_scout.sh"
echo "  - 日志: logs/scheduler.log"
echo "  - 配置: ~/Library/LaunchAgents/com.user.job-scout.daily.plist"
echo ""
echo "🔍 常用命令:"
echo "  - 查看状态: launchctl list | grep job-scout"
echo "  - 查看日志: tail -f logs/scheduler.log"
echo "  - 停止任务: launchctl stop com.user.job-scout.daily"
echo "  - 启动任务: launchctl start com.user.job-scout.daily"
echo "  - 卸载任务: launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist"
echo ""

# 显示当前任务状态
if launchctl list | grep -q "com.user.job-scout.daily"; then
    echo "✅ 定时任务状态: 运行中"
    launchctl list | grep job-scout
else
    echo "⚠️  定时任务状态: 未运行"
fi

echo ""
echo "🎯 下一次执行: 今天 18:00"
echo "📝 查看完整文档: cat SCHEDULED_EXECUTION_GUIDE.md"
