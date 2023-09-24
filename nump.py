import numpy as np
import matplotlib.pyplot as plt

files = ["data_web search_ate-20_atc-20.npy",  "data_data mining_ate-20_atc-20.npy",
         "data_web search_ate-80_atc-20.npy",  "data_data mining_ate-80_atc-20.npy",
         "data_web search_ate-80_atc-160.npy", "data_data mining_ate-80_atc-160.npy"]
names = ["web serch ate20 atc20",  "data mining ate20 atc20", 
         "web serch ate80 atc20",  "data mining ate80 atc20",
         "web serch ate80 atc160", "data mining ate80 atc160"]

# for i in range(len(files)):
one2ten = np.arange(1, 11, 1)
data = np.load(files[0], allow_pickle=True)
mean = [np.mean(data[i], axis=0) for i in range(10)]
percentile_95 = [np.percentile(data[i], 95, axis=0) for i in range(10)]
percentile_99 = [np.percentile(data[i], 99, axis=0) for i in range(10)]
plt.plot(one2ten, mean, label="mean")
plt.plot(one2ten, percentile_95, label="95%")
plt.plot(one2ten, percentile_99, label="99%") 
plt.xlabel("flows/s")
plt.ylabel("Completion Time (s)")
plt.xticks(np.arange(1, 11, 1))
plt.title(names[0])
# plt.yscale("log")
plt.legend()
plt.savefig(f"{names[0]}.png")
plt.clf()


