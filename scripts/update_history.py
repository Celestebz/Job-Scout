#!/usr/bin/env python3
"""
Job History Database Updater
更新岗位历史数据库

用途：将新发现的岗位添加到job_history.json中
期望薪资：12-18K
"""

import json
import os
from datetime import datetime

# ===== 配置区域 =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
JOB_HISTORY_FILE = os.path.join(PROJECT_ROOT, 'job_history.json')

# 新发现的岗位（12-18K期望薪资搜索结果）
new_jobs = [
    {
        "id": "lutuo_reddit_community_12-26k",
        "company": "路特创新（A轮）",
        "title": "Reddit/Quora海外社区运营专员",
        "salary": "12-26K",
        "location": "深圳-坂田",
        "first_seen": "2026-03-03",
        "match_score": 90,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "ugreen_overseas_market_12-18k",
        "company": "绿联科技（上市公司）",
        "title": "海外市场经理",
        "salary": "12-18K·14薪",
        "location": "深圳",
        "first_seen": "2026-03-03",
        "match_score": 92,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "youweier_tiktok_12-18k",
        "company": "深圳优维尔科技",
        "title": "海外社媒运营专员（TikTok）",
        "salary": "12-18K·14薪",
        "location": "深圳-西乡",
        "first_seen": "2026-03-03",
        "match_score": 88,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "youshengyan_indie_site_12-18k",
        "company": "有生之颜日化",
        "title": "独立站运营",
        "salary": "12-18K·13薪",
        "location": "深圳-福田区",
        "first_seen": "2026-03-03",
        "match_score": 85,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "baoanal_influencer_15-30k",
        "company": "宝安区某公司",
        "title": "海外红人营销专员",
        "salary": "15-30K",
        "location": "深圳-宝安区",
        "first_seen": "2026-03-03",
        "match_score": 86,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "kesimingde_sales_12-18k",
        "company": "深圳科思明德医疗科技",
        "title": "小语种海外销售",
        "salary": "12-18K·14薪",
        "location": "深圳-龙华区",
        "first_seen": "2026-03-03",
        "match_score": 80,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "mudi_europe_ecom_10-15k",
        "company": "慕迪贸易（C轮）",
        "title": "品牌与市场运营经理（欧洲电商出海）",
        "salary": "10-15K",
        "location": "深圳-南山区",
        "first_seen": "2026-03-03",
        "match_score": 85,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "junzhi_europe_channel_12-20k",
        "company": "上海珺至贸易",
        "title": "欧洲电商出海渠道拓展负责人",
        "salary": "12-20K",
        "location": "深圳-龙岗区",
        "first_seen": "2026-03-03",
        "match_score": 83,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "zelifang_tiktok_management",
        "company": "深圳泽立方信息科技",
        "title": "TikTok运营管培生（2026届）",
        "salary": "面议",
        "location": "深圳",
        "first_seen": "2026-03-03",
        "match_score": 82,
        "apply_url": "校招官网",
        "source": "WebSearch"
    },
    {
        "id": "anker_marketing_spec_6-11k",
        "company": "安克创新",
        "title": "Marketing Specialist（英语专八要求）",
        "salary": "6-11K",
        "location": "深圳-新安",
        "first_seen": "2026-03-03",
        "match_score": 88,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "b_round_smart_hardware_kol_15-25k",
        "company": "某B轮智能硬件公司",
        "title": "社媒与KOL营销专员",
        "salary": "15-25K·15薪",
        "location": "深圳-南山区",
        "first_seen": "2026-03-03",
        "match_score": 87,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
    {
        "id": "social_media_kol_25-45k",
        "company": "某深圳在线社交/媒体公司",
        "title": "海外KOL运营",
        "salary": "25-45K·13薪",
        "location": "深圳",
        "first_seen": "2026-03-03",
        "match_score": 75,
        "apply_url": "猎聘",
        "source": "WebSearch"
    },
]


def main():
    """主函数"""

    # 读取现有的 job_history.json
    with open(JOB_HISTORY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查并只添加新岗位（去重）
    existing_ids = {job['id'] for job in data['jobs']}
    new_unique_jobs = [job for job in new_jobs if job['id'] not in existing_ids]

    # 添加新岗位
    data['jobs'].extend(new_unique_jobs)
    data['total_jobs'] = len(data['jobs'])
    data['last_updated'] = datetime.now().isoformat()
    data['statistics']['total_new_jobs'] = data['statistics'].get('total_new_jobs', 0) + len(new_unique_jobs)

    # 更新平均匹配度
    all_scores = [job['match_score'] for job in data['jobs']]
    data['statistics']['avg_match_score'] = round(sum(all_scores) / len(all_scores), 1)

    # 保存更新后的文件
    with open(JOB_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Job history database updated!")
    print(f"📊 Total jobs in database: {data['total_jobs']}")
    print(f"🆕 New jobs added: {len(new_unique_jobs)}")
    print(f"📈 Average match score: {data['statistics']['avg_match_score']}")
    print(f"📅 Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Salary expectation: 12-18K")


if __name__ == '__main__':
    main()
