import numpy as np
import matplotlib.pyplot as plt

data = np.load("data_data_mining_ate-20_atc-160.npy")
# data = np.load("data_data_mining_ate-20_atc-20.npy")
mean = np.mean(data, axis=0)
percentile_95 = np.percentile(data,95, axis=0)
percentile_99 = np.percentile(data,99, axis=0)
plt.plot(mean, label="mean")
plt.plot(percentile_95, label="95%")
plt.plot(percentile_99, label="99%") 
plt.xlabel("flows/s")
plt.ylabel("Completion Time (s)")
plt.legend()
plt.savefig("data_mining.png")


# data = np.load("data_web_search.npy")
# data = np.load("data_data_mining.npy")
# mean = np.mean(data, axis=0)
# percentile_95 = np.percentile(data,95, axis=0)
# percentile_99 = np.percentile(data,99, axis=0)
# plt.plot(mean, label="mean")
# plt.plot(percentile_95, label="95%")
# plt.plot(percentile_99, label="99%")
# plt.legend()

# plt.savefig("data_mining.png")
