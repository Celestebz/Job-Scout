#!/usr/bin/env python3
"""
GitHub Actions Job Scout Executor
使用Claude Agent SDK执行job-scout技能

用途：在GitHub Actions中自动化执行Job Scout技能
依赖：claude-agent-sdk, openpyxl, pandas
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('job_scout_execution.log')
    ]
)
logger = logging.getLogger(__name__)


class JobScoutGitHubActionsExecutor:
    """Job Scout GitHub Actions执行器"""

    def __init__(self):
        """初始化执行器"""
        self.project_root = Path(__file__).parent.parent
        self.result_dir = self.project_root / "result"
        self.logs_dir = self.project_root / "logs"

        # 确保目录存在
        self.result_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # 加载配置
        self.config = self._load_config()

        logger.info(f"✅ JobScoutGitHubActionsExecutor initialized")
        logger.info(f"📁 Project root: {self.project_root}")

    def _load_config(self) -> Dict:
        """加载用户配置"""
        config_file = self.project_root / "users" / "wangbaozhen" / "config.json"

        if not config_file.exists():
            logger.warning(f"⚠️ Config file not found: {config_file}")
            return self._get_default_config()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ Config loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "user_id": "wangbaozhen",
            "search_preferences": {
                "location": "深圳",
                "salary_range": "12-18K",
                "job_types": ["运营", "产品运营", "海外运营"]
            }
        }

    def execute_job_scout_with_claude_code(self) -> Dict[str, Any]:
        """
        使用Claude Code CLI执行job-scout技能

        这是当前最可靠的实现方式，因为：
        1. Claude Agent SDK对slash commands的支持还在开发中
        2. Claude Code CLI已经完全支持/job-scout命令
        3. 在GitHub Actions中安装和运行Claude Code CLI是经过验证的方案
        """
        import subprocess
import timeout_decorator

        logger.info("🚀 Executing job-scout using Claude Code CLI...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_dir / f"daily-run-{timestamp}.log"

        try:
            # 构建命令
            cmd = [
                "claude",
                "/job-scout",
                "帮我找工作"
            ]

            logger.info(f"📝 Command: {' '.join(cmd)}")
            logger.info(f"📝 Log file: {log_file}")

            # 执行命令（45分钟超时）
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=2700  # 45 minutes
            )

            # 保存日志
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Job Scout Execution Log ===\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Exit Code: {result.returncode}\n\n")
                f.write(f"=== STDOUT ===\n{result.stdout}\n\n")
                f.write(f"=== STDERR ===\n{result.stderr}\n")

            if result.returncode == 0:
                logger.info("✅ Job Scout executed successfully")

                # 提取关键信息
                summary = self._extract_summary_from_log(result.stdout)

                return {
                    "success": True,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "log_file": str(log_file),
                    "summary": summary
                }
            else:
                logger.error(f"❌ Job Scout failed with exit code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")

                return {
                    "success": False,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "log_file": str(log_file),
                    "error": f"Command failed with exit code {result.returncode}"
                }

        except subprocess.TimeoutExpired:
            logger.error("⏰ Job Scout timed out after 45 minutes")
            return {
                "success": False,
                "error": "Execution timeout after 45 minutes",
                "log_file": str(log_file)
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "log_file": str(log_file) if log_file.exists() else None
            }

    def _extract_summary_from_log(self, log_text: str) -> Dict:
        """从日志中提取关键信息"""
        summary = {
            "new_jobs": 0,
            "average_score": 0,
            "priority_distribution": {},
            "report_file": None
        }

        lines = log_text.split('\n')
        for line in lines:
            if "新发现岗位" in line:
                try:
                    summary["new_jobs"] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif "平均匹配度" in line:
                try:
                    summary["average_score"] = float(''.join(filter(lambda x: x.isdigit() or x == '.', line)))
                except:
                    pass
            elif "报告已生成" in line and ".xlsx" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    summary["report_file"] = parts[-1].strip()

        return summary

    def generate_summary_report(self, execution_result: Dict[str, Any]) -> str:
        """生成执行摘要报告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = []
        report.append("=" * 60)
        report.append("Job Scout GitHub Actions执行报告")
        report.append("=" * 60)
        report.append(f"执行时间: {timestamp}")
        report.append(f"执行状态: {'✅ 成功' if execution_result['success'] else '❌ 失败'}")
        report.append("")

        if execution_result['success']:
            summary = execution_result.get('summary', {})
            report.append("📊 执行摘要:")
            report.append(f"  - 新发现岗位: {summary.get('new_jobs', 'N/A')} 个")
            report.append(f"  - 平均匹配度: {summary.get('average_score', 'N/A')}")
            report.append(f"  - 报告文件: {summary.get('report_file', 'N/A')}")
            report.append("")
            report.append(f"📝 完整日志: {execution_result.get('log_file', 'N/A')}")
        else:
            report.append("❌ 错误信息:")
            report.append(f"  {execution_result.get('error', 'Unknown error')}")

        report.append("=" * 60)

        return "\n".join(report)

    def save_execution_result(self, execution_result: Dict[str, Any]):
        """保存执行结果到JSON文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.logs_dir / f"execution-result-{timestamp}.json"

        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(execution_result, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Execution result saved to {result_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save execution result: {e}")

    def run(self) -> int:
        """执行Job Scout任务"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Job Scout GitHub Actions Execution")
        logger.info("=" * 60)

        # 执行job-scout
        execution_result = self.execute_job_scout_with_claude_code()

        # 保存执行结果
        self.save_execution_result(execution_result)

        # 生成摘要报告
        summary_report = self.generate_summary_report(execution_result)
        print("\n" + summary_report)

        # 保存摘要到文件
        summary_file = self.logs_dir / "last-run-summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)

        logger.info("=" * 60)
        logger.info("🏁 Job Scout GitHub Actions Execution Completed")
        logger.info("=" * 60)

        return 0 if execution_result['success'] else 1


def main():
    """主函数"""
    executor = JobScoutGitHubActionsExecutor()
    exit_code = executor.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
