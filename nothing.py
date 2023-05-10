import numpy as np

gt = np.array([[0, 2, 1],
               [1, 2, 1],
               [1, 0, 1]])

pre = np.array([[0, 1, 1],
                [2, 0, 1],
                [1, 1, 1]])
num_class = 3
mask = (gt >= 0) & (gt < num_class)
print(mask)
print(gt[mask].astype('int'))
label = num_class * gt[mask].astype('int') + pre[mask]
print(label)