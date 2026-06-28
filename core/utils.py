"""共享工具函数"""


def col_letter(n: int) -> str:
    """数字列号 → 字母列号（1→A, 27→AA）"""
    result = ""
    while n > 0:
        n -= 1
        result = chr(n % 26 + ord("A")) + result
        n //= 26
    return result
