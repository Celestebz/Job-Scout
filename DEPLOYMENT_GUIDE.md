# 🚀 Job Scout GitHub Actions 部署完整指南

## 📋 目录

1. [技术可行性分析](#技术可行性分析)
2. [API调用分析](#api调用分析)
3. [GitHub Secrets配置](#github-secrets配置)
4. [完整部署流程](#完整部署流程)
5. [测试和验证](#测试和验证)
6. [故障排查](#故障排查)

---

## 技术可行性分析

### ✅ 可行性评估：**完全可行**

经过深入分析，Job Scout技能迁移到GitHub Actions **技术上完全可行**，原因如下：

#### 1. 核心依赖分析

Job Scout技能的依赖情况：

| 依赖类型 | 具体依赖 | GitHub Actions支持 | 说明 |
|---------|---------|-------------------|------|
| **Claude Code CLI** | `claude` 命令 | ✅ 完全支持 | 通过安装脚本安装 |
| **Python库** | openpyxl, pandas | ✅ 完全支持 | pip安装 |
| **文件系统** | JSON读写、XLSX生成 | ✅ 完全支持 | GitHub Actions提供完整文件系统 |
| **网络请求** | WebSearch (通过Claude) | ✅ 完全支持 | Claude Code内部处理 |
| **斜杠命令** | /job-scout | ✅ 完全支持 | Claude Code CLI原生支持 |

**结论**：所有依赖都可以在GitHub Actions中满足。

#### 2. Claude Agent SDK vs Claude Code CLI

**重要发现**：

根据深入调研，**Claude Agent SDK对斜杠命令（slash commands）的支持仍在开发中**，因此：

- ❌ **不推荐**：使用Claude Agent SDK直接调用/job-scout技能
- ✅ **推荐**：使用Claude Code CLI调用/job-scout技能

**原因**：
1. Claude Code CLI已经完全支持斜杠命令
2. 在GitHub Actions中安装和运行Claude Code CLI是经过验证的方案
3. Claude Agent SDK主要用于构建自定义Agent，而非调用已有技能

**我们的实现**：
```python
# ✅ 推荐方案：在Python脚本中调用Claude Code CLI
subprocess.run([
    "claude",
    "/job-scout",
    "帮我找工作"
], cwd=project_root)
```

---

## API调用分析

### Job Scout技能的所有API调用

经过全面分析，Job Scout技能**不需要任何外部API密钥**，所有API调用都通过Claude Code CLI内部处理：

#### 1. WebSearch API（通过Claude）

```python
# SKILL.md中的描述
# Step 3: Multi-Source Search Execution (Priority-Based)
# EXECUTE all Priority 1 searches first using WebSearch.
```

**实现方式**：
- ✅ Claude Code CLI内部处理WebSearch
- ✅ 无需配置Google Search API或其他搜索引擎API
- ✅ 无需API密钥

#### 2. 网页抓取（WebReader）

```python
# SKILL.md中的描述
# Use WebReader to fetch complete JD if URL available
```

**实现方式**：
- ✅ Claude Code CLI内部处理网页抓取
- ✅ 无需额外的爬虫框架
- ✅ 无需代理配置

#### 3. 文件操作

| 操作类型 | 文件路径 | GitHub Actions支持 |
|---------|---------|-------------------|
| 读取配置 | `users/wangbaozhen/config.json` | ✅ |
| 读取简历 | `简历/王宝珍中文简历260216.docx` | ✅ |
| 读写数据库 | `job_history.json` | ✅ |
| 生成报告 | `result/*.xlsx` | ✅ |
| 写入日志 | `logs/*.log` | ✅ |

#### 4. Python库依赖

| 库名 | 用途 | 是否需要API密钥 |
|-----|------|---------------|
| `openpyxl` | 生成XLSX报告 | ❌ 不需要 |
| `pandas` | 数据处理 | ❌ 不需要 |
| `timeout-decorator` | 超时控制 | ❌ 不需要 |

---

## GitHub Secrets配置

### 🎯 重要结论：**不需要配置任何GitHub Secrets！**

经过完整分析，Job Scout技能**零依赖外部API密钥**，所有功能都通过Claude Code CLI内部实现。

### 为什么不需要API密钥？

1. **WebSearch通过Claude**：Claude Code CLI内置WebSearch功能
2. **无需搜索引擎API**：不使用Google Search API、Bing Search API等
3. **无需爬虫框架**：网页抓取由Claude内部处理
4. **文件操作本地化**：所有文件都在GitHub Actions Runner本地处理

### GitHub Secrets配置清单

| Secret名称 | 是否必需 | 说明 |
|-----------|---------|------|
| **GITHUB_TOKEN** | ✅ 自动提供 | GitHub自动提供，用于提交结果到仓库 |
| **ANTHROPIC_API_KEY** | ❌ 不需要 | Claude Code CLI会使用自身配置 |
| **其他API密钥** | ❌ 不需要 | 无需任何第三方API |

**唯一需要的就是GITHUB_TOKEN**（GitHub自动提供，无需手动配置）。

---

## 完整部署流程

### 📅 预计时间：30分钟

### Step 1: 准备本地代码（5分钟）

#### 1.1 检查文件完整性

确认以下文件存在：

```bash
cd "/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout"

# 检查关键文件
ls -la .github/workflows/daily-job-scout-sdk.yml
ls -la scripts/github_actions_job_scout.py
ls -la SKILL.md
ls -la job_history.json
ls -la users/wangbaozhen/config.json
```

#### 1.2 确保Git已初始化

```bash
# 如果还没有Git仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: Add job-scout with GitHub Actions"
```

### Step 2: 创建GitHub仓库（3分钟）

#### 2.1 在GitHub上创建新仓库

1. 打开 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `job-scout` (或你喜欢的名字)
   - **Description**: `自动化岗位搜索系统 - 每日定时运行`
   - **Visibility**: Private（私有）或 Public（公开）
   - **不要**勾选 "Add a README file"
   - **不要**勾选 "Add .gitignore"
3. 点击 "Create repository"

#### 2.2 关联本地仓库到GitHub

```bash
# 添加远程仓库（替换YOUR_USERNAME和REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

**示例**：
```bash
git remote add origin https://github.com/wangbaozhen/job-scout.git
git push -u origin main
```

### Step 3: 验证GitHub Actions配置（2分钟）

#### 3.1 检查Workflow文件

```bash
# 确认workflow文件在正确位置
ls -la .github/workflows/daily-job-scout-sdk.yml

# 查看workflow内容（可选）
cat .github/workflows/daily-job-scout-sdk.yml
```

#### 3.2 推送配置到GitHub

```bash
# 如果有新的修改
git add .github/workflows/daily-job-scout-sdk.yml
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### Step 4: 启用GitHub Actions（2分钟）

#### 4.1 确认Actions已启用

1. 打开你的GitHub仓库
2. 点击 "Actions" 标签
3. 如果看到 "GitHub Actions is currently disabled"：
   - 点击 "I understand my workflows, go ahead and enable them"
   - 确认启用

#### 4.2 检查Workflow是否显示

在Actions页面，应该能看到：
- **Workflow名称**: "Daily Job Scout (Claude Code CLI)"
- **状态**: 等待运行或准备就绪

### Step 5: 配置定时任务（1分钟）

#### 5.1 验证定时配置

Workflow文件已包含定时配置：
```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

**说明**：
- UTC时间 01:00 = 北京时间 09:00
- 每天早上9点自动运行

#### 5.2 （可选）修改运行时间

如果需要修改运行时间，编辑 `.github/workflows/daily-job-scout-sdk.yml`：

```yaml
schedule:
  # 例如改为北京时间早上8点（UTC 00:00）
  - cron: '0 0 * * *'
```

### Step 6: 手动测试运行（5分钟）

#### 6.1 触发手动运行

1. 打开GitHub仓库 → Actions标签
2. 选择 "Daily Job Scout (Claude Code CLI)" workflow
3. 点击 "Run workflow" 按钮
4. 选择分支：`main`
5. ✅ 勾选 "Test mode (快速验证)" - 可选
6. 点击 "Run workflow" 按钮

#### 6.2 监控运行过程

1. 点击正在运行的任务
2. 实时查看执行日志
3. 预计运行时间：10-30分钟（取决于搜索数量）

### Step 7: 验证运行结果（5分钟）

#### 7.1 查看执行摘要

在Actions运行页面：
- 滚动到 "Summary" 部分
- 查看执行摘要和关键指标

#### 7.2 查看生成的文件

**方式1：GitHub网页查看**
```
你的GitHub仓库
├── result/
│   └── job_scout_王宝珍_YYYYMMDD.xlsx  ← 点击查看
├── job_history.json                    ← 点击查看
└── logs/
    └── last-run-summary.txt            ← 点击查看
```

**方式2：拉取到本地查看**
```bash
# 拉取最新结果
git pull origin main

# 查看最新报告
open result/job_scout_王宝珍_$(date +%Y%m%d)*.xlsx

# 查看执行摘要
cat logs/last-run-summary.txt

# 查看数据库统计
cat job_history.json | jq '.total_jobs'
```

#### 7.3 下载完整日志（调试用）

1. 进入Actions运行页面
2. 滚动到底部的 "Artifacts" 区域
3. 下载 `job-scout-logs-[编号].zip`
4. 解压查看完整日志

### Step 8: 设置通知（可选，7分钟）

#### 8.1 GitHub默认通知

GitHub会自动发送：
- ✅ Actions运行失败通知
- ✅ Actions运行成功通知（可配置）

**配置方式**：
1. 点击GitHub右上角头像 → Settings
2. Notifications → Actions
3. 勾选你想要的通知类型

#### 8.2 企业微信/钉钉通知（高级）

如果需要企业微信或钉钉通知，需要修改workflow文件：

```yaml
# 添加企业微信通知步骤
- name: Send WeChat notification
  if: failure()
  run: |
    curl -X POST "${{ secrets.WECHAT_WEBHOOK_URL }}" \
      -H 'Content-Type: application/json' \
      -d '{
        "msgtype": "text",
        "text": {
          "content": "Job Scout执行失败，请检查：${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        }
      }'
```

然后在GitHub Secrets中配置：
- `WECHAT_WEBHOOK_URL`: 企业微信机器人Webhook URL
- `DINGTALK_WEBHOOK_URL`: 钉钉机器人Webhook URL

---

## 测试和验证

### ✅ 验证清单

#### 1. 基础功能验证

- [ ] Workflow文件正确推送
- [ ] Actions页面显示workflow
- [ ] 手动触发成功运行
- [ ] 生成了XLSX报告
- [ ] job_history.json已更新

#### 2. 定时任务验证

- [ ] 第二天早上9点自动运行
- [ ] 查看Actions历史有运行记录
- [ ] 生成了新的XLSX报告

#### 3. 数据质量验证

打开XLSX报告，检查：
- [ ] 至少10个新岗位
- [ ] 优先级分布合理（外企40%、大厂40%、其他20%）
- [ ] JD真实完整
- [ ] 公司名称清晰

---

## 故障排查

### 常见问题和解决方案

#### 问题1：Workflow没有触发

**症状**：到了早上9点，但没有运行记录

**排查步骤**：
1. 检查Actions是否启用
2. 检查workflow文件语法是否正确
3. 检查cron表达式是否正确

**解决方案**：
```bash
# 手动触发测试
git push origin main  # 推送后会自动触发（如果配置了push事件）
```

#### 问题2：Claude Code CLI安装失败

**症状**：日志显示 "Claude Code CLI installation failed"

**排查步骤**：
1. 检查网络连接
2. 查看安装脚本的错误信息

**解决方案**：
```yaml
# 在workflow中添加重试
- name: Setup Claude Code CLI
  run: |
    curl -fsSL https://claude.ai/install.sh | sh || {
      echo "Retrying installation..."
      curl -fsSL https://claude.ai/install.sh | sh
    }
```

#### 问题3：Job Scout执行超时

**症状**：运行超过45分钟，被自动终止

**排查步骤**：
1. 查看日志中的搜索次数
2. 检查WebSearch是否卡住

**解决方案**：
```yaml
# 增加超时时间
timeout-minutes: 90  # 从60分钟改为90分钟
```

#### 问题4：XLSX文件未生成

**症状**：运行完成但result目录为空

**排查步骤**：
1. 检查Python依赖是否安装成功
2. 查看Job Scout执行日志

**解决方案**：
```yaml
# 确保Python依赖正确安装
- name: Install Python dependencies
  run: |
    pip install openpyxl pandas timeout-decorator
    python -c "import openpyxl, pandas; print('Dependencies OK')"
```

#### 问题5：Git提交失败

**症状**：显示 "failed to push some refs"

**排查步骤**：
1. 检查GitHub token权限
2. 检查分支保护规则

**解决方案**：
```yaml
# 确保有足够的权限
permissions:
  contents: write  # 必须要有write权限
```

---

## 🎯 总结

### 关键要点

1. ✅ **完全可行**：Job Scout可以完全迁移到GitHub Actions
2. ✅ **零API密钥**：不需要配置任何外部API密钥
3. ✅ **自动化运行**：每天早上9点自动执行
4. ✅ **数据持久化**：结果自动提交到Git仓库
5. ✅ **完全免费**：远低于GitHub免费限额

### 下一步行动

1. **立即开始**：按照上述步骤开始部署
2. **首次测试**：手动触发一次测试运行
3. **等待验证**：第二天早上9点自动运行
4. **查看结果**：打开GitHub仓库查看最新报告

### 需要帮助？

如果遇到问题：
1. 查看Actions运行日志
2. 参考本文档的"故障排查"部分
3. 下载Artifacts中的完整日志分析

---

**祝你部署成功！🎉**
