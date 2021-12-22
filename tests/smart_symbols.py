#
# Test removing smart symbols
#
from string import ascii_letters, digits

# Smart symbols removal
def smart_symbols(param, need):
    types = {"letteral": ascii_letters + "_",
             "digital": digits + "."}
    new = [e for e in param if e in types[need]]
    return "".join(new)


float_case = smart_symbols("14.(6s1327]!6793{}~|*0\8j6&a2735'[", "digital")
int_case = smart_symbols("(1%)@623#!*86(%|23|  !@~950!@$^7#$%'", "digital")
sentence_case = smart_symbols("(U@S)DT)!@_+FUTURE!@!~]     ~}{", "letteral")
word_case = smart_symbols("!@T/' '/`%)#@%RXE%(#@$09012~`*#!%TH", "letteral")

cases = [float_case,
         int_case,
         sentence_case,
         word_case]

outs = ["14.6132767930862735",
        "162386239507",
        "USDT_FUTURE",
        "TRXETH"]

for i in range(len(cases)):
    if cases[i] == outs[i]:
        print("OK: removing smart symbols {}".format(cases[i]))
    else:
        print("WARNING: removing smart symbols")
