result = ''
a = input()
while a != 'a':
    result += '"${}", '.format(a)
    a = input()

print(result)
