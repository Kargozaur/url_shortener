import string

chars = string.digits + string.ascii_letters


def encode_base62(n):
    if n == 0:
        return chars[0]
    result = ""
    while n > 0:
        n, rem = divmod(n, 62)
        result = chars[rem] + result
    return result
