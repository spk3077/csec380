the_set = set()

file = open("paths3.list", 'r')
lines = file.readlines()

for line in lines:
    line = line.replace("\n","")
    the_set.add(line)

file.close()

file = open ("paths2.list", 'r')
lines = file.readlines()

for line in lines:
    line = line.replace("\n","")
    the_set.add(line)

file = open ("paths.list", 'w')
for item in the_set:
    file.write(item)
    file.write("\n")
