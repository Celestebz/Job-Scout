# GitHub Actions定时运行方案 - 数据存储详解

## 📁 数据存储位置总览

### 1. GitHub仓库（永久存储）⭐

**位置**：你的GitHub仓库根目录

**存储内容**：
```
你的GitHub仓库
├── job_history.json              ✅ 自动提交（去重数据库）
├── result/                       ✅ 自动提交（最近30天的报告）
│   ├── job_scout_王宝珍_20260309.xlsx
│   ├── job_scout_王宝珍_20260310.xlsx
│   └── job_scout_王宝珍_20260311.xlsx
├── logs/                         ✅ 自动提交（执行摘要）
│   └── last-run-summary.txt
└── backup/                       ✅ 自动提交（数据库备份）
    └── job_history_20260309.json
```

**访问方式**：
1. **浏览器访问**：直接在GitHub网站查看文件
2. **Git克隆**：`git clone https://github.com/你的用户名/你的仓库.git`
3. **GitHub网页界面**：点击文件即可预览XLSX

**保留时间**：✅ **永久保留**（除非手动删除）

---

### 2. GitHub Artifacts（临时存储）

**位置**：GitHub Actions运行页面

**存储内容**：
```
每次Actions运行的Artifacts页面
└── job-scout-logs-[运行编号].zip
    ├── logs/daily-run-20260309_090001.log    (完整日志)
    ├── logs/last-run-summary.txt              (执行摘要)
    └── result/job_scout_王宝珍_20260309.xlsx  (XLSX报告)
```

**访问方式**：
1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 选择一次运行记录
4. 滚动到页面底部的 "Artifacts" 区域
5. 点击下载 ZIP 文件

**保留时间**：⏰ **30天**（自动清理）

---

## 🔄 数据流转过程

### 完整的数据流

```
GitHub Actions Runner (临时环境)
│
├─ Step 1: 检出代码
│  └─ 从GitHub克隆仓库到Runner
│
├─ Step 2: 执行Job Scout
│  ├─ 读取 job_history.json (用于去重)
│  ├─ 执行WebSearch搜索
│  ├─ 生成 result/job_scout_YYYYMMDD.xlsx
│  └─ 更新 job_history.json
│
├─ Step 3: 提交结果
│  ├─ git add job_history.json
│  ├─ git add result/*.xlsx
│  ├─ git commit -m "..."
│  └─ git push (推送到GitHub仓库)
│
└─ Step 4: 上传Artifacts
   └─ 上传完整日志和报告 (保留30天)
        │
        ▼
GitHub仓库 (永久存储)
├─ job_history.json ✅ 更新
├─ result/*.xlsx ✅ 新增
└─ GitHub永久保存
```

---

## 💾 数据存储策略

### 策略对比

| 存储位置 | 存储内容 | 保留时间 | 访问方式 | 推荐用途 |
|---------|---------|---------|---------|---------|
| **Git仓库** | job_history.json | 永久 | Git克隆/网页查看 | ⭐⭐⭐⭐⭐ 去重数据库 |
| **Git仓库** | result/*.xlsx | 30天+ | Git克隆/网页查看 | ⭐⭐⭐⭐⭐ 最新报告 |
| **Git仓库** | backup/*.json | 30天 | Git克隆/网页查看 | ⭐⭐⭐⭐ 数据备份 |
| **Artifacts** | 完整日志+报告 | 30天 | Actions页面下载 | ⭐⭐⭐ 调试用 |

### 推荐配置：混合存储

**核心原则**：
- ✅ **job_history.json** → 必须提交到Git（用于去重）
- ✅ **最新XLSX报告** → 提交到Git（方便查看）
- ✅ **完整日志** → 上传到Artifacts（保留30天）

**理由**：
1. **job_history.json**是核心数据库，必须永久保存
2. **XLSX报告**需要方便访问，放在Git仓库最方便
3. **日志文件**很大，放在Artifacts节省仓库空间

---

## 📊 实际使用场景

### 场景1：查看最新报告

**方法A：浏览器访问（推荐）**
```
1. 打开 https://github.com/你的用户名/你的仓库
2. 进入 result/ 目录
3. 点击最新的 job_scout_王宝珍_YYYYMMDD.xlsx
4. 直接在浏览器预览或下载
```

**方法B：Git克隆**
```bash
# 克隆仓库
git clone https://github.com/你的用户名/你的仓库.git
cd 你的仓库

# 查看最新报告
open result/job_scout_王宝珍_$(date +%Y%m%d).xlsx
```

### 场景2：查看历史数据

**查看岗位历史统计**：
```bash
# 克隆仓库后
git clone https://github.com/你的用户名/你的仓库.git
cd 你的仓库

# 查看数据库统计
cat job_history.json | jq '.total_jobs'
cat job_history.json | jq '.last_updated'

# 查看某个日期的报告
ls -la result/ | grep "20260309"
```

### 场景3：调试执行问题

**下载完整日志**：
```
1. 打开 GitHub仓库 → Actions标签
2. 选择失败的那次运行
3. 滚动到底部 "Artifacts"
4. 下载 job-scout-logs-[编号].zip
5. 解压查看完整日志
```

---

## ⚙️ 配置选项

### 选项1：只提交关键数据（推荐）

**适合**：想要保持仓库整洁

```yaml
# .github/workflows/daily-job-scout.yml
- name: Commit results
  run: |
    # 只提交job_history.json和最新报告
    git add job_history.json
    git add result/job_scout_王宝珍_$(date +%Y%m%d).xlsx

    # 清理30天前的旧报告
    find result/ -name "*.xlsx" -mtime +30 -delete

    git commit -m "🤖 Automated run [skip ci]"
    git push
```

**结果**：
```
你的GitHub仓库
├── job_history.json (1个文件，持续更新)
├── result/
│   ├── job_scout_王宝珍_20260309.xlsx (最近30天)
│   ├── job_scout_王宝珍_20260310.xlsx
│   └── ... (最多30个文件)
└── backup/
    └── job_history_20260309.json (最近30天)
```

### 选项2：保留所有历史

**适合**：想要完整的历史记录

```yaml
# .github/workflows/daily-job-scout.yml
- name: Commit results
  run: |
    # 提交所有文件，不清理
    git add job_history.json result/ backup/

    git commit -m "🤖 Automated run [skip ci]"
    git push
```

**结果**：
```
你的GitHub仓库
├── job_history.json (持续增长)
├── result/
│   ├── job_scout_王宝珍_20260309.xlsx
│   ├── job_scout_王宝珍_20260310.xlsx
│   └── ... (所有历史报告)
└── backup/
    └── job_history_*.json (所有备份)
```

---

## 🔐 隐私和安全性

### 敏感数据处理

**当前job-scout的数据都是公开的**：
- ✅ job_history.json - 只包含公开的岗位信息
- ✅ XLSX报告 - 只包含岗位数据
- ✅ 日志文件 - 执行日志，无敏感信息

**如果将来包含敏感数据**，需要：

1. **使用Git Crypt加密敏感文件**
```bash
# 安装git-crypt
brew install git-crypt

# 加密敏感文件
git-crypt init
echo "*.secret filter=git-crypt diff=git-crypt" > .gitattributes
```

2. **使用GitHub Secrets存储密钥**
```yaml
env:
  MY_API_KEY: ${{ secrets.MY_API_KEY }}
```

---

## 📈 存储成本分析

### GitHub免费额度

| 资源 | 免费额度 | job-scout使用量 | 占比 |
|-----|---------|----------------|------|
| **仓库存储** | 1GB | ~10MB/月 | 1% |
| **带宽** | 100GB/月 | ~5MB/天 | 1.5% |
| **Artifacts** | 500GB/月 | ~10MB/天 | 0.6% |
| **构建时间** | 2000分钟/月 | ~10分钟/天 | 1.5% |

**结论**：✅ **完全免费，远低于限额**

### 文件大小估算

```
job_history.json:  ~100KB (包含100个岗位)
每个XLSX报告:       ~50KB
每天日志文件:       ~200KB
30天总计:          ~10MB
```

**结论**：✅ **存储空间占用极小，可以忽略不计**

---

## 🚀 快速开始

### Step 1: 创建GitHub仓库

```bash
# 如果还没有GitHub仓库
cd "/Users/celeste/Documents/06 Codiing/面试skill/skills/job-scout"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: Add job-scout skill"

# 创建GitHub仓库后，关联远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### Step 2: 启用GitHub Actions

```bash
# 推送到GitHub后，Actions会自动启用
git push origin main
```

### Step 3: 验证运行

1. 打开GitHub仓库
2. 点击 "Actions" 标签
3. 应该能看到 "Daily Job Scout" 工作流
4. 点击 "Run workflow" 手动测试一次

### Step 4: 查看结果

```bash
# 拉取最新结果
git pull origin main

# 查看生成的文件
ls -la result/
cat job_history.json | jq '.total_jobs'
```

---

## 🎯 总结

### 数据存储位置总结

| 存储位置 | 内容 | 访问方式 | 保留时间 |
|---------|------|---------|---------|
| **GitHub仓库** | job_history.json, XLSX报告 | Git克隆/网页查看 | 永久 |
| **Artifacts** | 完整日志 | Actions页面下载 | 30天 |

### 关键要点

1. ✅ **所有重要数据都保存在GitHub仓库中** - 永久存储
2. ✅ **可以直接在网页上查看XLSX报告** - 无需下载
3. ✅ **job_history.json会自动更新** - 用于去重
4. ✅ **完整日志保存在Artifacts** - 保留30天
5. ✅ **完全免费** - 远低于GitHub限额

### 推荐工作流

```
每天早上9点自动运行
   ↓
GitHub Actions执行
   ↓
生成报告并提交到Git仓库
   ↓
你收到通知（可选）
   ↓
打开GitHub网页查看最新XLSX报告
   ↓
决定投递哪些岗位
```

---

## 📞 需要帮助？

如果遇到问题，检查：
1. GitHub仓库是否正确配置
2. Actions权限是否开启（Settings → Actions → General）
3. Workflow文件是否在 `.github/workflows/` 目录下
4. 查看Actions运行日志了解详细错误
