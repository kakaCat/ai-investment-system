# API 文档生成

为 API 端点生成完整的 8 段式文档注释。

---

请为 $ARGUMENTS 生成 API 文档：

## 输入说明
- 可以是 API 端点路径: `/api/v1/account/detail`
- 可以是功能描述: `获取账户详情`
- 可以是现有代码文件: `backend/app/api/v1/account_api.py`

## 分析内容

### 1. 接口信息收集
- 确定接口路径和方法（必须是 POST）
- 确定对应的前端页面
- 明确接口功能

### 2. 参数分析
- 从 Service 或需求文档推断请求参数
- 确定参数类型和是否必填
- 添加参数说明

### 3. 响应分析
- 从 Builder 或 Converter 推断响应结构
- 确定字段类型和含义
- 包含嵌套结构

### 4. 流程分析
- 分析 Service 执行流程
- 梳理时序步骤
- 标注关键节点

### 5. 业务规则
- 从 Converter 提取业务规则
- 权限和验证规则
- 边界条件处理

## 输出格式

生成符合项目规范的 8 段式文档：

```python
@router.post("/{action}")
async def {function_name}(request: {RequestModel}, user: User = Depends(get_current_user)):
    """
    {接口标题}

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/{module}/{action}
    对应页面: pages/{module}/{page}.vue
    接口功能: {功能描述}

    ========================================
    请求参数
    ========================================
    {
        "param1": {
            "type": "string",
            "required": true,
            "description": "参数说明"
        },
        "param2": {
            "type": "integer",
            "required": false,
            "default": 10,
            "description": "参数说明"
        }
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "field1": "string - 字段说明",
            "field2": 123,
            "nested": {
                "sub_field": "说明"
            },
            "list": [
                {
                    "item_field": "说明"
                }
            ]
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. 验证用户登录状态
    2. 参数校验
    3. 权限检查（验证用户是否有权访问该资源）
    4. 调用 Repository 获取数据
    5. 调用 Converter 进行业务处理
    6. 调用 Builder 构建响应
    7. 返回结果

    ========================================
    业务规则
    ========================================
    1. 规则1: 说明
    2. 规则2: 说明
    3. 权限: 只能访问自己的数据

    ========================================
    错误码
    ========================================
    400: 参数错误
    401: 未登录
    403: 无权限访问
    404: 资源不存在
    1001: 业务错误1
    1002: 业务错误2

    ========================================
    前端调用示例
    ========================================
    // 基本调用
    const response = await api.post('/api/v1/{module}/{action}', {
        param1: 'value',
        param2: 10
    })

    // 处理响应
    if (response.code === 0) {
        const data = response.data
        // 处理数据
    }

    ========================================
    修改记录
    ========================================
    {YYYY-MM-DD}: 初始版本
    """
    service = {Action}Service()
    return await service.execute(request.dict(), user.id)
```

## 使用示例
- `/api-doc-gen /api/v1/account/detail` - 为指定端点生成文档
- `/api-doc-gen 事件列表查询` - 根据功能描述生成
- `/api-doc-gen backend/app/api/v1/event_api.py:get_events` - 为现有函数补充文档
