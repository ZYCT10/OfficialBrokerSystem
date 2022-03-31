#
# Test python random choices module
#
from random import choices
from string import ascii_lowercase


def random_letters(length):
    ret = ''.join(choices(ascii_lowercase, k=length))
    return(ret)

length = 12
random_string = random_letters(length)


if len(random_string) == length:
    print("OK: generating random string: {}".format(random_string))
else:
    print("WARNING: python generate random string")
