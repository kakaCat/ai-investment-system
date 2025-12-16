"""
基础测试文件

这个文件包含一些基础的测试用例，确保pytest可以运行。
"""
import pytest


def test_basic():
    """基础测试 - 验证pytest工作正常"""
    assert True


def test_string_operations():
    """测试字符串操作"""
    test_str = "AI Investment System"
    assert test_str.startswith("AI")
    assert "Investment" in test_str
    assert test_str.endswith("System")


def test_numeric_operations():
    """测试数值操作"""
    assert 1 + 1 == 2
    assert 10 * 10 == 100
    assert 100 / 4 == 25


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (0, False),
        (1, True),
        (-1, True),
        (100, True),
    ],
)
def test_boolean_conversion(input_value, expected):
    """测试布尔转换"""
    assert bool(input_value) == expected
