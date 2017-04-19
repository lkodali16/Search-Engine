import math
from scipy import t

f = open('ttest_data.txt', 'r')
data = f.readlines()
data = [i.split() for i in data]
data_a = [int(i[0]) for i in data]
data_b = [int(i[1]) for i in data]

b_minus_a = [(int(i[1]) - int(i[0])) for i in data]
# sigma calculation
x_mean = float(sum(b_minus_a)) / len(b_minus_a)

sigma_ab = sum([(x-x_mean)**2 for x in b_minus_a])

sigma_ab = sigma_ab ** (0.5)

t_value = (x_mean / sigma_ab) * len(b_minus_a)
p_value = t.sf(t_value, len(b_minus_a))
print sigma_ab/(10**(0.5))
print t_value