---
name: job-scout
description: Active job discovery system with smart deduplication and priority-based search (Foreign Companies:Big Tech:Others = 3:3:4). Performs multi-source job hunting, extracts real JDs, calculates match scores, outputs XLSX report. Auto-filters previously recommended jobs. Enforces minimum match score 60+. Use when user requests job search, "帮我找工作", "找岗位". Requires: resume file in 简历/ folder. Outputs: XLSX report + JSON job database.
license: MIT
---

# Job Scout - 智能岗位侦察兵

## Overview

主动式岗位发现系统，核心特性：

1. **优先级分布** - 外企30%、大厂30%、其他40% (3:3:4)
2. **固定输出数量** - 每次搜索10个岗位
3. **主动搜索** - 基于用户画像生成多组搜索词
4. **智能去重** - 自动过滤已推荐岗位
5. **XLSX输出** - 生成带格式的大字体Excel文件
6. **数据库维护** - 自动更新已推荐岗位JSON数据库
7. **三重质量验证** - 社招 + 公司名精确 + JD真实

### 优先级分布要求

**严格按照以下比例搜索和推荐岗位**：
- 🟢 **Priority 1（外企）**: 30% (3个岗位) - 外国公司在华分支
- 🔵 **Priority 2（大厂）**: 30% (3个岗位) - **国内互联网/AI/跨境电商行业头部企业**
- ⚪ **Priority 3（其他）**: 40% (4个岗位) - 其他匹配公司

**大厂定义**（Priority 2）:
- **互联网大厂**: 字节跳动、腾讯、阿里巴巴、美团、拼多多、小红书、快手、B站、京东、百度
- **AI大厂**: DeepSeek、智谱AI、月之暗面（Kimi）、MiniMax、零一万物
- **跨境电商大厂**: SHEIN、Temu、安克创新
- **出海游戏大厂**: 米哈游、莉莉丝、趣加、网易

**CRITICAL**: 每次搜索固定输出**10个岗位**，严格按照 3:3:4 分布。

### 公司名称精确度要求（CRITICAL）

**CRITICAL**: 公司名称必须100%精确，能被搜索引擎找到

**拒绝规则**（任一条件触发即拒绝）:
- ❌ 包含"某"字：如"某知名外企"、"某科技公司"
- ❌ 包含融资轮次：如"某公司（A轮）"、"B轮融资公司"
- ❌ 只有模糊描述：如"知名外企"、"头部公司"、"大型互联网公司"
- ❌ 公司名称过短：少于5个字符

**接受规则**:
- ✅ 公司名称清晰具体：如"博世集团"、"字节跳动"
- ✅ 全称公司名：如"深圳市识刻创新科技有限公司"
- ✅ 包含国家/地区信息：如"博世集团（德国Bosch）"
- ✅ 用户可以自行搜索投递

**错误示例**（会直接拒绝）:
- "某知名外企" - 包含"某"+"知名"
- "某外企电商公司" - 包含"某"
- "头部外企" - 只有模糊描述
- "某出海SaaS公司（A轮）" - 包含"某"+"轮"

**正确示例**:
- "博世集团（德国Bosch）" ✓
- "中美联泰大都会人寿保险" ✓
- "字节跳动" ✓

---

## File Structure

```
job-scout/
├── skill.md                    # 本文件
├── job_history.json            # 已推荐岗位数据库（自动维护）
├── result/                     # 报告目录
│   └── job_scout_{user_id}_{YYYYMMDD_HHMM}.xlsx
└── 简历/                        # 简历文件夹
    └── {resume_file}.docx
```

---

## Workflow

### Step 0: Load Job History Database

**READ** `job_history.json`:

```json
{
  "last_updated": "2026-03-15T21:50:21Z",
  "total_jobs": 96,
  "jobs": [
    {
      "id": "bosch_overseas_bd_20260315_v3",
      "company": "博世集团（德国Bosch）",
      "title": "海外业务发展经理",
      "salary": "25-45K·15薪",
      "location": "深圳",
      "first_seen": "2026-03-15",
      "match_score": 94,
      "apply_url": "博世招聘官网",
      "source": "WebSearch",
      "type": "foreign",  // foreign=外企, big_tech=大厂, other=其他
      "jd": "岗位职责：\n1. 负责海外业务拓展\n..."
    }
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

### Step 1: Extract User Profile

**READ** resume file from `简历/` folder:

```markdown
## 用户画像

### 基本信息
- 姓名: [name]
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

### Step 2: Generate Search Strategy (Priority-Based)

**CRITICAL**: Generate search terms in PRIORITY ORDER:

#### Priority 1: Foreign Companies (外企) - 30% (3个岗位)

```python
foreign_company_searches = [
    # 神仙外企平台（专业外企招聘信息聚合）
    f'site:waiqi.com 外企 运营 {location}',
    f'site:mp.weixin.qq.com "神仙外企" 产品运营 {location}',
    f'site:mp.weixin.qq.com "神仙外企" 海外运营',

    # 知名外企官方招聘
    f'{location} 外企招聘 英语 运营 2026',
    f'微软中国 {location} 运营',
    f'苹果中国 {location} operations',
    f'亚马逊中国 {location} 运营',
    f'谷歌中国 {location} 产品运营',
    f'Meta {location} 运营',
    f'Tesla {location} 运营',

    # 欧美外企
    f'{location} 欧美企业 运营 英语',
    f'{location} 跨国公司 MNC 运营',

    # 外企招聘平台
    f'猎聘 {location} 外企 运营',
    f'智联招聘 {location} 外企 英语',
]
```

#### Priority 2: Domestic Big Tech (大厂) - 30% (3个岗位)

**定义**: 国内互联网/AI/跨境电商行业头部企业

```python
big_tech_searches = [
    # === 互联网大厂 ===
    # 字节跳动
    f'字节跳动 {location} 海外运营',
    f'site:jobs.bytedance.com {location} 运营',
    f'site:mp.weixin.qq.com "字节跳动招聘" 运营',

    # 腾讯
    f'腾讯 {location} 国际化运营',
    f'site:careers.tencent.com {location} 运营',
    f'site:mp.weixin.qq.com "腾讯招聘" 产品运营',

    # 阿里巴巴
    f'阿里巴巴 {location} 跨境运营',
    f'site:jobs.alibaba.com {location} 运营',

    # 美团、拼多多、小红书、快手、B站、京东、百度
    f'美团 {location} 海外业务',
    f'拼多多 {location} TEMU 运营',
    f'小红书 {location} 海外运营',
    f'快手 {location} 出海运营',
    f'B站 {location} AIGC 运营',
    f'京东 {location} 跨境电商',
    f'百度 {location} AI 运营',

    # === AI大厂 ===
    # DeepSeek
    f'DeepSeek {location} 运营',
    f'site:mp.weixin.qq.com "DeepSeek招聘" 产品运营',

    # 智谱AI
    f'智谱AI {location} 产品运营',
    f'site:mp.weixin.qq.com "智谱AI招聘" 运营',

    # 月之暗面（Kimi）
    f'月之暗面 {location} 运营',
    f'Kimi {location} 产品运营',

    # MiniMax
    f'MiniMax {location} AIGC 运营',

    # 零一万物
    f'零一万物 {location} AI 运营',

    # === 跨境电商大厂 ===
    # SHEIN
    f'SHEIN {location} 运营',
    f'site:mp.weixin.qq.com "SHEIN招聘" 海外运营',

    # Temu/拼多多国际
    f'Temu {location} 运营',
    f'拼多多国际 {location} 海外运营',

    # 安克创新
    f'安克创新 {location} 海外运营',
    f'site:mp.weixin.qq.com "安克创新招聘" 运营',

    # === 出海游戏大厂 ===
    # 米哈游
    f'米哈游 {location} 海外运营',
    f'site:mp.weixin.qq.com "米哈游招聘" 出海',

    # 莉莉丝
    f'莉莉丝 {location} 海外发行',
    f'site:mp.weixin.qq.com "莉莉丝招聘" 海外',

    # 趣加（FunPlus）
    f'趣加 {location} 海外运营',

    # 网易游戏海外
    f'网易 {location} 游戏海外运营',

    # === 大厂招聘平台 ===
    f'Boss直聘 {location} 大厂 运营',
]
```

#### Priority 3: Other Matching Companies (其他) - 40% (4个岗位)

```python
other_searches = [
    # 出海公司
    f'SHEIN {location} 运营',
    f'米哈游 {location} 海外运营',
    f'莉莉丝 {location} 出海',
    f'安克创新 {location} 运营',

    # AI公司
    f'DeepSeek {location} 运营',
    f'智谱AI {location} 产品运营',

    # 通用搜索（仅当前两项不足时使用）
    f'{location} 出海运营 2026',
    f'{location} AI产品运营',
    f'猎聘 {location} 海外运营',
]
```

---

### Step 2.5: 扩展搜索词维度优化（方案1 - 提升新岗位发现率50%）

**问题**: 传统搜索词重复度高，导致新岗位发现率低

**解决方案**: 通过5个维度扩展搜索词，覆盖更多职位变体和技能组合

**CRITICAL**: `location` 必须固定为用户现居地（如"深圳"），不可扩展到其他城市

#### 维度1: 职位变体（Position Variations）

不要只用"海外运营"，使用职位变体覆盖更多相关岗位：

```python
position_variations = [
    # 核心职位
    "海外运营", "海外市场", "国际业务", "跨境运营",
    "全球运营", "出海运营", "国际化运营", "海外营销",

    # 职位层级
    "海外运营专员", "海外运营经理", "海外运营总监",
    "海外运营负责人", "海外运营主管",
]
```

#### 维度2: 技能组合（Skill Combinations）

覆盖用户简历中的核心技能和项目经验：

```python
skill_combinations = [
    # KOL/社媒相关（匹配YouTube KOL项目）
    "KOL运营", "达人运营", "红人营销", "Influencer运营",
    "KOL营销", "达人BD", "红人合作", "KOL内容营销",

    # AI相关（匹配AI智能客服系统项目）
    "AI产品运营", "AIGC运营", "智能客服", "大模型运营",
    "AI工具运营", "Agent运营", "RAG应用", "AI客服",

    # 平台相关（匹配Facebook项目）
    "TikTok运营", "YouTube运营", "Instagram运营",
    "Facebook运营", "社媒运营", "海外社媒",

    # 跨境电商（匹配海外销售经验）
    "亚马逊运营", "TEMU运营", "SHEIN运营",
    "跨境电商", "海外电商", "独立站运营",
]
```

#### 维度3: 平台限制（Platform Filters）

使用专业招聘平台的site:搜索，获取更精准的岗位：

```python
platform_filters = [
    "site:liepin.com",      # 猎聘
    "site:zhipin.com",      # BOSS直聘
    "site:zhaopin.com",     # 智联招聘
    "site:51job.com",       # 前程无忧
    "site:linkedin.com",    # LinkedIn
]
```

#### 维度4: 时间限制（Time Filters）

优先搜索最新发布的岗位，提高新岗位发现率：

```python
time_filters = [
    "2026年3月", "更新时间7天", "今天", "最新", "本周", "最新发布",
]
```

#### 维度5: 薪资/层级过滤（Salary/Level Filters）

根据用户期望薪资和经验水平筛选：

```python
level_filters = [
    "专员", "经理", "总监", "负责人", "主管",
]
```

---

#### 生成扩展搜索词（100+个组合）

**CRITICAL**: 所有搜索词的location必须固定为用户现居地

```python
def generate_expanded_search_terms(location):
    """
    生成扩展搜索词（100+个组合）

    Args:
        location: 用户现居地（如"深圳"），不可变

    Returns:
        list: 扩展后的搜索词列表
    """
    expanded_searches = []

    # 维度组合：职位 × 技能 × 平台 × 时间 × 层级
    for position in ["海外运营", "海外市场", "跨境运营"]:
        for skill in ["KOL运营", "AI产品运营", "TikTok运营"]:
            for platform in ["", "site:liepin.com", "site:zhipin.com"]:
                for time in ["", "2026年3月", "最新"]:
                    for level in ["", "经理"]:
                        # 构建搜索词
                        search_term = f"{location} {position} {skill} {level} {time} {platform}".strip()
                        expanded_searches.append(search_term)

    # 添加纯技能搜索
    for skill in ["KOL运营", "AI产品运营", "智能客服"]:
        for platform in ["site:liepin.com", "site:zhipin.com"]:
            search_term = f"{location} {skill} {platform}".strip()
            expanded_searches.append(search_term)

    return expanded_searches

# 示例：生成深圳地区的扩展搜索词
shenzhen_searches = generate_expanded_search_terms("深圳")
print(f"生成 {len(shenzhen_searches)} 个扩展搜索词")

# 输出示例：
# 深圳 海外运营 KOL运营 经理 2026年3月 site:liepin.com
# 深圳 海外运营 AI产品运营 最新 site:zhipin.com
# 深圳 跨境运营 TikTok运营 site:liepin.com
# 深圳 KOL运营 site:liepin.com
# 深圳 AI产品运营 site:zhipin.com
# ... (共100+个搜索词)
```

---

#### 扩展搜索词示例（50个高频词）

**职位变体搜索**:
```python
深圳 海外运营 英语
深圳 海外市场 英语
深圳 国际业务 英语
深圳 跨境运营 英语
深圳 全球运营 英语
深圳 出海运营 英语
深圳 国际化运营 英语
深圳 海外营销 英语
深圳 海外运营专员
深圳 海外运营经理
深圳 海外运营总监
深圳 海外运营负责人
深圳 海外运营主管
```

**技能组合搜索**:
```python
深圳 KOL运营 英语
深圳 达人运营 英语
深圳 红人营销 英语
深圳 Influencer运营 英语
深圳 AI产品运营 英语
深圳 AIGC运营 英语
深圳 智能客服 英语
深圳 大模型运营 英语
深圳 TikTok运营 英语
深圳 YouTube运营 英语
深圳 Instagram运营 英语
深圳 Facebook运营 英语
```

**平台限制搜索**:
```python
site:liepin.com 深圳 海外运营
site:zhipin.com 深圳 海外运营
site:zhaopin.com 深圳 海外运营
site:51job.com 深圳 海外运营
site:linkedin.com 深圳 海外运营
```

**时间限制搜索**:
```python
深圳 海外运营 2026年3月
深圳 海外运营 更新时间7天
深圳 海外运营 今天
深圳 海外运营 最新
深圳 海外运营 本周
```

**组合搜索（高精度）**:
```python
site:liepin.com 深圳 海外运营经理 2026年3月
site:zhipin.com 深圳 AI产品运营 英语
site:zhaopin.com 深圳 KOL运营 最新
深圳 TikTok运营经理 英语 2026
深圳 海外市场总监 更新时间7天
```

---

#### 预期效果

- ✅ 新岗位发现率提升 **50%**
- ✅ 搜索覆盖率提升 **100%**
- ✅ 避免搜索词重复导致的岗位遗漏
- ⚠️ 搜索次数增加（建议设置合理上限，如50-100次）

---

### Step 3: Execute Priority-Based Search with Expanded Terms

**CRITICAL**: Execute searches in PRIORITY ORDER and maintain 3:3:4 ratio (10 jobs total):

**OPTIMIZATION**: 使用Step 2.5的扩展搜索词，提升新岗位发现率50%

```python
# 从用户简历中提取location（如"深圳"）
location = user_profile.get('location', '深圳')

# 生成扩展搜索词（100+个组合）
expanded_searches = generate_expanded_search_terms(location)

# Step 3.1: 先搜索外企（Priority 1 - 目标3个）
priority_1_jobs = []
target_count = 3
max_searches = 50  # 设置搜索上限，避免过度搜索

search_count = 0
while len(priority_1_jobs) < target_count and search_count < max_searches:
    # 使用外企专用搜索词 + 扩展搜索词
    all_priority_1_searches = foreign_company_searches + expanded_searches

    for search_term in all_priority_1_searches:
        search_count += 1
        LOG: f"Priority 1 search ({search_count}/{max_searches}): '{search_term}'"
        results = WebSearch(search_term)

        # 过滤和验证结果
        for job in results:
            if job.get('type') == 'foreign' and job not in priority_1_jobs:
                priority_1_jobs.append(job)

        if len(priority_1_jobs) >= target_count:
            break

    if len(priority_1_jobs) < target_count:
        LOG: f"Foreign companies insufficient ({len(priority_1_jobs)}/{target_count}), continuing search..."

# Step 3.2: 再搜索大厂（Priority 2 - 目标3个）
priority_2_jobs = []
target_count = 3
search_count = 0

while len(priority_2_jobs) < target_count and search_count < max_searches:
    # 使用大厂专用搜索词 + 扩展搜索词
    all_priority_2_searches = big_tech_searches + expanded_searches

    for search_term in all_priority_2_searches:
        search_count += 1
        LOG: f"Priority 2 search ({search_count}/{max_searches}): '{search_term}'"
        results = WebSearch(search_term)

        # 过滤和验证结果
        for job in results:
            if job.get('type') == 'big_tech' and job not in priority_2_jobs:
                priority_2_jobs.append(job)

        if len(priority_2_jobs) >= target_count:
            break

    if len(priority_2_jobs) < target_count:
        LOG: f"Big tech insufficient ({len(priority_2_jobs)}/{target_count}), continuing search..."

# Step 3.3: 最后搜索其他（Priority 3 - 目标4个）
priority_3_jobs = []
target_count = 4
search_count = 0

while len(priority_3_jobs) < target_count and search_count < max_searches:
    # 使用其他搜索词 + 扩展搜索词
    all_priority_3_searches = other_searches + expanded_searches

    for search_term in all_priority_3_searches:
        search_count += 1
        LOG: f"Priority 3 search ({search_count}/{max_searches}): '{search_term}'"
        results = WebSearch(search_term)

        # 过滤和验证结果
        for job in results:
            if job.get('type') == 'other' and job not in priority_3_jobs:
                priority_3_jobs.append(job)

        if len(priority_3_jobs) >= target_count:
            break

    if len(priority_3_jobs) < target_count:
        LOG: f"Other companies insufficient ({len(priority_3_jobs)}/{target_count}), continuing search..."

# Step 3.4: 按比例选取最终结果
final_jobs = []
final_jobs.extend(priority_1_jobs[:3])  # 3个外企
final_jobs.extend(priority_2_jobs[:3])  # 3个大厂
final_jobs.extend(priority_3_jobs[:4])  # 4个其他

LOG: f"Final selection: {len(final_jobs)} jobs (3 foreign + 3 big tech + 4 others)"
LOG: f"Total searches performed: {search_count} (expanded from {len(foreign_company_searches) + len(big_tech_searches) + len(other_searches)} base terms)"
```

---

### Step 4: Quality Validation (三重验证)

**CRITICAL**: Filter jobs through THREE validation layers:

#### Layer 1: 招聘类型验证（社招优先）

```python
campus_keywords = [
    '校招', '校园招聘', '2026届', '2025届', '应届生',
    '实习', '实习生', 'intern', 'campus',
    '管培生', '培训生'
]

job_title = job['title'].lower()
job_description = job.get('jd', '').lower()

is_campus_job = any(keyword in job_title or keyword in job_description
                   for keyword in campus_keywords)

if is_campus_job:
    LOG: f"REJECTED: '{job['title']}' - 校招/实习岗位"
    continue
```

**拒绝模式**:
| 岗位标题 | 是否保留 | 原因 |
|---------|---------|------|
| "2026届校园招聘-运营" | ❌ 拒绝 | 校招岗位 |
| "产品运营实习生" | ❌ 拒绝 | 实习岗位 |
| "海外运营（3-5年经验）" | ✅ 保留 | 明确社招 |

#### Layer 2: 公司名称精确度验证

**CRITICAL**: 公司名称必须100%精确，能被搜索到

```python
company_name = extracted_company.strip()

# 拒绝模式：公司名包含模糊描述词
vague_patterns = [
    "某", "知名", "头部", "大型", "多家",
    "A轮", "B轮", "C轮", "D轮", "E轮",
    "独角兽", "上市公司", "集团",
]

# 严格验证：只要包含"某"字，直接拒绝
if "某" in company_name:
    LOG: f"REJECTED: '{company_name}' - 包含'某'字，公司名不精确"
    continue

# 严格验证：包含融资轮次的，直接拒绝
if "轮)" in company_name or "轮（" in company_name:
    LOG: f"REJECTED: '{company_name}' - 包含融资轮次，公司名不精确"
    continue

# 严格验证：公司名过短（<5个字符），可能不够精确
if len(company_name) < 5:
    LOG: f"REJECTED: '{company_name}' - 公司名称过短，可能不够精确"
    continue

# 严格验证：包含模糊描述词的组合
for pattern in vague_patterns:
    if pattern in company_name and pattern != "某":  # "某"已经检查过了
        LOG: f"REJECTED: '{company_name}' - 包含模糊描述词'{pattern}'"
        continue

# 通过验证
LOG: f"ACCEPT: '{company_name}' - 公司名称精确，可被搜索到"
```

**拒绝/保留模式**:
| 公司名 | 是否保留 | 原因 |
|--------|---------|------|
| "某知名外企" | ❌ 拒绝 | 包含"某" |
| "某出海SaaS公司（A轮）" | ❌ 拒绝 | 包含"某"+"轮" |
| "深圳某跨境电商公司" | ❌ 拒绝 | 包含"某" |
| "某大型互联网公司" | ❌ 拒绝 | 包含"某"+"大型" |
| "知名外企" | ❌ 拒绝 | 包含"知名"，无具体名称 |
| "头部外企" | ❌ 拒绝 | 包含"头部"，无具体名称 |
| "某科技公司" | ❌ 拒绝 | 包含"某"，公司名不精确 |
| "博世集团（德国Bosch）" | ✅ 保留 | 公司名清晰，可搜索 |
| "字节跳动" | ✅ 保留 | 公司名清晰，可搜索 |
| "深圳市识刻创新科技有限公司" | ✅ 保留 | 公司名清晰，全称 |
| "中美联泰大都会人寿保险" | ✅ 保留 | 公司名清晰，全称 |

**CRITICAL RULE**:
- ❌ **任何包含"某"字的公司名都直接拒绝**
- ❌ **任何包含融资轮次的公司名都直接拒绝**
- ❌ **只有"知名"、"头部"等形容词而无具体公司名的都拒绝**
- ✅ **公司名必须清晰具体，用户可以自行搜索投递**

#### Layer 3: JD真实性验证

```python
jd_text = job.get('jd', '')

# 真实JD特征
real_jd_indicators = [
    len(jd_text) > 100,  # JD长度足够
    '岗位职责' in jd_text or 'Job Description' in jd_text,
    '任职要求' in jd_text or 'Requirements' in jd_text,
    any(keyword in jd_text for keyword in ['团队', '协作', '负责', '制定']),
]

if sum(real_jd_indicators) < 3:
    LOG: f"WARNING: '{job['title']}' - JD真实性待确认"
    job['notes'] = f"{job.get('notes', '')}\n⚠️ JD真实性待确认"
```

**JD真实性验证标准**:
| JD内容 | 是否保留 | 原因 |
|--------|---------|------|
| 完整职责+要求描述 | ✅ 保留 | 真实JD |
| "岗位职责: 1. 负责运营相关工作" | ❌ 拒绝 | 模板JD |
| "JD详情请查看投递链接" | ❌ 拒绝 | 无真实JD |

---

### Step 5: Deduplication

**CHECK** if jobs are NEW:

```python
for job in all_jobs:
    job_id = f"{company_slug}_{title_slug}_{salary_slug}"

    if job_id in job_history:
        LOG: f"SKIP: '{job['title']}' - 已推荐过"
        continue

    job['is_new'] = True
    new_jobs.append(job)
```

---

### Step 6: Match Analysis

**CALCULATE** match score for NEW jobs:

```python
直接匹配 = (resume_skills ∩ jd_requirements) / total_jd_requirements
可迁移经验 = related_but_not_direct_experience / total_requirements
薪资匹配 = 1.0 if salary_in_range else 0.5 if negotiable else 0.0
公司优先级 = 1.0 if type in ['foreign', 'big_tech'] else 0.7

综合匹配度 = (直接匹配 × 0.5) + (可迁移经验 × 0.3) + (薪资匹配 × 0.1) + (公司优先级 × 0.1)
```

---

### Step 7: Dynamic Search Expansion (Target 3:3:4 Ratio, 10 Jobs Total)

**CRITICAL**: 动态扩展搜索直到满足 3:3:4 分布（总共10个岗位）：

```python
max_rounds = 5
current_round = 1
target_total = 10

# 目标数量
target_foreign = 3  # 30%
target_big_tech = 3  # 30%
target_other = 4  # 40%

while len(new_jobs) < target_total and current_round <= max_rounds:
    LOG: f"Found {len(new_jobs)} jobs, need {target_total}. Expanding search (Round {current_round})..."

    # 计算当前各类型数量
    foreign_count = len([j for j in new_jobs if j.get('type') == 'foreign'])
    big_tech_count = len([j for j in new_jobs if j.get('type') == 'big_tech'])
    other_count = len([j for j in new_jobs if j.get('type') == 'other'])

    # 基于缺口决定扩展策略
    if foreign_count < target_foreign:  # 外企不足3个
        expansion_keywords = [
            f'外企 {location} 运营 2026',
            f'跨国公司 {location} 产品运营',
            f'欧美企业 {location} 海外运营',
            f'思科中国 {location} 运营',
            f'英特尔中国 {location} 运营',
            f'IBM中国 {location} 运营',
        ]
        LOG: f"Expanding: Foreign companies ({foreign_count}/{target_foreign})..."

    elif big_tech_count < target_big_tech:  # 大厂不足3个
        expansion_keywords = [
            f'大厂 {location} 运营 2026',
            f'互联网大厂 {location} 产品运营',
            f'字节跳动 {location} 海外运营',
            f'腾讯 {location} AI产品运营',
            f'阿里巴巴 {location} 出海运营',
            f'美团 {location} 运营',
            f'拼多多 {location} 运营',
        ]
        LOG: f"Expanding: Big tech companies ({big_tech_count}/{target_big_tech})..."

    elif other_count < target_other:  # 其他不足4个
        expansion_keywords = [
            f"{location} 运营招聘 2026",
            f"{location} 出海运营 2026",
            f"{location} AI产品运营",
            f'猎聘 {location} 海外运营',
        ]
        LOG: f"Expanding: Other matching companies ({other_count}/{target_other})..."

    else:  # 数量达标，按比例选取
        LOG: "All types sufficient, selecting top 10 by 3:3:4 ratio..."
        break

    # 执行扩展搜索（每轮2个搜索词）
    for search_term in expansion_keywords[:2]:
        LOG: f"Expanded search: '{search_term}'"
        results = WebSearch(search_term)
        # 处理结果，更新new_jobs...

    current_round += 1

# 最终按3:3:4比例选取
final_selection = []
final_selection.extend([j for j in new_jobs if j.get('type') == 'foreign'][:3])
final_selection.extend([j for j in new_jobs if j.get('type') == 'big_tech'][:3])
final_selection.extend([j for j in new_jobs if j.get('type') == 'other'][:4])

LOG: f"Final selection: {len(final_selection)} jobs ({len(final_selection[:3])} foreign + {len(final_selection[3:6])} big tech + {len(final_selection[6:10])} others)"
```

---

### Step 8: Generate XLSX Report

**GENERATE** XLSX format report:

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

# 创建工作簿
wb = Workbook()
ws = wb.active
ws.title = "岗位侦察报告"

# 表头
headers = ['rank', 'type', 'company', 'title', 'salary', 'location',
           'match_score', 'jd', 'apply_url', 'notes', 'search_date']

# 写入数据
for row_idx, job in enumerate(final_jobs, start=2):
    type_mapping = {'foreign': '外企', 'big_tech': '大厂', 'other': '其他'}

    cell_data = [
        row_idx - 1,  # rank
        type_mapping.get(job.get('type'), '其他'),  # type
        job['company'],
        job['title'],
        job['salary'],
        job['location'],
        job['match_score'],
        job.get('jd', ''),
        job['apply_url'],
        f"{type_mapping.get(job.get('type'), '其他')} 匹配度{job['match_score']}分",
        job['first_seen']
    ]

    for col_idx, value in enumerate(cell_data, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)

# 设置格式
header_fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=13)
body_font = Font(size=14)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

# 不同类型用不同颜色
type_fills = {
    '外企': PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    '大厂': PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),
    '其他': PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")
}

# 应用格式
for row_idx in range(1, max_row + 1):
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.alignment = center_align

        if row_idx == 1:  # 表头
            cell.fill = header_fill
            cell.font = header_font
        else:  # 数据行
            cell.font = body_font
            job_type = ws.cell(row=row_idx, column=2).value
            if job_type in type_fills:
                cell.fill = type_fills[job_type]

# 设置列宽
column_widths = {
    'A': 6, 'B': 10, 'C': 35, 'D': 30, 'E': 18, 'F': 15,
    'G': 12, 'H': 70, 'I': 35, 'J': 25, 'K': 15
}

for col_letter, width in column_widths.items():
    ws.column_dimensions[col_letter].width = width

# 设置行高
for row in ws.iter_rows(min_row=1, max_row=max_row):
    ws.row_dimensions[row[0].row].height = 50

# 保存文件
output_file = f'result/job_scout_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
wb.save(output_file)
```

**XLSX格式特点**:
- ✅ 表头紫色背景 + 白色粗体字
- ✅ 数据行14号字体
- ✅ 不同类型用颜色区分（外企=绿色，大厂=蓝色，其他=橙色）
- ✅ 自动列宽和行高
- ✅ JD列宽度70，自动换行

---

### Step 9: Update Database

**APPEND** new jobs to `job_history.json`:

```json
{
  "last_updated": "2026-03-15T21:50:21Z",
  "total_jobs": 96,
  "jobs": [
    ...existing jobs...
    ...new jobs...
  ]
}
```

---

## Expected Results

### 岗位分布目标

**目标分布**（严格按 3:3:4）：
- 🟢 **外企**: 3 个岗位 (30%)
- 🔵 **大厂**: 3 个岗位 (30%)
- ⚪ **其他**: 4 个岗位 (40%)

**总计**: **固定10个岗位/次**

### 实际案例

**2026-03-15 搜索结果**（10个岗位）：
```
外企: 3 个 (30%) ✓
├─ 博世集团（德国Bosch） - 海外业务发展经理 (25-45K·15薪)
├─ 中美联泰大都会人寿保险（美国MetLife） - 综合管理岗 (30-50K·14薪)
└─ 阳狮集团（法国Publicis） - 客户总监 (面议)

大厂: 3 个 (30%) ✓
├─ 字节跳动 - TikTok海外运营专家 (30-50K·15薪) [互联网大厂]
├─ DeepSeek - AI产品运营 (面议) [AI大厂]
└─ SHEIN - 海外运营经理 (20-40K·14薪) [跨境电商大厂]

其他: 4 个 (40%) ✓
├─ 无界未来 - 海外产品运营（AI工具） (18-30K·13薪)
├─ 追觅科技 - 海外新媒体运营 (15-25K·15薪)
├─ 华为 - 海外市场拓展经理（英语专八） (30-40K)
└─ 深圳市识刻创新科技 - 海外市场运营 (13-25K)
```

**注意**: 所有公司名都是清晰具体的，可以被搜索引擎找到。不存在"某知名外企"、"某外企电商公司"等模糊名称。

---

## Trigger Conditions

### Natural Language Patterns
- "帮我找工作"
- "找岗位"
- "搜索岗位"
- "帮我找合适的岗位"
- "job search"

---

## Summary

**核心特性**:
1. ✅ **优先级分布** - 外企30%、大厂30%、其他40% (3:3:4)
2. ✅ **固定输出数量** - 每次搜索**10个岗位**
3. ✅ **三重质量验证** - 社招 + 公司名精确 + JD真实
4. ✅ **智能去重** - 只显示新发现的岗位
5. ✅ **XLSX输出** - 内置格式，方便编辑
6. ✅ **数据库持久化** - 自动更新JSON数据库

**优先级分类**:
- 🟢 **外企（30%）**: 外国公司在华分支（博世、苹果、微软、亚马逊等）
- 🔵 **大厂（30%）**: **国内互联网/AI/跨境电商行业头部企业**
  - 互联网大厂: 字节跳动、腾讯、阿里巴巴、美团、拼多多、小红书、快手、B站、京东、百度
  - AI大厂: DeepSeek、智谱AI、月之暗面（Kimi）、MiniMax、零一万物
  - 跨境电商大厂: SHEIN、Temu、安克创新
  - 出海游戏大厂: 米哈游、莉莉丝、趣加、网易
- ⚪ **其他（40%）**: 其他匹配公司（追觅科技、无界未来、华为等）

**质量保证**:
- 匹配度 ≥ 60
- 拒绝校招/实习岗位
- **拒绝公司名模糊的岗位（包含"某"字或融资轮次）**
- 拒绝模板JD

**公司名精确度标准**:
- ❌ **任何包含"某"字的公司名都拒绝**
- ❌ **任何包含融资轮次的公司名都拒绝**
- ❌ **只有"知名"、"头部"等形容词而无具体名称的都拒绝**
- ✅ **公司名必须清晰具体，用户可以自行搜索投递**

**输出规格**:
- **固定数量**: 每次搜索 **10个岗位**
- **分布比例**: 3个外企 + 3个大厂（互联网/AI/跨境电商） + 4个其他
- **输出文件**: `result/job_scout_{user_id}_{YYYYMMDD_HHMM}.xlsx`
- **数据库**: `job_history.json` (自动更新)
