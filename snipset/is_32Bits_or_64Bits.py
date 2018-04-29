import platform
print(platform.architecture())

import sys
is_64bits = sys.maxsize > 2**32
print("is_64bits : ")
print(is_64bits)