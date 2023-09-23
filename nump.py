import numpy as np
import matplotlib.pyplot as plt

files = ["data_web search_ate-20_atc-20.npy",  "data_data mining_ate-20_atc-20.npy",
         "data_web search_ate-80_atc-20.npy",  "data_data mining_ate-80_atc-20.npy",
         "data_web search_ate-80_atc-160.npy", "data_data mining_ate-80_atc-160.npy"]
names = ["web serch ate20 atc20",  "data mining ate20 atc20", 
         "web serch ate80 atc20",  "data mining ate80 atc20",
         "web serch ate80 atc160", "data mining ate80 atc160"]
## I want to use axis 1 for lator 
for i in range(len(files)):
    data = np.load(files[i])
    mean = np.mean(data, axis=0)
    percentile_95 = np.percentile(data,95, axis=0)
    percentile_99 = np.percentile(data,99, axis=0)
    plt.plot(mean, label="mean")
    plt.plot(percentile_95, label="95%")
    plt.plot(percentile_99, label="99%") 
    plt.xlabel("flows/s")
    plt.ylabel("Completion Time (s)")
    plt.title(names[i])
    plt.legend()
    plt.savefig(f"{names[i]}.png")
    plt.clf()


