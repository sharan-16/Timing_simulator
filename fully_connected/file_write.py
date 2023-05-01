import numpy as np
rand1 = np.random.randint(10, size=(1,256))
string_array = []
f = open("VDMEM.txt", "w")
print(rand1)
for i in range(0,256):
  for j in range(0,256):
    f.write(str(rand1[0][j]))
    f.write('\n')
    # write rand1[0][j] into the file
    pass
inputs = np.random.randint(10, size=(1,256))
for j in range(0,256):
    # write inputs[0][j] into the file
    f.write(str("1"))
    f.write('\n')
    pass
print(inputs)

f.close()


result = np.sum(rand1)
print(result)