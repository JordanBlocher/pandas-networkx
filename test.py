import matplotlib.pyplot as plt

f1 = plt.figure()
plt.plot([1, 2, 3])
plt.title("Figure 1 not cleared clf()") 

f2 = plt.figure()
plt.plot([1,2,3]) 
# Clear Figure 2 with clf() function:
plt.clf()
plt.title("Figure 2 cleared with clf()")

plt.show()
