#!/usr/bin/env python3
"""
架构守卫 - 自动检查代码是否符合架构规范

运行: python scripts/check_architecture.py

检查项:
1. API方法必须使用POST
2. Service文件命名规范
3. Converter必须使用@staticmethod
4. Builder必须使用@staticmethod
5. Controller不包含业务逻辑
"""

import os
import re
import sys
from pathlib import Path
from typing import List


class Colors:
    """终端颜色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def check_backend_architecture() -> List[str]:
    """检查后端架构规范"""
    violations = []
    backend_path = Path("backend")

    if not backend_path.exists():
        return violations

    # 检查1: API必须使用POST方法
    print(f"{Colors.BLUE}检查后端API方法...{Colors.NC}")
    api_path = backend_path / "app" / "api"
    if api_path.exists():
        api_files = list(api_path.rglob("*.py"))
        for file in api_files:
            if file.name == "__init__.py":
                continue
            try:
                content = file.read_text()
                # 检查是否使用了GET/PUT/DELETE/PATCH方法
                matches = re.findall(r'@router\.(get|put|delete|patch)\s*\(', content)
                if matches:
                    violations.append(
                        f"{file.relative_to(Path.cwd())}: "
                        f"使用了非POST方法 - {set(matches)}"
                    )
            except Exception as e:
                print(f"  警告: 无法读取 {file}: {e}")

    # 检查2: Service文件命名规范
    print(f"{Colors.BLUE}检查Service文件命名...{Colors.NC}")
    services_path = backend_path / "app" / "services"
    if services_path.exists():
        service_files = list(services_path.rglob("*.py"))
        for file in service_files:
            if file.name == "__init__.py":
                continue
            if not file.name.endswith("_service.py"):
                violations.append(
                    f"{file.relative_to(Path.cwd())}: "
                    f"Service文件必须以_service.py结尾"
                )

    # 检查3: Converter必须是静态方法
    print(f"{Colors.BLUE}检查Converter静态方法...{Colors.NC}")
    if services_path.exists():
        for file in service_files:
            try:
                content = file.read_text()
                if "Converter" not in content:
                    continue

                # 提取Converter类的内容
                converter_blocks = re.findall(
                    r'class\s+\w+Converter.*?(?=\n(?:class|$))',
                    content,
                    re.DOTALL
                )

                for block in converter_blocks:
                    # 找出所有方法
                    methods = re.findall(r'def\s+(\w+)\s*\(', block)
                    # 找出静态方法
                    static_methods = re.findall(
                        r'@staticmethod\s+def\s+(\w+)\s*\(',
                        block
                    )

                    # 排除__init__和特殊方法
                    non_static = set(methods) - set(static_methods)
                    non_static = {m for m in non_static if not m.startswith('__')}

                    if non_static:
                        violations.append(
                            f"{file.relative_to(Path.cwd())}: "
                            f"Converter方法不是静态方法 - {non_static}"
                        )
            except Exception as e:
                print(f"  警告: 无法检查 {file}: {e}")

    # 检查4: Builder必须是静态方法
    print(f"{Colors.BLUE}检查Builder静态方法...{Colors.NC}")
    if services_path.exists():
        for file in service_files:
            try:
                content = file.read_text()
                if "Builder" not in content:
                    continue

                # 提取Builder类的内容
                builder_blocks = re.findall(
                    r'class\s+\w+Builder.*?(?=\n(?:class|$))',
                    content,
                    re.DOTALL
                )

                for block in builder_blocks:
                    methods = re.findall(r'def\s+(\w+)\s*\(', block)
                    static_methods = re.findall(
                        r'@staticmethod\s+def\s+(\w+)\s*\(',
                        block
                    )

                    non_static = set(methods) - set(static_methods)
                    non_static = {m for m in non_static if not m.startswith('__')}

                    if non_static:
                        violations.append(
                            f"{file.relative_to(Path.cwd())}: "
                            f"Builder方法不是静态方法 - {non_static}"
                        )
            except Exception as e:
                print(f"  警告: 无法检查 {file}: {e}")

    # 检查5: Repository不应包含业务逻辑关键字
    print(f"{Colors.BLUE}检查Repository纯净性...{Colors.NC}")
    repo_path = backend_path / "app" / "repositories"
    if repo_path.exists():
        repo_files = list(repo_path.rglob("*.py"))
        business_keywords = ['calculate', 'compute', 'process', 'convert', 'transform']

        for file in repo_files:
            if file.name == "__init__.py":
                continue
            try:
                content = file.read_text()
                # 检查是否包含业务逻辑关键字
                found_keywords = []
                for keyword in business_keywords:
                    if re.search(rf'\bdef\s+{keyword}', content, re.IGNORECASE):
                        found_keywords.append(keyword)

                if found_keywords:
                    violations.append(
                        f"{file.relative_to(Path.cwd())}: "
                        f"Repository可能包含业务逻辑 - 发现方法: {found_keywords}"
                    )
            except Exception as e:
                print(f"  警告: 无法检查 {file}: {e}")

    return violations


def check_frontend_architecture() -> List[str]:
    """检查前端架构规范"""
    violations = []
    frontend_path = Path("frontend")

    if not frontend_path.exists():
        return violations

    # 检查1: 组件应使用Composition API
    print(f"{Colors.BLUE}检查前端Composition API...{Colors.NC}")
    src_path = frontend_path / "src"
    if src_path.exists():
        vue_files = list(src_path.rglob("*.vue"))
        for file in vue_files:
            try:
                content = file.read_text()
                # 检查是否使用Options API
                if "export default {" in content:
                    # 检查是否有setup
                    if "setup(" not in content and "<script setup" not in content:
                        violations.append(
                            f"{file.relative_to(Path.cwd())}: "
                            f"组件应使用Composition API（<script setup>）"
                        )
            except Exception as e:
                print(f"  警告: 无法读取 {file}: {e}")

    # 检查2: 不应直接在组件中调用axios
    print(f"{Colors.BLUE}检查前端API调用...{Colors.NC}")
    if src_path.exists():
        vue_files = list(src_path.rglob("*.vue"))
        for file in vue_files:
            # 排除service目录
            if "service" in str(file):
                continue
            try:
                content = file.read_text()
                # 检查是否直接导入axios
                if re.search(r"import\s+.*\s+from\s+['\"]axios['\"]", content):
                    violations.append(
                        f"{file.relative_to(Path.cwd())}: "
                        f"不应在组件中直接导入axios，请使用API Service"
                    )
            except Exception as e:
                print(f"  警告: 无法检查 {file}: {e}")

    return violations


def main():
    """主函数"""
    print()
    print("🔍 开始架构检查...")
    print("=" * 50)
    print()

    all_violations = []

    # 检查后端
    if Path("backend").exists():
        print(f"{Colors.YELLOW}📦 后端架构检查{Colors.NC}")
        print("-" * 50)
        backend_violations = check_backend_architecture()
        all_violations.extend(backend_violations)
        print(f"  发现 {len(backend_violations)} 个违反项")
        print()

    # 检查前端
    if Path("frontend").exists():
        print(f"{Colors.YELLOW}📦 前端架构检查{Colors.NC}")
        print("-" * 50)
        frontend_violations = check_frontend_architecture()
        all_violations.extend(frontend_violations)
        print(f"  发现 {len(frontend_violations)} 个违反项")
        print()

    # 输出结果
    print("=" * 50)
    print()

    if all_violations:
        print(f"{Colors.RED}❌ 架构检查失败！发现以下违反项:{Colors.NC}")
        print()
        for i, violation in enumerate(all_violations, 1):
            print(f"{Colors.RED}{i}.{Colors.NC} {violation}")
        print()
        print(f"{Colors.YELLOW}总计: {len(all_violations)} 个违反项{Colors.NC}")
        print()
        print(f"{Colors.BLUE}💡 请参考:{Colors.NC}")
        print("   - backend/ARCHITECTURE.md")
        print("   - frontend/ARCHITECTURE.md")
        print("   - ~/.claude/CLAUDE.md")
        print()
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}✅ 架构检查通过！{Colors.NC}")
        print(f"{Colors.GREEN}所有代码符合架构规范。{Colors.NC}")
        print()
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}检查已取消{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"{Colors.RED}错误: {e}{Colors.NC}")
        sys.exit(1)
