# Job Scout 去重机制说明

## 🔄 去重机制实现

### 核心原理

```
┌─────────────────────────────────────────────────────────────┐
│                     去重流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. 搜索发现岗位                                              │
│     └── WebSearch 发现 15 个岗位                             │
│                                                               │
│  2. 生成唯一ID                                                │
│     └── job_id = f"{company}_{title}_{salary}"               │
│         例: "bytedance_CapCut海外运营_15-25K"                 │
│                                                               │
│  3. 对比数据库                                                │
│     └── 读取 users/{user_id}/job_history.json                │
│     └── 检查 job_id 是否已存在                               │
│                                                               │
│  4. 标记状态                                                  │
│     ├── NEW → 今日新发现                                     │
│     └── EXISTING → 往期已推荐                                │
│                                                               │
│  5. 更新数据库                                                │
│     └── 将 NEW 岗位添加到 job_history.json                   │
│     └── 通过 Git 提交到 GitHub 仓库                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 唯一ID生成规则

### 格式

```
job_id = "{company_slug}_{title_slug}_{salary_slug}"
```

### 示例

| 岗位 | company_slug | title_slug | salary_slug | 最终 job_id |
|------|-------------|------------|-------------|-------------|
| 字节跳动-CapCut海外运营-15-25K | bytedance | capcut海外运营 | 15-25k | `bytedance_capcut海外运营_15-25k` |
| 腾讯云-AIGC产品运营-25-40K | tencentcloud | aigc产品运营 | 25-40k | `tencentcloud_aigc产品运营_25-40k` |
| SHEIN-商家运营-20-50K | shein | 商家运营 | 20-50k | `shein_商家运营_20-50k` |

### 去重判定

```python
# 完全匹配 → 同一个岗位
company_same AND title_same AND salary_same → DUPLICATE

# 薪资略有差异（<20%）→ 可能是同一岗位
company_same AND title_same AND salary_similar → LIKELY_DUPLICATE

# 完全不同的组合 → 新岗位
ELSE → NEW_JOB
```

---

## 💾 数据库结构

### job_history.json

```json
{
  "last_updated": "2026-03-03T21:00:00Z",
  "user_id": "wangbaozhen",
  "total_jobs": 13,
  "statistics": {
    "total_new_jobs": 13,
    "total_recommended": 8,
    "avg_match_score": 82
  },
  "jobs": [
    {
      "id": "bytedance_capcut海外运营_15-25k",
      "company": "字节跳动",
      "title": "CapCut海外区域运营",
      "salary": "15-25K·15薪",
      "location": "深圳南山区",
      "first_seen": "2026-03-02",
      "last_seen": "2026-03-03",
      "match_score": 95,
      "times_seen": 2,
      "status": "active",
      "apply_url": "https://jobs.bytedance.com/experienced",
      "source": "猎聘"
    }
  ]
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识符 |
| `first_seen` | 首次发现日期 |
| `last_seen` | 最后发现日期 |
| `times_seen` | 被发现的次数 |
| `status` | active（仍在招聘）/ expired（已过期） |

---

## 🌐 GitHub 部署后的去重

### 问题与解决方案

| 问题 | 解决方案 |
|------|---------|
| GitHub Actions 每次是新环境 | 将 job_history.json 提交回仓库 |
| 多人共用一个仓库 | 每个用户独立的数据库文件 |
| 并发运行冲突 | Git 自动合并，每个用户只修改自己的文件 |

### 文件结构

```
your-repo/
├── .github/
│   └── workflows/
│       └── daily-job-scout.yml
├── users/
│   ├── wangbaozhen/
│   │   ├── resume.docx
│   │   ├── config.json
│   │   └── job_history.json      ← 王宝珍的去重数据
│   ├── lisi/
│   │   ├── resume.docx
│   │   ├── config.json
│   │   └── job_history.json      ← 李四的去重数据
│   └── zhangsan/
│       ├── resume.docx
│       ├── config.json
│       └── job_history.json      ← 张三的去重数据
└── reports/
    ├── wangbaozhen_20260302.html
    ├── wangbaozhen_20260303.html
    ├── lisi_20260302.html
    └── index.html
```

### Git 提交流程

```yaml
# 每次 GitHub Actions 运行后
1. 执行搜索
2. 更新 users/{user_id}/job_history.json
3. 生成 HTML 报告
4. Git add + commit + push
   → 只提交该用户的数据库文件
   → 其他用户的文件不受影响
```

---

## 🔒 隐私与安全

### 敏感信息处理

`job_history.json` 包含的数据：
- ✅ 公司名（公开信息）
- ✅ 岗位名称（公开信息）
- ✅ 薪资范围（公开信息）
- ✅ 匹配度分数（生成数据）
- ✅ 搜索来源（公开平台）

**不包含**：
- ❌ 个人身份信息
- ❌ 联系方式
- ❌ 简历详细内容

### 安全建议

1. **私有仓库**: 建议将仓库设为 Private
2. **加密配置**: 如有敏感偏好，可加密 config.json
3. **访问控制**: GitHub Actions token 权限最小化

---

## 📊 去重效果示例

### 第1天运行

```
搜索发现: 10 个岗位
去重检查: 全部 NEW
输出: 10 个 NEW 标签
数据库: 10 条记录
```

### 第2天运行

```
搜索发现: 8 个岗位
去重检查:
  - 3 个 NEW
  - 5 个 EXISTING（昨天已推荐）
补充数据库: 2 个高匹配旧岗位
输出: 3 个 NEW + 2 个 EXISTING = 5 个岗位
数据库: 12 条记录（10旧 + 2新）
```

### 第3天运行（假设无新岗位）

```
搜索发现: 5 个岗位
去重检查: 全部 EXISTING
补充数据库: 0 个（已有5个）
输出: 5 个 EXISTING 标签
数据库: 12 条记录（无变化）
```

---

## ⚙️ 配置选项

### config.json 参数

```json
{
  "deduplication": {
    "enabled": true,                    // 是否启用去重
    "method": "exact",                  // exact / fuzzy
    "salary_tolerance": 0.2,            // 薪资容差 20%
    "expire_days": 30,                  // 岗位过期天数
    "max_database_size": 1000           // 最大数据库条目
  }
}
```

### 去重策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `exact` | 精确匹配（公司+职位+薪资） | 严格去重，避免重复 |
| `fuzzy` | 模糊匹配（容许薪资浮动） | 薪资范围可能变化的岗位 |

---

## 🛠️ 故障排查

### 问题：数据库丢失

**原因**: GitHub Actions 未正确提交文件

**解决**:
```yaml
- name: Debug database file
  run: |
    ls -la users/wangbaozhen/
    cat users/wangbaozhen/job_history.json

- name: Force commit
  run: |
    git add -f users/wangbaozhen/job_history.json
    git commit -m "Force update database" || echo "No changes"
```

### 问题：去重不生效

**原因**: job_id 生成规则不一致

**检查**:
```bash
# 查看数据库中的 ID 格式
cat users/wangbaozhen/job_history.json | jq '.jobs[].id'

# 确保每次运行使用相同的 slug 函数
```

---

## 📚 总结

| 特性 | 本地运行 | GitHub 部署 |
|------|---------|-------------|
| 去重机制 | ✅ 有效 | ✅ 有效（需正确配置） |
| 多用户隔离 | 不适用 | ✅ 按用户隔离 |
| 数据持久化 | 本地文件 | Git 仓库 |
| 并发安全 | 不适用 | ✅ 每用户独立文件 |
| 数据隐私 | ✅ 完全本地 | ⚠️ 需设为私有仓库 |
