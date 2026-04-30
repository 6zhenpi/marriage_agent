import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Snail.spiders.law_spider import run as run_law
from Snail.spiders.judicial_spider import run as run_judicial
from Snail.spiders.case_spider import run as run_case
from Snail.utils.validator import get_metadata_summary
from Snail.utils.logger import get_logger

logger = get_logger("run_all")


def main():
    logger.info("=" * 70)
    logger.info("  Snail 数据采集系统 - 全量执行")
    logger.info(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    results = {}

    logger.info("\n[1/3] 执行法律条文爬虫...")
    try:
        results["law"] = run_law()
        logger.info(f"法律条文: 成功 {results['law']['saved']}, 失败 {results['law']['failed']}")
    except Exception as e:
        results["law"] = {"saved": 0, "failed": 0, "error": str(e)}
        logger.error(f"法律条文爬虫异常: {e}")

    logger.info("\n[2/3] 执行司法解释爬虫...")
    try:
        results["judicial"] = run_judicial()
        logger.info(f"司法解释: 成功 {results['judicial']['saved']}, 失败 {results['judicial']['failed']}")
    except Exception as e:
        results["judicial"] = {"saved": 0, "failed": 0, "error": str(e)}
        logger.error(f"司法解释爬虫异常: {e}")

    logger.info("\n[3/3] 执行裁判案例采集...")
    try:
        results["case"] = run_case()
        logger.info(f"裁判案例: 成功 {results['case']['saved']}, 失败 {results['case']['failed']}")
    except Exception as e:
        results["case"] = {"saved": 0, "failed": 0, "error": str(e)}
        logger.error(f"裁判案例采集异常: {e}")

    summary = get_metadata_summary()

    logger.info("\n" + "=" * 70)
    logger.info("  采集结果汇总")
    logger.info("=" * 70)
    logger.info(f"  法律条文: {results.get('law', {}).get('saved', 0)} 条")
    logger.info(f"  司法解释: {results.get('judicial', {}).get('saved', 0)} 部")
    logger.info(f"  裁判案例: {results.get('case', {}).get('saved', 0)} 条")
    logger.info(f"  元数据总记录: {summary['total_files']}")
    logger.info(f"  已接受: {summary['accepted']}")
    logger.info(f"  已拒绝: {summary['rejected']}")
    logger.info(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    return results


if __name__ == "__main__":
    main()
