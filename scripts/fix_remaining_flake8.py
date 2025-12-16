#!/usr/bin/env python3
"""
修复剩余的flake8问题
"""
from pathlib import Path
import re


def fix_unused_imports():
    """移除未使用的导入"""
    fixes = {
        "app/repositories/ai_conversation_repo.py": [("from typing import List\n", "")],
        "app/repositories/event_repo.py": [("from sqlalchemy import or_\n", "")],
        "app/repositories/trade_repo.py": [("from sqlalchemy import or_\n", "")],
        "app/services/ai/daily_review_service.py": [("from datetime import date\n", "")],
        "app/services/ai/single_analysis_service.py": [("from datetime import datetime\n", "")],
        "app/services/event/event_update_service.py": [("from datetime import date\n", "")],
        "app/services/holding/holding_sync_service.py": [("Optional, ", "")],
        "app/services/review/review_service.py": [("Optional, ", "")],
        "app/services/settings/settings_service.py": [("Optional, Dict, Any", "")],
        "app/services/stock/stock_detail_service.py": [("Optional, ", "")],
        "app/utils/tushare_client.py": [
            ("from typing import List\n", ""),
            ("from decimal import Decimal\n", ""),
        ],
    }

    for file_path, replacements in fixes.items():
        full_path = Path(file_path)
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")
            for old, new in replacements:
                content = content.replace(old, new)
            full_path.write_text(content, encoding="utf-8")
            print(f"✅ Fixed imports: {file_path}")


def fix_auth_service():
    """修复 auth_service.py 中的 is True/False 比较"""
    file_path = Path("app/services/auth_service.py")
    if not file_path.exists():
        return

    content = file_path.read_text(encoding="utf-8")

    # 修复 == True 和 == False
    content = re.sub(r"(\w+)\s*==\s*True", r"\1 is True", content)
    content = re.sub(r"(\w+)\s*==\s*False", r"\1 is False", content)

    file_path.write_text(content, encoding="utf-8")
    print("✅ Fixed: app/services/auth_service.py")


def fix_bare_except():
    """修复裸except语句"""
    fixes = {
        "app/services/ai/daily_review_service.py": (
            "        except:\n",
            "        except Exception:\n",
        ),
        "app/utils/ai_client.py": ("            except:\n", "            except Exception:\n"),
    }

    for file_path, (old, new) in fixes.items():
        full_path = Path(file_path)
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")
            content = content.replace(old, new)
            full_path.write_text(content, encoding="utf-8")
            print(f"✅ Fixed bare except: {file_path}")


def fix_unused_variables():
    """修复未使用的变量"""
    file_path = Path("app/services/holding/holding_sync_service.py")
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        # 将 old_total_cost = 替换为 _ =
        content = re.sub(r"old_total_cost\s*=", "_old_total_cost =", content)
        file_path.write_text(content, encoding="utf-8")
        print("✅ Fixed unused variable: app/services/holding/holding_sync_service.py")


def fix_long_line():
    """修复超长行"""
    file_path = Path("app/models/strategy.py")
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        # 找到第57行并拆分
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if i == 56 and len(line) > 120:  # 第57行 (索引56)
                # 拆分长行
                if "comment=" in line:
                    # 将comment参数移到下一行
                    lines[i] = line.replace(", comment=", ",\n                        comment=")
                    break
        content = "\n".join(lines)
        file_path.write_text(content, encoding="utf-8")
        print("✅ Fixed long line: app/models/strategy.py")


def main():
    """主函数"""
    print("🔧 修复剩余的flake8问题...\n")

    fix_unused_imports()
    fix_auth_service()
    fix_bare_except()
    fix_unused_variables()
    fix_long_line()

    print("\n✅ 所有问题已修复！")


if __name__ == "__main__":
    main()
