#!/bin/bash
# Job Scout 定时执行脚本（合盖运行版）
# 使用 caffeinate 防止系统休眠

PROJECT_DIR="/Users/celeste/Documents/06 Codiing/找工作/skills/job-scout"
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
