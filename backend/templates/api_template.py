"""
API Controller Template - {Module}模块API

========================================
使用说明
========================================
1. 复制此文件到 backend/app/api/v1/{module}_api.py
2. 全局替换以下占位符:
   - {Module} → 模块名称（如 Account）
   - {module} → 模块名称小写（如 account）
   - {Feature} → 功能名称（如 AccountDetail）
   - {Action} → 动作名称（如 detail）
3. 根据实际业务填充 TODO 部分
4. 编写完整的8段式API文档注释

========================================
架构约束
========================================
✅ 所有API必须使用 POST 方法
✅ URL格式: /api/v1/{module}/{action}
✅ Controller只负责: 接收请求 → 获取用户 → 调用Service → 返回响应
✅ 不允许在 Controller 中编写业务逻辑
✅ 必须编写完整的8段式API文档注释
✅ 必须进行异常处理

参考文档: backend/ARCHITECTURE.md
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

# TODO: 导入数据库依赖
# from backend.app.core.deps import get_db, get_current_user

# TODO: 导入Service
# from backend.app.services.{module}.{action}_service import {Feature}Service

# TODO: 导入用户模型
# from backend.app.models.user import User


router = APIRouter(
    prefix="/api/v1/{module}",
    tags=["{module}"]
)


@router.post("/{action}")
async def {action}_endpoint(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    {接口标题}

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/{action}
    对应页面: pages/{module}/{action}.vue
    接口功能: [功能描述]

    业务场景:
    - 场景1: [描述]
    - 场景2: [描述]

    ========================================
    请求参数
    ========================================
    {
        "param1": "string",    # 参数1说明（必需）
        "param2": 123,         # 参数2说明（可选）
        "param3": {            # 参数3说明（可选）
            "sub1": "value",
            "sub2": 456
        }
    }

    参数说明:
    - param1 (string, 必需): 详细说明
    - param2 (number, 可选): 详细说明，默认值: 0
    - param3 (object, 可选): 详细说明

    ========================================
    响应数据
    ========================================
    成功响应 (200):
    {
        "code": 0,
        "message": "success",
        "data": {
            "field1": "value1",
            "field2": 123,
            "field3": {
                "subfield1": "value",
                "subfield2": 456
            }
        }
    }

    字段说明:
    - data.field1 (string): 字段1说明
    - data.field2 (number): 字段2说明
    - data.field3 (object): 字段3说明

    ========================================
    执行流程（时序）
    ========================================
    1. [Controller] 接收请求，验证参数格式
    2. [Controller] 获取当前用户信息
    3. [Service] 验证业务参数
    4. [Service] 检查用户权限
    5. [Repository] 查询数据库
    6. [Converter] 执行业务计算
    7. [Builder] 构建响应数据
    8. [Controller] 返回响应

    ========================================
    业务规则
    ========================================
    1. 规则1: [描述具体的业务规则]
    2. 规则2: [描述具体的业务规则]
    3. 规则3: [描述具体的业务规则]

    权限要求:
    - 需要登录
    - 需要拥有资源访问权限

    数据验证:
    - 验证项1: [描述]
    - 验证项2: [描述]

    ========================================
    错误码
    ========================================
    | 错误码 | 说明 | 处理建议 |
    |--------|------|----------|
    | 1001 | 缺少必需参数 | 检查请求参数 |
    | 1002 | 参数格式错误 | 检查参数类型 |
    | 2001 | 无权访问 | 检查用户权限 |
    | 3001 | 资源不存在 | 检查资源ID |
    | 5001 | 服务器内部错误 | 联系技术支持 |

    ========================================
    前端调用示例
    ========================================
    ```typescript
    // services/api/{module}.ts
    import { post } from '@/utils/request'

    export const {action}{Module} = async (params: {
        param1: string
        param2?: number
        param3?: {
            sub1: string
            sub2: number
        }
    }) => {
        return await post('/api/v1/{module}/{action}', params)
    }
    ```

    ```vue
    <!-- pages/{module}/{action}.vue -->
    <script setup lang="ts">
    import { {action}{Module} } from '@/services/api/{module}'

    const handle{Action} = async () => {
        try {
            const result = await {action}{Module}({
                param1: 'value1',
                param2: 123
            })
            console.log(result.data)
        } catch (error) {
            console.error('操作失败:', error)
        }
    }
    </script>
    ```

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本，实现基础功能
    YYYY-MM-DD: [修改内容描述]

    ========================================
    相关文档
    ========================================
    - PRD: docs/prd/v3/main.md
    - Service: backend/app/services/{module}/{action}_service.py
    - Repository: backend/app/repositories/{module}_repo.py
    - 前端页面: frontend/src/pages/{module}/{action}.vue
    """

    try:
        # TODO: 第1步 - 基础参数验证（可选）
        # if "required_param" not in request:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="缺少必需参数: required_param"
        #     )

        # TODO: 第2步 - 创建Service实例
        # service = {Feature}Service(db)

        # TODO: 第3步 - 调用Service执行业务逻辑
        # result = await service.execute(request, user.id)

        # TODO: 第4步 - 返回成功响应
        # return {
        #     "code": 0,
        #     "message": "success",
        #     "data": result
        # }

        # 临时返回（开发时删除）
        return {
            "code": 0,
            "message": "success",
            "data": {
                "info": "请实现业务逻辑"
            }
        }

    except PermissionError as e:
        # 权限错误 (403)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except ValueError as e:
        # 参数错误 (400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # 服务器内部错误 (500)
        # TODO: 添加日志记录
        # logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


# ========================================
# 其他常用端点示例
# ========================================

@router.post("/query")
async def query_{module}(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    查询{Module}列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/query
    对应页面: pages/{module}/list.vue
    接口功能: 查询{Module}列表，支持分页和筛选

    ========================================
    请求参数
    ========================================
    {
        "page": 1,              # 页码（可选，默认1）
        "page_size": 20,        # 每页数量（可选，默认20）
        "filters": {            # 筛选条件（可选）
            "status": "active",
            "keyword": "搜索关键词"
        },
        "sort": {               # 排序（可选）
            "field": "created_at",
            "order": "desc"     # asc/desc
        }
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "id": 1,
                    "name": "示例",
                    "status": "active",
                    "created_at": "2025-01-01T00:00:00Z"
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 20,
                "total": 100,
                "total_pages": 5
            }
        }
    }

    ========================================
    执行流程
    ========================================
    1. 接收分页和筛选参数
    2. 调用Service查询数据
    3. 返回列表和分页信息

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本
    """
    # TODO: 实现列表查询逻辑
    pass


@router.post("/create")
async def create_{module}(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    创建{Module}

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/create
    对应页面: pages/{module}/create.vue
    接口功能: 创建新的{Module}记录

    ========================================
    请求参数
    ========================================
    {
        "name": "string",       # 名称（必需）
        "description": "string", # 描述（可选）
        "status": "active"      # 状态（可选，默认active）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "创建成功",
        "data": {
            "id": 123,
            "name": "string",
            "created_at": "2025-01-01T00:00:00Z"
        }
    }

    ========================================
    执行流程
    ========================================
    1. 验证必需参数
    2. 检查数据唯一性（如需要）
    3. 调用Service创建记录
    4. 返回创建的记录

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本
    """
    # TODO: 实现创建逻辑
    pass


@router.post("/update")
async def update_{module}(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    更新{Module}

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/update
    对应页面: pages/{module}/edit.vue
    接口功能: 更新{Module}记录

    ========================================
    请求参数
    ========================================
    {
        "id": 123,              # 记录ID（必需）
        "name": "string",       # 名称（可选）
        "description": "string", # 描述（可选）
        "status": "active"      # 状态（可选）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "更新成功",
        "data": {
            "id": 123,
            "name": "string",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    }

    ========================================
    执行流程
    ========================================
    1. 验证ID参数
    2. 检查记录是否存在
    3. 检查用户权限
    4. 调用Service更新记录
    5. 返回更新后的记录

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本
    """
    # TODO: 实现更新逻辑
    pass


@router.post("/delete")
async def delete_{module}(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    删除{Module}（软删除）

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/delete
    对应页面: pages/{module}/list.vue
    接口功能: 软删除{Module}记录

    ========================================
    请求参数
    ========================================
    {
        "id": 123              # 记录ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "删除成功",
        "data": {
            "id": 123,
            "deleted_at": "2025-01-01T00:00:00Z"
        }
    }

    ========================================
    执行流程
    ========================================
    1. 验证ID参数
    2. 检查记录是否存在
    3. 检查用户权限
    4. 调用Service软删除记录
    5. 返回删除结果

    ========================================
    业务规则
    ========================================
    1. 使用软删除（设置 is_deleted=true, deleted_at=now()）
    2. 不允许删除已被引用的记录
    3. 需要记录删除操作日志

    ========================================
    修改记录
    ========================================
    YYYY-MM-DD: 初始版本
    """
    # TODO: 实现删除逻辑
    pass
