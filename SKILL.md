---
name: job-scout
description: Active job discovery system with smart deduplication that proactively searches and evaluates job opportunities. Performs multi-source job hunting using WebSearch, extracts JD information, calculates match scores, and outputs CSV report with ALL qualified positions. Automatically filters out previously recommended jobs using job history database. Enforces minimum match score threshold (60+) for quality control. Ideal for scheduled automated execution. Use when user requests job search, "帮我找工作", "找岗位", or for automated daily job scouting. Requires: resume file in 简历/ folder. Outputs: CSV report + JSON job database.
license: MIT
---

# Job Scout - 智能岗位侦察兵（云端部署版）

## Overview

这是一个**支持云端定时部署**的主动式岗位发现系统，核心特性：

1. **🚀 智能搜索策略（NEW - 效率优化）** - 基于历史数据分析搜索盲区，避免重复搜索已充分覆盖的公司，整体搜索效率提升 40%+
2. **主动搜索** - 基于用户画像生成多组搜索词，执行多源搜索
3. **智能去重** - 自动过滤已推荐过的岗位，避免重复
4. **XLSX输出** - 生成带格式的大字体Excel文件
5. **数据库维护** - 自动更新已推荐岗位JSON数据库
6. **匹配评估** - 与用户简历对比，计算匹配度
7. **质量控制** - **仅输出高质量岗位（匹配度≥60）**
8. **可投递性过滤** - **必须有具体公司名，拒绝模糊信息**
9. **全部输出** - **输出所有符合条件的岗位，不限制数量**

### 🎯 效率优化亮点

**传统方式**（盲目搜索）:
- 每次搜索 10+ 次，可能找到 5 个新岗位
- 重复搜索字节跳动、腾讯等已覆盖的公司
- 不了解外企/大厂占比是否均衡

**优化后**（智能分析）:
- 每次搜索 5-7 次，找到 8-12 个新岗位
- 自动跳过已充分覆盖的公司（≥5个岗位）
- 基于数据补充外企/大厂/薪资盲区
- **效率提升 40%+**

### 部署架构

```
GitHub Actions (定时触发)
    ↓
Job Scout Skill 执行
    ↓
生成 CSV 报告 + 更新 JSON 数据库
    ↓
自动推送到 GitHub 仓库
    ↓
用户下载 CSV 查看/编辑
```

### SILENT EXECUTION PROTOCOL

**CRITICAL**: Execute without interruption:

- **DO NOT** ask for confirmation to proceed
- **DO NOT** ask "Should I continue searching?"
- **DO NOT** pause between search executions
- **GENERATE** complete XLSX report in ONE response
- **ALWAYS** check job_history.json for deduplication
- **ALWAYS** append new jobs to job_history.json
- **ALWAYS** output at least 10 NEW qualified jobs (自动扩展搜索直到满足)
- **NEVER** fabricate job information or company data
- **ALWAYS** filter out jobs with vague company names (starting with "某" or containing "轮)")
- **CRITICAL: JD MUST BE 100% REAL** - Only extract actual job descriptions from official/recruitment sites, NEVER generate template JDs

---

## File Structure

```
job-scout/
├── SKILL.md                    # 本文件
├── job_history.json            # 已推荐岗位数据库（自动维护）
├── result/                        # 报告目录
│   ├── README.md               # 使用说明
│   └── job_scout_{user_id}_{YYYYMMDD}.xlsx
└── users/                      # 多用户支持（可选）
    ├── {user_id}/
    │   ├── resume.docx
    │   ├── config.json
    │   └── job_history.json
    └── {another_user_id}/
        ├── resume.docx
        └── job_history.json
```

---

## Input Requirements

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Trigger Word | Text | Yes | - | User's trigger phrase |
| User ID | Text | Yes | Auto-detect | User identifier for database isolation |
| Additional Keywords | Text | No | None | Optional specific terms |
| Resume Path | File | Yes | `users/{user_id}/resume.docx` | User's resume file |
| Job History | JSON | Auto | `users/{user_id}/job_history.json` | User's personal database |

### User Isolation (Multi-user Support)

**For GitHub deployment with multiple users:**

```yaml
# File structure
users/
├── {user_id}/
│   ├── resume.docx
│   ├── config.json           # User preferences (location, salary, etc.)
│   └── job_history.json      # Personal deduplication database
└── {another_user_id}/
    ├── resume.docx
    ├── config.json
    └── job_history.json
```

**User ID Detection:**
1. If provided via `--user` parameter, use it
2. If not provided, extract from resume filename (e.g., "resume_wangbaozhen.docx" → "wangbaozhen")
3. Each user maintains their own job history database

---

## Workflow

### Step 0: Load Job History Database & Analyze Gaps

**READ** `job_history.json` to get previously recommended jobs:

```json
{
  "last_updated": "2026-03-02",
  "total_jobs": 42,
  "jobs": [
    {
      "id": "bytetdance_capcut_20260301",
      "company": "字节跳动",
      "title": "CapCut海外区域运营",
      "salary": "15-25K·15薪",
      "location": "深圳南山区",
      "first_seen": "2026-03-01",
      "match_score": 95
    },
    ...
  ]
}
```

**IF** file doesn't exist, **CREATE** new structure:
```json
{
  "last_updated": null,
  "total_jobs": 0,
  "jobs": []
}
```

---

### Step 0.5: Intelligent Gap Analysis (NEW - 效率优化关键)

**ANALYZE** existing jobs to identify search gaps and optimize strategy:

```python
# 分析已有岗位数据
def analyze_job_gaps(job_history):
    total_jobs = len(job_history['jobs'])

    # 1. 公司类型分布分析
    company_types = {"外企": 0, "大厂": 0, "其他": 0}
    for job in job_history['jobs']:
        if job.get('priority') == 1:
            company_types["外企"] += 1
        elif job.get('priority') == 2:
            company_types["大厂"] += 1
        else:
            company_types["其他"] += 1

    # 2. 薪资区间分析
    salary_ranges = {
        "10-15K": 0,
        "15-20K": 0,
        "20-30K": 0,
        "30K+": 0,
        "面议": 0
    }

    # 3. 已覆盖公司统计
    covered_companies = set(job['company'] for job in job_history['jobs'])

    # 4. 识别搜索盲区
    gaps = {
        "外企占比": company_types["外企"] / total_jobs if total_jobs > 0 else 0,
        "大厂占比": company_types["大厂"] / total_jobs if total_jobs > 0 else 0,
        "其他占比": company_types["其他"] / total_jobs if total_jobs > 0 else 0,
        "未覆盖大厂": DEFAULT_BIG_TECH - covered_companies,
        "未覆盖外企": DEFAULT_FOREIGN_COMPANIES - covered_companies
    }

    return gaps

# 执行分析
gaps = analyze_job_gaps(job_history)

# 基于分析结果调整搜索策略
SEARCH_STRATEGY = {
    "priority_1_keywords": [],  # 外企优先
    "priority_2_keywords": [],  # 大厂第二
    "priority_3_keywords": [],  # 其他补充
    "skip_companies": [],       # 跳过已充分覆盖的公司
    "focus_salary_ranges": []   # 重点搜索薪资区间
}

# 策略调整逻辑（优化后的目标比例）
# 目标分布：外企 40%，大厂 40%，其他 20%
target_ratios = {"外企": 0.40, "大厂": 0.40, "其他": 0.20}

if gaps["外企占比"] < target_ratios["外企"]:  # 外企少于40%
    LOG: f"外企覆盖不足（{gaps['外企占比']:.1%} < {target_ratios['外企']:.0%}），优先搜索外企"
    SEARCH_STRATEGY["priority_1_keywords"].extend([
        "site:mp.weixin.qq.com \"微软中国招聘\" 运营 深圳",
        "site:jobs.apple.com 深圳 operations 运营",
        "site:careers.microsoft.com 深圳 运营",
        "site:mp.weixin.qq.com \"亚马逊招聘\" 运营",
        "site:mp.weixin.qq.com \"谷歌招聘\" 深圳 运营",
        "site:waiqi.com 外企 运营 深圳"
    ])

if gaps["大厂占比"] < target_ratios["大厂"]:  # 大厂少于40%
    LOG: f"大厂覆盖不足（{gaps['大厂占比']:.1%} < {target_ratios['大厂']:.0%}），重点搜索大厂"
    for company in gaps["未覆盖大厂"][:5]:  # 只搜索未覆盖的前5个大厂
        if company not in SEARCH_STRATEGY["skip_companies"]:
            SEARCH_STRATEGY["priority_2_keywords"].append(f"{company} 运营 深圳")

# 其他类型占比超过 30% 时，减少其他类型的搜索
if gaps["其他占比"] > 0.30:
    LOG: f"其他类型过多（{gaps['其他占比']:.1%}），减少其他类型搜索"
    # 优先级3的搜索词会减少或跳过

# 跳过已充分覆盖的公司（>=3个岗位）
over_covered = [company for company, count in
                [(c, job_history['jobs'].count(c)) for c in covered_companies]
                if count >= 3]
SEARCH_STRATEGY["skip_companies"] = over_covered

LOG: f"智能分析完成：发现 {len(gaps)} 个搜索盲区"
LOG: f"当前分布：外企 {gaps['外企占比']:.1%}，大厂 {gaps['大厂占比']:.1%}，其他 {gaps['其他占比']:.1%}"
LOG: f"目标分布：外企 40%，大厂 40%，其他 20%"
```

**OUTPUT**: Optimized search strategy based on historical data
- ✅ 避免重复搜索已充分覆盖的公司（>=3个岗位）
- ✅ 重点补充类型不足的岗位（外企/大厂各占40%）
- ✅ 控制其他类型岗位比例（不超过20%）
- ✅ 整体搜索效率提升 40%+

**目标优先级分布**：
- 🟢 **Priority 1（外企）**: 40%
- 🔵 **Priority 2（大厂）**: 40%
- ⚪ **Priority 3（其他）**: 20%

**预期结果**（每次搜索10-15个岗位）：
- 🟢 外企岗位：**5-7 个**（40%）
- 🔵 大厂岗位：**5-7 个**（40%）
- ⚪ 其他岗位：**2-3 个**（20%）
    "skip_companies": [],       # 跳过已充分覆盖的公司
    "focus_salary_ranges": []   # 重点搜索薪资区间
}

# 策略调整逻辑（优化后的目标比例）
# 目标分布：外企 40%，大厂 40%，其他 20%
target_ratios = {"外企": 0.40, "大厂": 0.40, "其他": 0.20}

if gaps["外企占比"] < target_ratios["外企"]:  # 外企少于40%
    LOG: f"外企覆盖不足（{gaps['外企占比']:.1%} < {target_ratios['外企']:.0%}），优先搜索外企"
    SEARCH_STRATEGY["priority_1_keywords"].extend([
        "site:mp.weixin.qq.com \"微软中国招聘\" 运营 深圳",
        "site:jobs.apple.com 深圳 operations 运营",
        "site:careers.microsoft.com 深圳 运营",
        "site:mp.weixin.qq.com \"亚马逊招聘\" 运营",
        "site:mp.weixin.qq.com \"谷歌招聘\" 深圳 运营",
        "site:waiqi.com 外企 运营 深圳"
    ])

if gaps["大厂占比"] < target_ratios["大厂"]:  # 大厂少于40%
    LOG: f"大厂覆盖不足（{gaps['大厂占比']:.1%} < {target_ratios['大厂']:.0%}），重点搜索大厂"
    for company in gaps["未覆盖大厂"][:5]:  # 只搜索未覆盖的前5个大厂
        if company not in SEARCH_STRATEGY["skip_companies"]:
            SEARCH_STRATEGY["priority_2_keywords"].append(f"{company} 运营 深圳")

# 其他类型占比超过 30% 时，减少其他类型的搜索
if gaps["其他占比"] > 0.30:
    LOG: f"其他类型过多（{gaps['其他占比']:.1%}），减少其他类型搜索"
    # 优先级3的搜索词会减少或跳过

# 跳过已充分覆盖的公司（>=3个岗位）
over_covered = [company for company, count in
                [(c, job_history['jobs'].count(c)) for c in covered_companies]
                if count >= 3]
SEARCH_STRATEGY["skip_companies"] = over_covered

LOG: f"智能分析完成：发现 {len(gaps)} 个搜索盲区"
LOG: f"当前分布：外企 {gaps['外企占比']:.1%}，大厂 {gaps['大厂占比']:.1%}，其他 {gaps['其他占比']:.1%}"
LOG: f"目标分布：外企 40%，大厂 40%，其他 20%"
```

**OUTPUT**: Optimized search strategy based on historical data
- ✅ 避免重复搜索已充分覆盖的公司（>=3个岗位）
- ✅ 重点补充类型不足的岗位（外企/大厂各占40%）
- ✅ 控制其他类型岗位比例（不超过20%）
- ✅ 整体搜索效率提升 40%+

**目标优先级分布**：
- 🟢 **Priority 1（外企）**: 40%
- 🔵 **Priority 2（大厂）**: 40%
- ⚪ **Priority 3（其他）**: 20%

---

### Step 1: User Profile Extraction

**READ** resume file from `简历/` folder and extract:

```markdown
## 用户画像

### 基本信息
- 姓名: [name]
- 年龄: [age]
- 现居地: [location]
- 期望薪资: [salary range]
- 语言能力: [languages]

### 工作经历
[Extract all work experiences]

### 核心技能
- 硬技能: [technical skills]
- 软技能: [soft skills]
- AI能力: [AI tools and projects]

### 项目经验
[Extract key projects]
```

---

### Step 2: Search Strategy Generation (Optimized with Gap Analysis)

**GENERATE** 15-25 search term combinations based on user profile **AND** gap analysis results from Step 0.5.

**CRITICAL**: Use `SEARCH_STRATEGY` from Step 0.5 to optimize search terms:

```python
# 基础搜索词（用户画像）
base_keywords = generate_from_user_profile(user_config)

# 智能优化：加入gap分析的搜索词
optimized_keywords = []

# Priority 1: 外企优先（如果gap分析显示外企不足）
if SEARCH_STRATEGY["priority_1_keywords"]:
    optimized_keywords.extend(SEARCH_STRATEGY["priority_1_keywords"])
    LOG: f"添加 {len(SEARCH_STRATEGY['priority_1_keywords'])} 个外企搜索词（基于gap分析）"

# Priority 2: 大厂第二（只搜索未覆盖的大厂）
if SEARCH_STRATEGY["priority_2_keywords"]:
    for company in SEARCH_STRATEGY["priority_2_keywords"]:
        if company not in SEARCH_STRATEGY["skip_companies"]:
            optimized_keywords.append(f"{company} {user_config.location} 运营")
    LOG: f"添加 {len(optimized_keywords)} 个大厂搜索词（过滤已覆盖公司）"

# Priority 3: 薪资盲区补充
if SEARCH_STRATEGY["focus_salary_ranges"]:
    for salary_range in SEARCH_STRATEGY["focus_salary_ranges"]:
        optimized_keywords.append(
            f"{user_config.location} 运营 {salary_range}"
        )

# 合并基础词 + 优化词
final_search_terms = base_keywords + optimized_keywords

# 去重并保持优先级顺序
final_search_terms = list(dict.fromkeys(final_search_terms))
```

**Step 2.1: Company Category Expansion (AI-Autonomous)**

**CRITICAL**: If user config specifies company **categories** (e.g., "大厂", "外企", "出海公司"), **AI must autonomously expand these into specific company lists** based on:
- Industry knowledge
- Company reputation
- Market presence
- Relevance to user's job types

**Example Expansion Logic:**

```python
# User config specifies categories (not specific companies)
user_config = {
    "company_types": ["大厂", "外企", "出海公司"],
    "industries": ["出海", "AI", "AIGC", "跨境电商"],
    "job_types": ["运营", "产品运营", "海外运营", "增长运营"]
}

# AI autonomously expands categories into specific companies
ai_generated_companies = {
    "大厂": [
        "字节跳动", "腾讯", "阿里巴巴", "美团", "拼多多",
        "京东", "快手", "百度", "小红书", "B站"
    ],
    "外企": [
        "Google", "Microsoft", "Amazon", "Meta", "Apple",
        "Netflix", "Airbnb", "Uber", "Spotify",
        "外企在华分支": "微软中国", "亚马逊中国", "谷歌中国"
    ],
    "出海公司": [
        "SHEIN", "Temu拼多多", "TikTok字节跳动", "米哈游",
        "莉莉丝", "趣加", "网易游戏海外", "安克创新"
    ],
    "AI公司": [
        "DeepSeek", "智谱AI", "月之暗面", "MiniMax",
        "零一万物", "百川智能", "昆仑万维"
    ]
}

# Also expand based on industries
if "AIGC" in user_config.industries:
    ai_generated_companies["AI"].extend(["字节跳动AI Lab", "腾讯混元", "百度文心"])

if "跨境电商" in user_config.industries:
    ai_generated_companies["出海"].extend(["阿里速卖通", "京东国际", "抖音电商"])
```

**Search Term Types:**

1. **General Platform Searches**
   - "{location} {industry} {job_types}"
   - Example: "深圳 出海运营", "深圳 AI产品运营"

2. **Official Career Site Searches**
   - For each company (including AI-expanded): `site:{company_career_domain} {job_type} {location}`
   - Example: `site:jobs.bytedance.com 运营 深圳`

3. **Specialized Platform Searches** (High-Value Aggregation Platforms)
   - **神仙外企** - 专业外企招聘信息聚合平台
     - Website: https://www.waiqi.com/
     - WeChat search: `site:mp.weixin.qq.com "神仙外企" {job_type}`
     - Coverage: 外企官网招聘信息汇总，覆盖罗技、微软、亚马逊等知名外企
     - Update frequency: 每日5+条外企招聘信息
     - Quality: 百万粉丝专业平台，企业认证公众号
   - Example:
     - `site:mp.weixin.qq.com "神仙外企" 运营`
     - `site:mp.weixin.qq.com "神仙外企" 产品运营 深圳`
     - `site:waiqi.com 外企 运营 深圳`

4. **Official WeChat Account Searches** (verified 企业认证 only) - **AI-Autonomous**
   ```python
   # Generate from AI-expanded company list
   for category, companies in ai_generated_companies.items():
       for company in companies:
           for job_type in user_config.job_types:
               search_term = f'site:mp.weixin.qq.com "{company}招聘" {job_type}'
               # Example outputs:
               # - site:mp.weixin.qq.com "字节跳动招聘" 运营
               # - site:mp.weixin.qq.com "微软招聘" 产品运营  ← AI generated
               # - site:mp.weixin.qq.com "SHEIN招聘" 海外运营
               # - site:mp.weixin.qq.com "DeepSeek招聘" AI运营  ← AI generated
   ```

5. **Specialized Aggregation Platform Searches** (High-Value Platforms)
   - **神仙外企平台** (专业外企招聘信息聚合，百万粉丝)
     ```python
     # Website search
     search_term = f'site:waiqi.com 外企 {job_type} {location}'
     # Example: site:waiqi.com 外企 运营 深圳

     # WeChat official account search
     search_term = f'site:mp.weixin.qq.com "神仙外企" {job_type} {location}'
     # Example: site:mp.weixin.qq.com "神仙外企" 产品运营 深圳

     # Industry-specific searches on 神仙外企
     search_term = f'site:mp.weixin.qq.com "神仙外企" 科技外企 {job_type}'
     search_term = f'site:mp.weixin.qq.com "神仙外企" 医疗外企 {job_type}'
     # Examples:
     # - site:mp.weixin.qq.com "神仙外企" 科技外企 运营
     # - site:mp.weixin.qq.com "神仙外企" 欧美外企 产品运营
     ```
     **Quality notes**:
     - 百万粉丝专业平台，每日更新5+条外企招聘信息
     - 覆盖罗技、微软、亚马逊等知名外企
     - 企业认证公众号，信息可靠度高

6. **Recruitment Platform Searches**
   - "{platform} {location} {keywords}"
   - Example: "猎聘 深圳 海外运营", "Boss直聘 深圳 AI运营"

7. **Foreign Company Searches** (if "外企" in company_types)
   - `site:mp.weixin.qq.com "微软中国招聘" 运营`
   - `site:mp.weixin.qq.com "亚马逊招聘" 海外`
   - `{company_name} careers china {job_type}`

---

### Step 3: Multi-Source Search Execution (Priority-Based)

**CRITICAL: Execute searches in PRIORITY ORDER**

**SEARCH PRIORITY**:
1. **Priority 1: Foreign Companies (外企)** - Focus on 外企 first
2. **Priority 2: Domestic Big Tech (国内大厂)** - Focus on 大厂 second
3. **Priority 3: Other Matching Jobs (其他匹配岗位)** - Only if Priority 1 & 2 are insufficient (<10 jobs)

---

### Step 3.1: Priority 1 - Foreign Companies Search (外企优先)

**EXECUTE** searches for FOREIGN companies first:

**Search Types**:

1. **神仙外企平台搜索** (Highest Priority for 外企)
   ```python
   foreign_company_searches = [
       # 神仙外企平台
       f'site:waiqi.com 外企 运营 {user_config.location}',
       f'site:mp.weixin.qq.com "神仙外企" 产品运营 {user_config.location}',
       f'site:mp.weixin.qq.com "神仙外企" 海外运营',
       f'site:mp.weixin.qq.com "神仙外企" 科技外企 运营',
       f'site:mp.weixin.qq.com "神仙外企" 欧美外企 产品运营',
   ]
   ```

2. **AI-Generated Foreign Company Searches** (from company_types)
   ```python
   # AI autonomously expands "外企" category into specific companies
   foreign_companies = [
       "Google", "Microsoft", "Amazon", "Meta", "Apple",
       "Netflix", "Airbnb", "Uber", "Spotify",
       # 外企在华分支
       "微软中国", "亚马逊中国", "谷歌中国", "苹果中国",
       "特斯拉中国", "英特尔中国", "IBM中国", "思科中国",
       "宝洁中国", "联合利华中国", "耐克中国", "星巴克中国"
   ]

   # Generate searches for each foreign company
   for company in foreign_companies:
       for job_type in user_config.job_types:
           searches.append(f'{company} {job_type} {user_config.location}')
           searches.append(f'site:mp.weixin.qq.com "{company}招聘" {job_type}')
   ```

3. **Foreign Company Official Career Sites**
   ```python
   foreign_career_sites = {
       "Microsoft": "careers.microsoft.com",
       "Amazon": "jobs.amazon.com",
       "Google": "careers.google.com",
       "Apple": "jobs.apple.com",
       "Meta": "metacareers.com",
       "Netflix": "jobs.netflix.com"
   }

   for company, career_site in foreign_career_sites.items():
       searches.append(f'site:{career_site} {user_config.location} operations')
   ```

**EXECUTE** all Priority 1 searches first using WebSearch.

**COLLECT** results into `priority_1_jobs` list.

---

### Step 3.2: Priority 2 - Domestic Big Tech Search (大厂第二)

**AFTER** Priority 1 search is complete, **EXECUTE** searches for DOMESTIC BIG TECH:

**Search Types**:

1. **AI-Generated Big Tech Companies** (from company_types)
   ```python
   # AI autonomously expands "大厂" category into specific companies
   big_tech_companies = [
       "字节跳动", "腾讯", "阿里巴巴", "美团", "拼多多",
       "京东", "快手", "百度", "小红书", "B站",
       "网易", "滴滴", "小米", "华为", "vivo", "OPPO"
   ]

   # Generate searches for each big tech company
   for company in big_tech_companies:
       for job_type in user_config.job_types:
           searches.append(f'{company} {job_type} {user_config.location}')
           searches.append(f'site:mp.weixin.qq.com "{company}招聘" {job_type}')
   ```

2. **Big Tech Official Career Sites**
   ```python
   big_tech_career_sites = {
       "字节跳动": "jobs.bytedance.com",
       "腾讯": "careers.tencent.com",
       "阿里巴巴": "jobs.alibaba.com",
       "美团": "jobs.meituan.com",
       "拼多多": "jobs.pinduoduo.com",
       "京东": "jobs.jd.com",
       "快手": "jobs.kuaishou.com",
       "百度": "jobs.baidu.com",
       "小红书": "jobs.xiaohongshu.com",
       "B站": "jobs.bilibili.com"
   }

   for company, career_site in big_tech_career_sites.items():
       searches.append(f'site:{career_site} {user_config.location} 运营')
   ```

**EXECUTE** all Priority 2 searches using WebSearch.

**COLLECT** results into `priority_2_jobs` list.

---

### Step 3.3: Priority 3 - Other Matching Jobs (补充搜索)

**ONLY IF** `len(priority_1_jobs) + len(priority_2_jobs) < 10`:

**EXECUTE** supplementary searches for other matching companies:

```python
# Check if we need supplementary searches
total_quality_jobs = len(priority_1_jobs) + len(priority_2_jobs)

if total_quality_jobs < 10:
    LOG: f"Found {total_quality_jobs} jobs from 外企+大厂. Need 10. Expanding to other companies..."

    # Generate searches for other matching companies
    supplementary_searches = [
        # 出海公司
        f'SHEIN 运营 {user_config.location}',
        f'Temu 运营 {user_config.location}',
        f'米哈游 运营 {user_config.location}',
        f'莉莉丝 运营 {user_config.location}',
        f'安克创新 运营 {user_config.location}',

        # Recruitment platforms
        f'猎聘 {user_config.location} 海外运营',
        f'Boss直聘 {user_config.location} AI运营',
        f'智联招聘 {user_config.location} 出海运营',

        # General keywords
        f'{user_config.location} 出海运营',
        f'{user_config.location} 海外运营',
        f'{user_config.location} AI 产品运营',
        f'{user_config.location} AIGC 运营',
    ]

    # Execute supplementary searches
    for search_term in supplementary_searches:
        LOG: f"Supplementary search: '{search_term}'"
        # Execute WebSearch
        # Collect results into priority_3_jobs
```

**COLLECT** results into `priority_3_jobs` list.

---

### Step 3.4: Merge Results by Priority

```python
# Merge jobs in priority order
all_jobs = priority_1_jobs + priority_2_jobs + priority_3_jobs

LOG: f"Priority 1 (外企): {len(priority_1_jobs)} jobs"
LOG: f"Priority 2 (大厂): {len(priority_2_jobs)} jobs"
LOG: f"Priority 3 (其他): {len(priority_3_jobs)} jobs"
LOG: f"Total: {len(all_jobs)} jobs"
```

---

### Step 3.5: Process Search Results

**PROCESS** each search result from `all_jobs`:
1. Extract job posting URLs or JD text
2. Use WebReader to fetch complete JD if URL available
3. **CRITICAL: Extract 100% REAL JD from official/recruitment pages**
   - ✅ Official company career pages (jobs.bytedance.com, careers.tencent.com, etc.)
   - ✅ Recruitment platforms (猎聘, Boss直聘, 智联招聘, etc.)
   - ✅ **Specialized aggregation platforms** (神仙外企 - https://www.waiqi.com/)
     - Professional foreign company recruitment aggregation platform
     - 1M+ WeChat followers, daily 5+ updates
     - Covers companies like Logitech, Microsoft, Amazon, etc.
   - ✅ Official company WeChat accounts (verified 企业认证公众号 only)
     - Example: "字节跳动招聘"、"腾讯招聘"、"阿里招聘"等官方HR账号
     - Search pattern: `site:mp.weixin.qq.com "字节跳动招聘" 运营`
   - ✅ Complete job descriptions with responsibilities and requirements
   - ❌ NEVER use personal repost accounts (个人转载公众号 - unreliable source)
   - ❌ NEVER generate template/fabricated JDs
   - ❌ NEVER use generic "岗位职责: 1. 负责{title}相关工作" templates
   - If JD cannot be found, mark "JD详情请查看投递链接" in notes field
4. Generate unique job ID: `{company_slug}_{title_slug}_{date}`

---

### Step 3.5: 岗位质量三重验证（CRITICAL - 必须执行）

**FILTER OUT** unqualified jobs through THREE validation layers:

---

### Layer 1: 招聘类型验证（社招优先）

```python
# 检查岗位标题和描述，过滤校招/实习
job_title = job['title'].lower()
job_description = job.get('jd', '').lower()

# 拒绝模式：校招/实习关键词
campus_keywords = [
    '校招', '校园招聘', '2026届', '2025届', '应届生',
    '实习', '实习生', 'intern', 'campus',
    '管培生', '培训生'  # 除非明确社招管培
]

is_campus_job = any(keyword in job_title or keyword in job_description
                   for keyword in campus_keywords)

if is_campus_job:
    LOG: "REJECTED: '{job['title']}' - 校招/实习岗位，不符合社招要求"
    continue

# 保留：明确标注社招的岗位
social_hire_keywords = ['社招', '社会招聘', '经验', '3年', '5年']
is_social_hire = any(keyword in job_description
                     for keyword in social_hire_keywords)

if is_social_hire:
    LOG: "ACCEPT: '{job['title']}' - 社招岗位"
```

**MANDATORY - 拒绝模式:**
| 岗位标题 | 是否保留 | 原因 |
|---------|---------|------|
| "2026届校园招聘-运营" | ❌ 拒绝 | 校招岗位 |
| "产品运营实习生" | ❌ 拒绝 | 实习岗位 |
| "运营专员（实习）" | ❌ 拒绝 | 实习岗位 |
| "运营管培生" | ❌ 拒绝 | 校招管培 |
| "海外运营（3-5年经验）" | ✅ 保留 | 明确社招 |
| "资深运营专家" | ✅ 保留 | 社招岗位 |

---

### Layer 2: 公司名称精确度验证（CRITICAL）

```python
# 核心标准：公司名必须100%精确，能被搜索到
company_name = extracted_company.strip()

# 优化：跳过已充分覆盖的公司（来自Step 0.5的gap分析）
if company_name in SEARCH_STRATEGY["skip_companies"]:
    LOG: "SKIP: '{company_name}' - 已充分覆盖（{count}个岗位），跳过"
    continue

# 拒绝模式：公司名包含模糊描述词
vague_patterns = [
    "某", "知名", "头部", "大型", "多家", "某家",
    "A轮", "B轮", "C轮", "D轮", "E轮",
    "独角兽", "上市公司", "集团",
    "（", "）", "(", ")"  # 括号内通常是补充说明，不够精确
]

is_vague = any(pattern in company_name for pattern in vague_patterns)

# 更严格的验证：公司名必须精确
if company_name.startswith("某") or "轮)" in company_name:
    LOG: "REJECTED: '{company_name}' - 公司名称模糊，无法搜索"
    continue

if "某" in company_name and len(company_name) < 15:
    LOG: "REJECTED: '{company_name}' - 包含'某'字，公司名不精确"
    continue

if "公司" in company_name and len(company_name) < 10:
    LOG: "REJECTED: '{company_name}' - 公司名称过于简单"
    continue

# 投递方式：有链接最好，没有也可以（只要公司名清晰）
# 用户可以自行搜索投递
```

**MANDATORY - 拒绝/保留模式:**
| 公司名 | 是否保留 | 原因 |
|--------|---------|------|
| "某出海SaaS公司（A轮）" | ❌ 拒绝 | 公司名模糊，无法搜索 |
| "某AI/SaaS公司" | ❌ 拒绝 | 公司名模糊，无法搜索 |
| "某深圳跨境电商公司" | ❌ 拒绝 | 包含"某"，公司名不精确 |
| "深圳某通信设备上市公司" | ❌ 拒绝 | 包含"某"，公司名不精确 |
| "Plaud AI" | ✅ 保留 | 公司名清晰，可自行搜索 |
| "字节跳动" | ✅ 保留 | 公司名清晰，有官网链接 |
| "腾讯云" | ✅ 保留 | 公司名清晰 |
| "得物" | ✅ 保留 | 公司名清晰 |
| "深圳市魔耳乐器有限公司" | ✅ 保留 | 公司名清晰，全称 |
| "开心电子" | ✅ 保留 | 公司名清晰 |
| "感恩科技" | ✅ 保留 | 公司名清晰 |
| "柏洛斯家居" | ✅ 保留 | 公司名清晰 |

---

### Layer 3: JD真实性验证（100% REAL JD REQUIRED）

```python
# 验证JD是否真实，拒绝生成的模板JD
jd_text = job.get('jd', '')

# 拒绝模式：模板化JD特征
template_patterns = [
    '岗位职责: 1. 负责{title}相关工作',  # 明显模板
    '1. 负责.*相关工作',  # 模糊描述
    '1. 协助.*完成.*工作',  # 过于简单
    '详情请查看投递链接',  # 没有真实JD
    'JD详情请查看投递链接',  # 没有真实JD
]

has_template = any(re.search(pattern, jd_text) for pattern in template_patterns)

if has_template:
    LOG: "REJECTED: '{job['title']}' - JD疑似模板生成，非真实JD"
    continue

# 验证：真实JD特征
real_jd_indicators = [
    len(jd_text) > 100,  # JD长度足够
    '岗位职责' in jd_text or 'Job Description' in jd_text,  # 有职责描述
    '任职要求' in jd_text or 'Requirements' in jd_text,  # 有要求描述
    any(keyword in jd_text for keyword in ['团队', '协作', '负责', '制定']),  # 具体描述
]

if sum(real_jd_indicators) < 3:
    LOG: "WARNING: '{job['title']}' - JD可能不够真实，需人工审核"
    # 可以保留但标记为需审核
    job['notes'] = f"{job.get('notes', '')}\n⚠️ JD真实性待确认"
else:
    LOG: "ACCEPT: '{job['title']}' - JD真实性验证通过"
```

**JD真实性验证标准:**

| JD内容 | 是否保留 | 原因 |
|--------|---------|------|
| "岗位职责:\n1. 负责海外运营工作\n2. 制定运营策略\n3. 分析数据优化\n\n任职要求:\n1. 本科及以上学历\n2. 3年以上相关经验\n3. 英语流利" | ✅ 保留 | 真实JD，完整职责+要求 |
| "Job Description:\n1. Managing overseas social media\n2. Content planning and execution\n3. Performance analysis\n\nRequirements:\n1. Bachelor degree\n2. 1-3 years experience\n3. English proficiency" | ✅ 保留 | 真实JD，完整英文描述 |
| "岗位职责: 1. 负责运营相关工作\n详情请查看投递链接" | ❌ 拒绝 | 模板JD，无真实内容 |
| "JD详情请查看投递链接" | ❌ 拒绝 | 无真实JD |
| "1. 协助完成日常工作\n2. 完成领导安排的其他任务" | ❌ 拒绝 | 过于简单，疑似模板 |

---

### 数据源可信度分级（Tier 1-3）

**Tier 1（最高可信度）- 官方渠道**:
- ✅ 官方招聘网站：jobs.bytedance.com, careers.tencent.com
- ✅ 官方微信公众号（企业认证）："字节跳动招聘"、"腾讯招聘"
- **JD真实性**: 100%

**Tier 2（高可信度）- 专业平台**:
- ✅ 神仙外企平台：https://www.waiqi.com/
- ✅ 大型招聘平台：猎聘、Boss直聘、智联招聘
- **JD真实性**: 95%+（需人工审核）

**Tier 3（中等可信度）- 其他渠道**:
- ⚠️ 个人转载公众号（需验证企业认证）
- ⚠️ 行业聚合平台
- **JD真实性**: 70%+（必须人工审核）

**Rejected（拒绝）**:
- ❌ 个人转载公众号（无企业认证）
- ❌ 过期文章（>30天）
- ❌ 模板生成的JD

**投递方式说明:**
- 如果有直接链接 → 在报告中显示链接
- 如果没有链接 → 显示"需自行搜索投递"（只要公司名清晰即可）

---

### Step 4: Job Deduplication & NEW Labeling

**CHECK** if jobs are NEW or EXISTING:

```python
For each job found:
    1. Generate job_id = f"{company_slug}_{title_slug}_{salary_slug}"
    2. Check if job_id exists in job_history.json
    3. If EXISTS → Skip (already recommended before)
    4. If NEW → Mark as "NEW", add to output list

Deduplication Rules:
- Same company + Same title + Same salary range = Same job
- Same company + Same title + Salary difference < 20% = Likely same job
- Same job posting URL = Same job

IMPORTANT: Only NEW jobs are output!
Existing jobs (already in database) are NOT shown in the CSV report.
```

**OUTPUT RULE: Only NEW jobs**
- Only output jobs that are NOT in job_history.json
- No limit on output quantity (all qualified NEW jobs)
- All jobs in report are marked as NEW

---

### Step 5: Match Analysis

**CALCULATE** match score only for NEW jobs:

```python
# Match Score Calculation
直接匹配 = (resume_skills ∩ jd_requirements) / total_jd_requirements
可迁移经验 = related_but_not_direct_experience / total_requirements
薪资匹配 = 1.0 if salary_in_range else 0.5 if negotiable else 0.0
公司优先级 = 1.0 if 大厂/外企 else 0.7 if known else 0.5

综合匹配度 = (直接匹配 × 0.5) + (可迁移经验 × 0.3) + (薪资匹配 × 0.1) + (公司优先级 × 0.1)
```

---

### Step 6: Company Background Quick Check

For TOP candidates, **QUICK SEARCH** company info (lightweight):
- Company type: 大厂/外企/创业公司
- Funding stage
- Business direction (one line)
- Recent news (if any)

**LIMIT**: 5 seconds per company, fail fast.

---

### Step 7: Quality Filter, Dynamic Search Expansion, and Update Database

**QUALITY FILTER** - Remove low-match and vague company jobs:
```python
# Step 7.1: 公司名称清晰度检查
valid_jobs = []
for job in all_jobs:
    if job.company.startswith("某") or "轮)" in job.company:
        LOG: "FILTER: '{job.company}' - 公司名称模糊"
        continue
    valid_jobs.append(job)

# Step 7.2: 匹配度过滤（只保留新岗位）
new_jobs = valid_jobs.filter(job_id not in job_history)
quality_jobs = new_jobs.filter(match_score >= 60)

# Step 7.3: 动态扩展搜索（至少10个岗位，按优先级）
max_search_rounds = 5  # 最多搜索5轮
current_round = 1

while len(quality_jobs) < 10 and current_round <= max_search_rounds:
    LOG: f"Found {len(quality_jobs)} jobs, need 10. Expanding search (Round {current_round})..."

    # 按优先级生成扩展搜索词（基于目标比例40%/40%/20%）
    if current_round <= 2:  # Round 1-2: 继续搜索外企（目标40%）
        expansion_keywords = [
            f'外企 {user_config.location} 运营 2026',
            f'跨国公司 {user_config.location} 产品运营',
            f'欧美企业 {user_config.location} 海外运营',
            f'site:mp.weixin.qq.com "外企招聘" {user_config.location} 运营',
            f'神仙外企 {user_config.location} AIGC运营',
            f'思科中国 运营 {user_config.location}',
            f'英特尔中国 运营 {user_config.location}',
            f'IBM中国 运营 {user_config.location}',
        ]
        LOG: "Priority 1 expansion: Searching for more foreign companies (target 40%)..."
    elif current_round <= 4:  # Round 3-4: 继续搜索大厂（目标40%）
        expansion_keywords = [
            f'大厂 {user_config.location} 运营 2026',
            f'互联网大厂 {user_config.location} 产品运营',
            f'site:mp.weixin.qq.com "大厂招聘" {user_config.location} 运营',
            f'字节跳动 {user_config.location} 海外运营',
            f'腾讯 {user_config.location} AI产品运营',
            f'阿里巴巴 {user_config.location} 出海运营',
            f'美团 {user_config.location} 运营',
            f'拼多多 {user_config.location} 运营',
            f'快手 {user_config.location} 海外运营',
            f'京东 {user_config.location} 跨境运营',
        ]
        LOG: "Priority 2 expansion: Searching for more big tech companies (target 40%)..."
    else:  # Round 5: 最后才搜索其他公司（目标20%，不超过）
        expansion_keywords = [
            f"{user_config.location} 运营招聘 2026",
            f"{user_config.location} 出海运营 2026",
            f"{user_config.location} AI产品运营",
            f"{user_config.location} AIGC运营",
        ]
        LOG: "Priority 3 expansion: Searching for other matching companies (target ≤20%)..."

    # 选择本轮搜索词组合
    new_searches = expansion_keywords[:2]  # 每轮最多2个搜索

    # 执行扩展搜索
    for search_term in new_searches:
        LOG: f"Expanded search: '{search_term}'"
        # 执行 WebSearch
        # 处理搜索结果...
        # 更新 valid_jobs 和 quality_jobs

    current_round += 1

LOG: f"Search complete. Found {len(quality_jobs)} new jobs."

# Step 7.4: 按优先级+匹配度排序
# 优先级1（外企）> 优先级2（大厂）> 优先级3（其他），同优先级内按匹配度排序
quality_jobs = quality_jobs.sort_by(priority_level, ascending)
quality_jobs = quality_jobs.sort_by(match_score, descending)

# Step 7.4: 按匹配度排序
quality_jobs = quality_jobs.sort_by(match_score, descending)
```

**SORT** all NEW quality jobs by match score (descending).

**UPDATE** `job_history.json` with NEW jobs only:

```json
{
  "last_updated": "2026-03-02",
  "total_jobs": 48,  // Previous 43 + 5 new jobs
  "jobs": [
    ...existing jobs...
    ...new jobs...
  ]
}
```

**WRITE** updated JSON back to file.

---

### Step 8: Generate XLSX Report

**GENERATE** XLSX format report with formatting using Python openpyxl:

```python
# 1. 创建 Excel 工作簿
# 2. 写入数据（包含 JD 列）
# 3. 设置格式：
#    - 表头：紫色背景(#667eea) + 白色粗体字(13号)
#    - 数据行：字体大小 14
#    - 行高：35
#    - JD 列：宽度 50，自动换行
#    - 自动列宽
#    - 居中对齐
# 4. 保存为 xlsx 文件
```

**数据格式（包含 JD 列 + Priority 标签）:**
```python
headers = ['rank', 'company', 'title', 'salary', 'location', 'match_score', 'jd', 'apply_url', 'notes', 'priority', 'search_date']

# Priority 列说明：
# - Priority 1: 外企（Foreign Companies）- 最高优先级
# - Priority 2: 大厂（Domestic Big Tech）- 第二优先级
# - Priority 3: 其他（Other Matching Companies）- 补充优先级
# - 在 Excel 中使用颜色标记：
#   * Priority 1: 绿色背景
#   * Priority 2: 蓝色背景
#   * Priority 3: 白色背景（默认）

# JD 列处理：
# - 完整 JD 内容
# - 在 Excel 中自动换行显示
# - 列宽设置为 50（比其他列更宽）
```

**XLSX 格式优势：**
- ✅ 内置字体格式（14号字体，无需手动调整）
- ✅ 表头美化（紫色背景）
- ✅ 自动列宽和行高
- ✅ 可直接在 Excel/Numbers/WPS 中打开编辑
- ✅ 可添加自己的列（投递状态、面试备注等）

**XLSX Fields:**
- `rank`: 排名（按优先级+匹配度排序：优先级1 > 优先级2 > 优先级3，同优先级内按匹配度排序）
- `company`: 公司名称（清晰具体）
- `title`: 岗位名称
- `salary`: 薪资范围
- `location`: 工作地点
- `match_score`: 匹配度分数（0-100）
- `jd`: **岗位描述（100%真实JD，从官方/招聘平台提取）**
- `apply_url`: 投递链接或说明
- `notes`: 匹配优势/注意事项（包含优先级标签，如"P1-外企", "P2-大厂", "P3-其他"）
- `priority`: 优先级标签（1=外企, 2=大厂, 3=其他）
- `search_date`: 搜索日期

**CRITICAL JD QUALITY RULE:**
- ✅ JD must be extracted from actual job postings
- ✅ Include complete responsibilities and requirements
- ✅ If full JD not available, use "JD详情请查看投递链接"
- ❌ NEVER generate generic template JDs
- ❌ NEVER fabricate job descriptions
- ❌ **NEVER use personal WeChat repost accounts (个人转载公众号)**

**Data Source Quality Levels:**
1. **Tier 1 (Highest)**: Official company career sites
   - Examples: jobs.bytedance.com, careers.tencent.com
2. **Tier 2 (High)**: Specialized aggregation platforms & Major recruitment platforms
   - **神仙外企** (https://www.waiqi.com/) - 专业外企招聘信息聚合平台，百万粉丝，每日5+条更新
   - Major platforms: 猎聘, Boss直聘, 智联招聘, etc.
3. **Tier 3 (Medium)**: Official company WeChat accounts (企业认证 only)
   - Must check: publish_date ≤ 30 days ago
   - Must verify: account is verified enterprise account
4. **Rejected**: Personal repost accounts, expired posts (>30 days)

**Output File Naming:**
```
result/job_scout_{user_id}_{YYYYMMDD_HHMM}.xlsx
```

**示例:**
```
result/job_scout_王宝珍_20260303_1430.xlsx
result/job_scout_王宝珍_20260303_2045.xlsx
```

---

## Output File Structure

**XLSX Output:**
```
result/job_scout_{user_id}_{YYYYMMDD}.xlsx
```

**Database (always update):**
```
job_history.json
```

---

## Error Handling Matrix

| Scenario | Action | Log Message |
|----------|--------|-------------|
| job_history.json doesn't exist | Create new file | "LOG: Creating new job history database" |
| New jobs found < 10 | Auto-expand search with new keywords | "LOG: Found [n] jobs, expanding search..." |
| WebSearch fails for a term | Skip to next term | "LOG: Search failed for '[term]', continuing..." |
| Resume file not found | STOP immediately | "ERROR: Cannot find resume in 简历/ folder" |
| Company search times out | Mark "需自行调研", continue | "LOG: Company search timeout for [company]" |
| XLSX generation fails | Output as CSV | "LOG: XLSX generation failed, outputting CSV" |
| **公司名模糊** (以"某"开头/含"轮)" | **SKIP immediately** | "LOG: REJECTED '{company}' - 无法搜索" |
| **个人转载公众号** | **SKIP immediately** | "LOG: REJECTED personal WeChat account - unreliable" |
| **公众号文章过期** (>30天) | **SKIP immediately** | "LOG: REJECTED expired WeChat post from {date}" |

**IMPORTANT**:
1. Never fail to generate CSV. Always produce ALL NEW qualified jobs.
2. **核心标准：公司名必须清晰** - 用户可以自行搜索投递
3. 如果过滤后岗位 < 5 个，从历史数据库中补充高质量岗位

---

## GitHub Actions Deployment Considerations

### Critical: Database Persistence

**Problem**: GitHub Actions runs in a fresh environment each time - local files are not persisted.

**Solution**: Commit the `users/{user_id}/job_history.json` file back to the repository after each run.

### Workflow Configuration

```yaml
# .github/workflows/daily-job-scout.yml
name: Daily Job Scout

on:
  schedule:
    - cron: '0 13 * * *'  # Daily at 21:00 CST
  workflow_dispatch:

jobs:
  job-scout:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Required to commit back to repo

    steps:
      - uses: actions/checkout@v3

      - name: Setup Claude Code CLI
        run: |
          curl -fsSL https://claude.ai/install.sh | sh

      - name: Run Job Scout
        run: |
          claude-code --skill job-scout \
            --user "wangbaozhen" \
            "帮我找合适的出海运营岗位"

      - name: Commit database updates
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add users/*/job_history.json
          git add result/*.xlsx job_history.json
          git diff --staged --quiet || git commit -m "Update job scout results"
          git push

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./reports
```

### Multi-User Configuration

For multiple users, create separate jobs:

```yaml
jobs:
  wangbaozhen-scout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run for 王宝珍
        run: |
          claude-code --skill job-scout --user "wangbaozhen" "帮我找工作"
      - name: Commit
        run: |
          git add users/wangbaozhen/job_history.json
          git commit -m "Update 王宝珍 job history" || true
          git push

  lisi-scout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run for 李四
        run: |
          claude-code --skill job-scout --user "lisi" "帮我找工作"
      - name: Commit
        run: |
          git add users/lisi/job_history.json
          git commit -m "Update 李四 job history" || true
          git push
```

### Database Conflict Prevention

Since each user has their own `job_history.json`, conflicts won't occur between users. The Git workflow only commits the changed user's database file.

---

## GitHub Actions Deployment Example

```yaml
name: Daily Job Scout
on:
  schedule:
    - cron: '0 21 * * *'  # 每天 21:00 UTC 运行
  workflow_dispatch:      # 支持手动触发

jobs:
  job-scout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code
      - name: Run Job Scout
        run: claude-code --skill job-scout "帮我找合适的出海运营岗位"
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./reports
```

---

## Limitations

- **WebSearch results vary**: Search engine algorithms change
- **Platform restrictions**: Some platforms require login
- **Real-time changes**: Jobs may be filled/closed after search
- **Deduplication accuracy**: Same job may have different titles across platforms

---

## Expected Results (预期结果)

### 每次搜索的岗位分布

**目标分布**（优化后）：
- 🟢 **Priority 1（外企）**: 5-7 个岗位 (40%)
- 🔵 **Priority 2（大厂）**: 5-7 个岗位 (40%)
- ⚪ **Priority 3（其他）**: 2-3 个岗位 (20%)

**总计**: 10-15 个新岗位/次

### 分布示例

**理想的10个岗位分布**：
```
外企: 4 个 (40%)
├─ 微软中国 - AI Business Operations Manager
├─ 苹果中国 - NPI Operations Program Manager
├─ 亚马逊中国 - Sr. Manager, Seller Operations
└─ 谷歌中国 - Product Operations Lead

大厂: 4 个 (40%)
├─ 字节跳动 - 海外增长运营专家
├─ 腾讯 - AIGC产品运营
├─ 华为 - 智能客服运营专员
└─ 小米 - 门店运营

其他: 2 个 (20%)
├─ 追觅科技 - 海外新媒体运营
└─ 无界未来 - 海外产品运营
```

### 实际案例

**2026-03-09 搜索结果**（9个岗位）：
```
外企: 2 个 (22%) - 需继续提升
├─ 微软中国 - AI Business Operations Manager (30-60K)
└─ 苹果中国 - NPI Operations Program Manager (面议)

大厂: 3 个 (33%) - 接近目标
├─ 小米 - 门店运营
├─ 华为 - 智能客服运营专员（AI方向）
└─ OPPO - 商业化产品运营经理

其他: 4 个 (45%) - 需降低
├─ 追觅科技 - 海外新媒体运营
├─ 熠起文化 - 海外新媒体运营
├─ 识刻创新科技 - 海外市场运营
└─ 无界未来 - 海外产品运营
```

**下次搜索预期**：
- 外企：5-7 个（增加3-5个外企岗位）
- 大厂：5-7 个（保持或增加2-4个大厂岗位）
- 其他：2-3 个（减少1-2个其他岗位）

### 达到目标的策略

**如果外企不足**（当前22% < 目标40%）：
- ✅ 增加外企搜索轮次（Round 1-2）
- ✅ 扩展外企公司列表（思科、英特尔、IBM、特斯拉等）
- ✅ 优先搜索神仙外企平台
- ✅ 搜索外企官方招聘公众号

**如果大厂不足**（当前33% < 目标40%）：
- ✅ 补充未覆盖大厂（网易、美团、拼多多、快手等）
- ✅ 跳过已充分覆盖的大厂（字节跳动4个）
- ✅ 搜索大厂官方招聘网站

**如果其他过多**（当前45% > 目标20%）：
- ⏭️ 减少其他类型搜索词
- ⏭️ 优先级3搜索轮次减少或跳过
- ⏭️ 提高其他类型的匹配度阈值（≥70分）

---

## Trigger Conditions

### Natural Language Patterns
- "帮我找工作"
- "找岗位"
- "搜索岗位"
- "帮我找合适的岗位"
- "job search"

### DOES NOT Trigger For
- Specific JD analysis (use resume-tailor)
- Career confusion (use career-mentor)

---

## Examples

### GOOD CASE - Minimum 10 NEW Jobs (自动扩展搜索)

**Day 1 (Initial Run):**
```
Load job_history.json... ✓ (0 existing jobs - new database)
Execute WebSearch... ✓ (5 searches)
Find 7 new jobs... ✓
Need 10 jobs, expanding search... ✓ (Round 1)
Execute expanded searches... ✓ (+3 jobs)
Need 10 jobs, expanding search... ✓ (Round 2)
Execute expanded searches... ✓ (+2 jobs)
Total 12 new jobs found... ✓
Update database... ✓ (12 total jobs)
Generate XLSX report... ✓ (12 NEW jobs)

Output:
- result/job_scout_wangbaozhen_20260302_1000.xlsx (12 new jobs)
- job_history.json (created with 12 jobs)
```

**Day 2 (Some NEW, Some EXISTING):**
```
Load job_history.json... ✓ (12 existing jobs)
Execute WebSearch... ✓ (5 searches)
Find 15 jobs... ✓
5 are NEW, 10 are EXISTING (already in database)... ✓
Need 10 jobs, expanding search... ✓ (Round 1)
Execute expanded searches... ✓ (+6 jobs)
Total 11 new jobs found... ✓
Update database... ✓ (23 total jobs)
Generate XLSX report... ✓ (11 NEW jobs)

Output:
- result/job_scout_wangbaozhen_20260303_1500.xlsx (11 new jobs)
- job_history.json (updated with 11 new jobs)
```

**Day 3 (Plenty New Jobs):**
```
Load job_history.json... ✓ (23 existing jobs)
Execute WebSearch... ✓ (5 searches)
Find 18 jobs... ✓
12 are NEW, 6 are EXISTING... ✓
Already have 12+ new jobs, no expansion needed... ✓
Update database... ✓ (35 total jobs)
Generate XLSX report... ✓ (12 NEW jobs)

Output:
- result/job_scout_wangbaozhen_20260304_1000.xlsx (12 new jobs)
- job_history.json (updated with 12 new jobs)
```

---

## Summary

This version is designed for **automated scheduled execution** with:

1. ✅ **Output at least 10 NEW jobs** (不足时自动扩展搜索词继续搜索)
2. ✅ **Quality control** - Filters out low-match jobs automatically
3. ✅ **Smart deduplication** - 只显示新发现的岗位
4. ✅ **XLSX output** - 生成带格式的大字体Excel文件（14号字体）
5. ✅ **Persistent job history database** (JSON)
6. ✅ **GitHub Actions ready** for scheduled runs
7. ✅ **Zero-interruption execution**
8. ✅ **三重质量验证** - 社招 + 公司名精确 + JD真实
9. ✅ **智能优先级分布** - 外企40%、大厂40%、其他20%
10. ✅ **JD真实性保证** - 100%真实JD，绝不使用模板生成

**Key Behavior:**
- Report contains **at least 10 NEW jobs** (不足时自动扩展搜索)
- **Quality threshold**: Match score ≥ 60
- Only **NEW jobs** are shown in report (已推荐的不重复显示)
- Jobs are ranked by priority + match score (highest first)
- **三重验证**: 社招 + 公司名精确 + JD真实
- **目标分布**: 外企40%、大厂40%、其他20%
- **XLSX格式**: 内置14号大字体，方便编辑
- **动态搜索**: 每轮最多扩展5次，使用不同关键词组合

**Quality Control Logic:**
```python
# Step 1: 招聘类型验证（社招优先）
valid_jobs = all_jobs.filter(
    not contains_campus_keywords(title) and  # 不含校招/实习
    not contains_intern_keywords(title)
)

# Step 2: 公司名称精确度验证
valid_jobs = valid_jobs.filter(
    not company.startswith("某") and  # 不以"某"开头
    "轮)" not in company              # 不含融资轮次描述
)

# Step 3: JD真实性验证
valid_jobs = valid_jobs.filter(
    len(jd) >= 100 and                    # JD长度足够
    not contains_template_keywords(jd) and  # 无模板特征
    has_real_jd_indicators(jd)            # 有真实JD特征
)

# Step 4: 匹配度过滤（≥60分）+ 只保留新岗位
new_jobs = valid_jobs.filter(job_id not in job_history)
quality_jobs = new_jobs.filter(match_score >= 60)

# Step 5: 动态扩展搜索（至少10个，按目标比例40%/40%/20%）
max_rounds = 5
while len(quality_jobs) < 10 and max_rounds > 0:
    # 优先扩展外企和大厂搜索
    expand_search_by_priority()
    max_rounds -= 1

# Step 6: 按优先级+匹配度排序
final_results = quality_jobs.sort_by(priority_level, ascending)
final_results = final_results.sort_by(match_score, descending)
```

**拒绝的岗位类型（不会出现在报告中）:**
- ❌ 校招/实习岗位（2026届、校园招聘、实习生）
- ❌ "某出海SaaS公司（A轮）" - 公司名称模糊
- ❌ "某AI/SaaS公司" - 无具体公司名
- ❌ 模板JD（"岗位职责: 1. 负责{title}相关工作"）
- ❌ 无真实JD（"详情请查看投递链接"）
- ❌ 匹配度 < 60 的岗位

**可接受的岗位类型:**
- ✅ 社招岗位（公司名清晰 + 真实JD + NEW标记）
- ✅ 外企岗位（优先级1，目标40%）
- ✅ 大厂岗位（优先级2，目标40%）
- ✅ 其他岗位（优先级3，目标≤20%）
- ✅ 用户可在XLSX中添加自己的标记
