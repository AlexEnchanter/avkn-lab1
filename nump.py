import os
import numpy as np
import matplotlib.pyplot as plt

files = ["data_web search_ate-20_atc-20.npy",  "data_data mining_ate-20_atc-20.npy",
         "data_web search_ate-80_atc-20.npy",  "data_data mining_ate-80_atc-20.npy",
         "data_web search_ate-80_atc-160.npy", "data_data mining_ate-80_atc-160.npy"]
names = ["web serch ate20 atc20",  "data mining ate20 atc20", 
         "web serch ate80 atc20",  "data mining ate80 atc20",
         "web serch ate80 atc160", "data mining ate80 atc160"]

one2ten = np.arange(1, 11, 1)
for i in range(len(files)): 
    if not os.path.exists(files[i]):
        continue

    data = np.load(files[i], allow_pickle=True)
    mean = [np.mean(data[i], axis=0) for i in range(10)]
    std = [np.std(data[i], axis=0) for i in range(10)]
    percentile_95 = [np.percentile(data[i], 95, axis=0) for i in range(10)]
    percentile_99 = [np.percentile(data[i], 99, axis=0) for i in range(10)]
    plt.errorbar(one2ten, mean, label="mean", yerr = std, capsize = 4)
    plt.errorbar(one2ten, percentile_95, label="95%", yerr = std, capsize = 4)
    plt.errorbar(one2ten, percentile_99, label="99%", yerr = std, capsize = 4) 
    plt.xlabel("flows/s")
    plt.ylabel("Completion Time (s)")
    plt.xticks(np.arange(1, 11, 1))
    plt.title(names[i])
    plt.legend()
    if "data" in names[i]:
        plt.yscale("log") 
    plt.savefig(f"{names[i]}.png")
    plt.clf()

