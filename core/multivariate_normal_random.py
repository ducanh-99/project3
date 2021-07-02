import numpy as np
# means = np.array([[1, 5, 2],
#                   [6, 2, 7],
#                   [1, 8, 2]])
num_samples = 10
# flat_means = means.ravel()

# # build block covariance matrix
cov = np.eye(2)
block_cov = np.kron(np.eye(1), cov)
print(block_cov)
mean = [35, 10]
cov = [15, 20]


out = np.random.multivariate_normal(
    mean, cov=block_cov, size=num_samples)

# out = out.reshape((-1,) + means.shape)
print(out)
