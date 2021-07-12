from datetime import datetime, timedelta, date

# a = timedelta(minutes=3)
# # a = a.
# b = time(minute=5)
# c = datetime.combine(date.min, b) - datetime.min
# print(c)
# # for i in range(5):
# #     b += a
# # print(b)

# _time = [timedelta(minutes=6), timedelta(minutes=5), timedelta(minutes=4)]
# a = [3, 2, 1]
# _time, a = zip(*sorted(zip(_time, a)))
# print(_time, a)
# sum(_time)

a = datetime.now()

b  = a - datetime(year=2021, month=7, day=11)
print(type(b))