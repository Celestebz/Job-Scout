# Job Scout - 智能岗位侦察兵

智能岗位发现系统，自动搜索、分析、推荐匹配的职位机会。

## 📁 文件结构

```
job-scout/
├── SKILL.md                    # 技能说明文档
├── README.md                   # 本文件
├── job_history.json            # 岗位历史数据库
│
├── scripts/                    # 脚本文件夹
│   ├── generate_report.py      # 生成XLSX报告
│   └── update_history.py       # 更新岗位数据库
│
├── result/                     # 报告输出文件夹（只放生成的报告）
│   └── job_scout_用户名_YYYYMMDD_HHMM.xlsx
│
└── users/                      # 用户配置文件夹
    └── {user_id}/
        ├── config.json         # 用户偏好配置
        ├── resume.docx         # 用户简历
        └── job_history.json    # 个人岗位历史（可选）
```

## 🚀 快速开始

### 1. 配置用户信息

编辑 `users/{user_id}/config.json` 设置：
- 期望薪资范围
- 目标城市
- 目标公司类型
- 搜索关键词

### 2. 运行岗位搜索

使用 Claude Code 执行：
```
/job-scout 帮我找工作
```

### 3. 生成报告

```bash
cd scripts
python3 generate_report.py
```

报告将保存在 `result/` 文件夹。

### 4. 更新数据库

```bash
cd scripts
python3 update_history.py
```

## 📝 脚本说明

### generate_report.py
- **用途**: 根据搜索结果生成Excel格式报告
- **输入**: 脚本中的 NEW_JOBS 列表
- **输出**: result/job_scout_用户名_时间戳.xlsx
- **特点**:
  - 14号大字体，方便阅读
  - 紫色表头，美观专业
  - 自动列宽和行高
  - 完整JD信息

### update_history.py
- **用途**: 将新岗位添加到历史数据库
- **输入**: 脚本中的 new_jobs 列表
- **输出**: 更新 job_history.json
- **特点**:
  - 自动去重
  - 更新统计信息
  - ISO时间戳

## 📊 数据格式

### job_history.json
```json
{
  "last_updated": "2026-03-03T22:20:00Z",
  "user_id": "wangbaozhen",
  "total_jobs": 26,
  "statistics": {
    "total_new_jobs": 12,
    "avg_match_score": 84.0,
    "filtered_vague_companies": 2
  },
  "jobs": [...]
}
```

### 岗位对象格式
```json
{
  "id": "company_title_salary_slug",
  "company": "公司名称",
  "title": "岗位名称",
  "salary": "薪资范围",
  "location": "工作地点",
  "first_seen": "首次发现日期",
  "match_score": 匹配度分数,
  "apply_url": "投递链接",
  "source": "数据来源"
}
```

## ⚙️ 配置说明

### 用户配置 (config.json)
```json
{
  "user_id": "用户ID",
  "name": "姓名",
  "search_preferences": {
    "location": "目标城市",
    "target_companies": ["目标公司列表"],
    "company_types": ["公司类型"],
    "industries": ["行业列表"],
    "job_types": ["岗位类型"]
  },
  "salary_expectation": {
    "min": 最低薪资,
    "target": 目标薪资,
    "max": 最高薪资
  }
}
```

## 🔄 工作流程

```
1. 用户触发搜索
   ↓
2. 执行多轮 WebSearch
   ↓
3. 提取岗位信息
   ↓
4. 计算匹配度
   ↓
5. 更新 job_history.json (去重)
   ↓
6. 生成 XLSX 报告
   ↓
7. 输出到 result/ 文件夹
```

## 📌 注意事项

1. **文件管理规范**:
   - 脚本文件放在 `scripts/` 文件夹
   - 报告文件放在 `result/` 文件夹
   - 不要混放不同类型的文件

2. **数据安全**:
   - job_history.json 记录所有历史岗位
   - 生成报告前会自动去重
   - 每次运行都会更新时间戳

3. **薪资建议**:
   - 应届生/转行者：8-12K
   - 1-3年经验：10-18K
   - 3-5年经验：15-30K
   - 5年以上：25K+

## 📮 反馈与支持

如有问题，请联系或提交 Issue。
