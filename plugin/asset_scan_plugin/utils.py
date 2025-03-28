import re

# 去除端口
def remove_port(url):
    return re.sub(r":\d+", "", url)


# 使用正则去掉 http:// 或 https://
def clean_url(url):
    url_pattern = re.compile(r'https?://')
    return remove_port(re.sub(url_pattern, '', url))


# 判断是不是ipv4
def is_ipv4(url):
    ipv4_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if ipv4_pattern.match(url):
        return True
    return False

