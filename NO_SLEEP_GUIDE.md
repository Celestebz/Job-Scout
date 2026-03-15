# MacBook 合盖后运行 Job Scout - 完整指南

## 🎯 目标
让 MacBook 在合盖状态下，每天 18:00 自动执行 Job Scout 任务

## ⚠️ 重要提示

### macOS 合盖行为
- **默认**: 合盖 = 休眠（所有任务停止）
- **解决方案**: 阻止系统休眠，或使用唤醒功能

---

## 📋 解决方案对比

| 方案 | 难度 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **方案1: 系统设置** | ⭐ 简单 | 官方支持，稳定 | 需外接显示器 | ⭐⭐⭐⭐⭐ |
| **方案2: caffeine命令** | ⭐⭐ 简单 | 灵活，可定时 | 手动触发 | ⭐⭐⭐⭐ |
| **方案3: launchd唤醒** | ⭐⭐⭐ 中等 | 完全自动化 | 配置复杂 | ⭐⭐⭐ |
| **方案4: 第三方工具** | ⭐⭐ 简单 | 图形界面 | 需安装软件 | ⭐⭐⭐⭐ |

---

## ✅ 方案1: 系统设置（推荐 - 有外接显示器）

### 适用场景
- ✅ MacBook 连接外接显示器
- ✅ 使用电源适配器
- ✅ 希望合盖后继续工作

### 设置步骤

#### 1. 启用"盖上盖不休眠"

```bash
# 方法1: 图形界面（推荐）
系统设置 → 电池 → 选项 → 开启"当使用电源适配器且显示器关闭时防止自动睡眠"

# 方法2: 命令行
sudo pmset -c disablesleep 1
```

#### 2. 验证设置

```bash
# 查看当前设置
pmset -g

# 应该看到:
# disablesleep 1  (表示已启用)
```

#### 3. 测试合盖

1. 连接电源适配器
2. 连接外接显示器（可选）
3. 合上 MacBook 盖子
4. 观察外接显示器是否保持工作

### 优缺点

**优点**:
- ✅ 官方支持，稳定可靠
- ✅ 无需额外软件
- ✅ 合盖后完全正常工作

**缺点**:
- ⚠️ 需要连接电源
- ⚠️ 最好连接外接显示器
- ⚠️ 笔记本可能过热

### 注意事项

⚠️ **散热警告**:
- 合盖时散热会受影响
- 建议使用散热支架
- 避免在柔软表面（如床、沙发）使用
- 监控温度（使用 `sudo powermetrics --samplers cpu_power`）

---

## ✅ 方案2: caffeine 命令（推荐 - 无外接显示器）

### 适用场景
- ✅ 无外接显示器
- ✅ 需要临时阻止休眠
- ✅ 灵活控制休眠时间

### 使用方法

#### 1. 基础用法

```bash
# 阻止系统休眠（直到手动停止）
caffeinate -d

# 阻止休眠指定时间（秒）
caffeinate -d -t 3600  # 阻止1小时

# 阻止休眠直到指定命令完成
caffeinate -d your_command
```

#### 2. 创建定时唤醒脚本

```bash
#!/bin/bash
# 文件位置: scripts/prevent_sleep.sh

# 每天 17:55 到 18:10 阻止休眠
# 确保定时任务能够执行

START_TIME=$(date -v17H -v55M +%s)
CURRENT_TIME=$(date +%s)
WAIT_SECONDS=$((START_TIME - CURRENT_TIME))

if [ $WAIT_SECONDS -gt 0 ]; then
    echo "等待 $WAIT_SECONDS 秒后开始阻止休眠..."
    sleep $WAIT_SECONDS
fi

# 阻止休眠 15 分钟（给任务充足时间）
echo "开始阻止休眠..."
caffeinate -d -t 900 &
CAFFEINATE_PID=$!

echo "caffeinate PID: $CAFFEINATE_PID"

# 15分钟后自动释放
sleep 900
kill $CAFFEINATE_PID 2>/dev/null
echo "休眠阻止已释放"
```

#### 3. 集成到定时任务

修改 `com.user.job-scout.daily.plist`:

```xml
<!-- 在执行前先阻止休眠 -->
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>
        cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout &&
        caffeinate -d -t 900 ./scripts/run_job_scout.sh
    </string>
</array>
```

这样定时任务会：
1. 自动阻止休眠15分钟
2. 执行 Job Scout 任务
3. 完成后自动恢复休眠

### 优缺点

**优点**:
- ✅ 无需外接显示器
- ✅ 灵活控制阻止时长
- ✅ macOS 内置命令，无需安装
- ✅ 可以精确控制阻止时间

**缺点**:
- ⚠️ 需要提前启动（或集成到定时任务）
- ⚠️ 合盖时 MacBook 仍在工作，消耗电量

---

## ✅ 方案3: launchd 定时唤醒（高级）

### 适用场景
- ✅ 需要完全自动化
- ✅ MacBook 大部分时间合盖
- ✅ 不希望持续阻止休眠

### 实现原理

```
18:00 前几分钟 → 唤醒 MacBook → 执行任务 → 允许休眠
```

### 配置步骤

#### 1. 创建唤醒定时任务

创建 `com.user.job-scout.wake.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.job-scout.wake</string>

    <!-- 每天 17:55 唤醒（提前5分钟） -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>17</integer>
        <key>Minute</key>
        <integer>55</integer>
    </dict>

    <!-- 唤醒后执行 -->
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>
            <!-- 阻止休眠 -->
            caffeinate -d -t 900 &
            CAFFEINATE_PID=$!

            <!-- 等待到 18:00 -->
            sleep 300

            <!-- 执行任务 -->
            cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout
            ./scripts/run_job_scout.sh

            <!-- 释放阻止休眠 -->
            kill $CAFFEINATE_PID 2>/dev/null
        </string>
    </array>

    <key>StandardOutPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/wake.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout/logs/wake_error.log</string>
</dict>
</plist>
```

#### 2. 加载唤醒任务

```bash
# 复制到 LaunchAgents
cp com.user.job-scout.wake.plist ~/Library/LaunchAgents/

# 加载任务
launchctl load ~/Library/LaunchAgents/com.user.job-scout.wake.plist

# 验证
launchctl list | grep job-scout
```

#### 3. 修改主任务配置

修改 `com.user.job-scout.daily.plist`，移除定时执行，改为依赖唤醒任务：

```xml
<!-- 移除 StartCalendarInterval -->
<!-- 改为由唤醒任务手动触发 -->

<key>AbandonProcessGroup</key>
<true/>
```

### 优缺点

**优点**:
- ✅ 完全自动化
- ✅ MacBook 大部分时间可以正常休眠
- ✅ 节省电量

**缺点**:
- ⚠️ 配置复杂
- ⚠️ 需要两个定时任务协调
- ⚠️ 某些 MacBook 型号可能不支持定时唤醒

---

## ✅ 方案4: 第三方工具

### 推荐工具

#### 1. **Amphetamine**（免费，推荐）

**功能**:
- 阻止系统休眠
- 可设置触发条件（时间、电量等）
- 支持定时任务

**下载**: Mac App Store

**配置**:
1. 安装 Amphetamine
2. 创建新会话
3. 设置触发条件：
   - 时间: 每天 17:50 - 18:20
   - 触发器: 自动开始
4. 启用会话

#### 2. **KeepingYouAwake**（开源免费）

**功能**:
- 菜单栏图标
- 一键阻止休眠
- 轻量级

**GitHub**: https://github.com/newmarcel/KeepingYouAwake

#### 3. **NoSleep**（免费）

**功能**:
- 合盖不休眠
- 可选择是否使用电源

**下载**: https://www.macupdate.com/app/mac/35040/nosleep

### 优缺点

**优点**:
- ✅ 图形界面，易用
- ✅ 功能丰富，可定制
- ✅ 适合不熟悉命令行的用户

**缺点**:
- ⚠️ 需要安装第三方软件
- ⚠️ 部分工具需要付费
- ⚠️ 可能存在兼容性问题

---

## 🎯 推荐配置方案

### 场景1: 有外接显示器（最佳）

**使用方案1: 系统设置**

```bash
# 1. 启用盖合不休眠（电源模式）
sudo pmset -c disablesleep 1

# 2. 验证
pmset -g | grep disablesleep

# 3. 加载定时任务
cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout
./scripts/deploy_scheduler.sh
```

**特点**:
- ✅ 完全自动化
- ✅ 稳定可靠
- ✅ 官方支持

---

### 场景2: 无外接显示器（推荐）

**使用方案2: caffeinate 命令**

修改 `com.user.job-scout.daily.plist`:

```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>
        cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout &&
        caffeinate -d -t 900 ./scripts/run_job_scout.sh
    </string>
</array>
```

**特点**:
- ✅ 无需外接显示器
- ✅ 自动阻止休眠15分钟
- ✅ 任务完成后自动恢复
- ✅ 完全自动化

---

### 场景3: 需要完全自动化

**使用方案3: launchd 定时唤醒 + caffeinate**

```bash
# 1. 加载唤醒任务（17:55唤醒）
launchctl load ~/Library/LaunchAgents/com.user.job-scout.wake.plist

# 2. 修改主任务（移除定时，由唤醒任务触发）
# 编辑 com.user.job-scout.daily.plist

# 3. 测试
# 等待 17:55，观察是否自动唤醒并执行任务
```

**特点**:
- ✅ MacBook 大部分时间可以休眠
- ✅ 节省电量
- ✅ 完全自动化

---

## ⚠️ 重要注意事项

### 1. 散热问题 🔥

**问题**: 合盖时散热受限

**解决方案**:
- ✅ 使用散热支架
- ✅ 放在硬质表面（如桌子）
- ✅ 避免在床、沙发等柔软表面使用
- ✅ 定期清理灰尘，确保散热畅通

**监控温度**:
```bash
# 查看CPU温度（需要安装 osx-cpu-temp）
brew install osx-cpu-temp
osx-cpu-temp

# 或使用系统工具
sudo powermetrics --samplers cpu_power -i 1000
```

### 2. 电量消耗 🔋

**问题**: 合盖不休眠会消耗电量

**解决方案**:
- ✅ 保持连接电源适配器
- ✅ 使用 caffeinate 限制阻止时长
- ✅ 定期检查电量

**预估电量消耗**:
- 闲置时: ~5-10% / 小时
- 执行 Job Scout: ~2-3% (10-15分钟)

### 3. 数据安全 💾

**建议**:
- ✅ 定期备份重要数据
- ✅ 确保自动保存已启用
- ✅ 使用 Time Machine 备份

### 4. 系统更新 🔄

**注意事项**:
- ⚠️ macOS 更新可能重置电源设置
- ⚠️ 需要重新验证配置

**验证方法**:
```bash
# 每次系统更新后检查
pmset -g | grep disablesleep
launchctl list | grep job-scout
```

---

## 🚀 快速开始

### 一键部署（推荐配置）

```bash
# 场景: 无外接显示器，使用 caffeinate 自动阻止休眠

cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout

# 1. 备份原配置
cp com.user.job-scout.daily.plist com.user.job-scout.daily.plist.backup

# 2. 修改配置（集成 caffeinate）
cat > com.user.job-scout.daily.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.job-scout.daily</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>
            cd /Users/celeste/Documents/06\ Codiing/面试skill/skills/job-scout &&
            caffeinate -d -t 900 ./scripts/run_job_scout.sh
        </string>
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

# 3. 重新加载
launchctl unload ~/Library/LaunchAgents/com.user.job-scout.daily.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.user.job-scout.daily.plist

# 4. 测试
./scripts/run_job_scout.sh

# 5. 查看日志
tail -f logs/scheduler.log
```

---

## 📊 验证清单

运行以下命令验证配置是否正确：

```bash
# ✅ 1. 检查定时任务是否加载
launchctl list | grep job-scout

# ✅ 2. 检查脚本权限
ls -l scripts/run_job_scout.sh

# ✅ 3. 手动测试执行
./scripts/run_job_scout.sh

# ✅ 4. 检查日志
cat logs/scheduler.log

# ✅ 5. 验证 caffeinate 可用
which caffeinate

# ✅ 6. 测试合盖（可选）
# 合上盖子，等待几分钟后检查:
# - 是否生成了新的报告
# - 日志是否有新记录
```

---

## 📞 故障排查

### 问题1: 合盖后任务未执行

**检查**:
```bash
# 查看错误日志
cat logs/stderr.log

# 手动测试 caffeinate
caffeinate -d -t 10 echo "测试成功"

# 检查电源设置
pmset -g
```

### 问题2: MacBook 过热

**解决方案**:
- 提高 MacBook，改善散热
- 减少合盖使用时间
- 监控温度

### 问题3: 电量消耗过快

**解决方案**:
- 确保连接电源
- 使用定时唤醒方案（方案3）
- 减少阻止休眠时长

---

## 📚 参考资料

- [Apple Discussions - Prevent MacBook sleep in Clamshell](https://discussions.apple.com/thread/255899382)
- [Lifewire - Keep MacBook Awake With Lid Closed](https://www.lifewire.com/prevent-macbook-from-sleeping-when-the-lid-is-closed-5203069)
- [macOS pmset Man Page](https://ss64.com/osx/pmset.html)
- [caffeinate Man Page](https://ss64.com/osx/caffeinate.html)

---

**最后更新**: 2026-03-10
**适用版本**: macOS 14.x (Sonoma) 及更高版本
