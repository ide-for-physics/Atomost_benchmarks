import sys
n1,n2,n3=map(int,sys.argv[1:4])
N=n1*n2*n3
print(N)
for i in range(n1):
    for j in range(n2):
        for k in range(n3):
            print(f"{i/n1:.10f} {j/n2:.10f} {k/n3:.10f} {1.0/N:.12f}")
