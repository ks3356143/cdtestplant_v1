import pydash as _

res = _.compact([1, 2, 3, 0, False, ""])
print(res)
