#!/usr/bin/env python3
"""
自动修复flake8代码规范问题
"""
import re
from pathlib import Path


def fix_file(file_path: Path):
    """修复单个文件的flake8问题"""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # 1. 移除未使用的导入
    unused_imports = {
        'app/api/v1/account_api.py': ['from fastapi import Body'],
        'app/core/config.py': ['from pydantic import field_validator'],
        'app/repositories/ai_conversation_repo.py': ['from typing import List'],
        'app/repositories/event_repo.py': ['from sqlalchemy import or_'],
        'app/repositories/trade_repo.py': ['from sqlalchemy import or_'],
        'app/services/ai/daily_analysis_service.py': ['import asyncio'],
    }

    rel_path = str(file_path.relative_to(Path.cwd() / 'backend'))
    if rel_path in unused_imports:
        for unused in unused_imports[rel_path]:
            content = content.replace(unused + '\n', '')

    # 2. 修复 E712: comparison to False should be 'if cond is False:' or 'if not cond:'
    # 将 == False 替换为 is False
    content = re.sub(r'(\w+)\s*==\s*False', r'\1 is False', content)

    # 3. 修复未使用的变量 F841
    if 'ai_chat_service.py' in str(file_path):
        # 移除未使用的 conv 变量赋值
        content = re.sub(
            r'\n\s+conv = await self\.conversation_repo\.create\(conversation_data\)\n',
            '\n        await self.conversation_repo.create(conversation_data)\n',
            content
        )

    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Fixed: {rel_path}")
        return True
    return False


def fix_long_lines():
    """手动修复过长的行（需要人工审查）"""
    fixes = {
        'app/models/account.py': [
            (37, '    available_cash = Column(NUMERIC(20, 8), default=0, nullable=False,\n                            comment="可用资金")'),
        ],
        'app/models/ai_decision.py': [
            (28, '    confidence = Column(NUMERIC(5, 2), nullable=True,\n                       comment="置信度(0-100)")'),
            (38, '    created_at = Column(TIMESTAMPTZ, server_default=func.now(),\n                        comment="创建时间")'),
            (69, '        index=True, comment="用户ID (虚拟外键关联users.user_id)")'),
        ],
    }
    print("\n⚠️  需要手动修复的长行（已生成建议）:")
    for file, lines in fixes.items():
        print(f"  {file}")
        for line_no, suggestion in lines:
            print(f"    Line {line_no}: 建议拆分")


def main():
    """主函数"""
    backend_dir = Path.cwd() / 'backend' / 'app'

    files_to_fix = [
        'api/v1/account_api.py',
        'core/config.py',
        'repositories/account_repo.py',
        'repositories/ai_conversation_repo.py',
        'repositories/ai_decision_repo.py',
        'repositories/event_repo.py',
        'repositories/holding_repo.py',
        'repositories/review_repo.py',
        'repositories/stock_repo.py',
        'repositories/strategy_repo.py',
        'repositories/trade_repo.py',
        'services/ai/ai_chat_service.py',
        'services/ai/daily_analysis_service.py',
    ]

    print("🔧 开始修复flake8问题...\n")

    fixed_count = 0
    for file_rel in files_to_fix:
        file_path = backend_dir / file_rel
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1

    print(f"\n✅ 已自动修复 {fixed_count} 个文件")

    # 长行需要手动处理
    # fix_long_lines()


if __name__ == '__main__':
    main()
