from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import setLogLevel
import argparse
import math 
import numpy as np
import random
import subprocess
import re
import time
import sys

x_web = [0,10_000, 20_000,30_000,50_000,80_000,200_000, 1_000_000, 2_000_000,5_000_000, 10_000_000,30_000_000]	
y_web = [0., 0.18, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98, 1.]
x_data = [0,180,216,560,900,1_100,1_870, 3_160, 10_000, 400_000, 3_160_000, 100_000_000, 1_000_000_000]
y_data = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ,0.97, 0.99, 1.]
edge_to_host_bw = 20
agr_to_core_bw = 20 
agr_to_edge_bw = 20

debug = False

class MyTopo(Topo):
    def build( self ):
        aggr_layer_switches = 4
        edge_layer_switches = 8
        num_of_hosts = 16
       
        #adding core layer, aggregation layer and edge layer switches
        core = self.addSwitch('s1')
        hosts = [self.addHost(f'h{i+1}') for i in range(num_of_hosts)]
        aggr_layer = [self.addSwitch(f's{i+2}') for i in range(aggr_layer_switches)]
        edge_layer = [self.addSwitch(f's{i+6}') for i in range(edge_layer_switches)]
	
        #adding links between core layer <-> aggregation layer, aggregation layer <-> edge layer, edge layer <-> hosts
        for i in range(num_of_hosts):
            if i < aggr_layer_switches:
            	self.addLink(core, aggr_layer[i], bw=agr_to_core_bw, delay='1ms')
            if i < edge_layer_switches:
            	self.addLink(aggr_layer[i//2], edge_layer[i], bw=agr_to_edge_bw, delay='1ms')
            self.addLink(hosts[i], edge_layer[i//2], bw=edge_to_host_bw, delay='1ms')
            

#source = source, sink = destination, _type [1 = web search, 2 = data mining], intensity = flows/s, gen_time = duration 
traffic_types = {1:{'name':'web search', 'flow':80000},2:{'name':'data mining', 'flow':1100}} 

def evaluation(_type, gen_time):  
    print(f'doing: data_{traffic_types[_type]["name"]}_ate-{agr_to_edge_bw}_atc-{agr_to_core_bw}')
    count = 0
    result = [[]]*10 
    for k in range(10):
        for i in range(1,11):
            t1, t2 = getRandomHosts()
            before_time = time.time() 
            flow_time_list, total_data = genIperf(f'h{t1}',f'h{t2}', _type, i, gen_time)
            after_time = time.time()  
            result[i-1] = result[i-1] + flow_time_list
            count += 1
            print(f" count: {count}, avg time: {round(np.mean(flow_time_list), 4)}; min {round(min(flow_time_list), 4)}; max {round(max(flow_time_list), 4)}, total data: {round(total_data, 4)} MB, real time: {round(after_time - before_time, 4)}\n")
    np_list = np.array(result, dtype=object)
    np.save(f'data_{traffic_types[_type]["name"]}_ate-{agr_to_edge_bw}_atc-{agr_to_core_bw}', np_list)	

def genIperf(source = None, sink = None, _type =None, intensity = None, gen_time = None):
    gen_func = webCDF if _type == 1 else dataCDF
    
    print(f"{source} -> {sink}", file=sys.stderr)
    source_node = net.get(source)
    sink_node = net.get(sink)
    sink_ip = sink_node.IP()
    num_of_flows = gen_time*intensity
    
    subprocess.getoutput("rm ./iperflog.txt")
    if(debug):
    	print(f"total flows: {num_of_flows}")
    	
    print(f'running command: iperf -s -P {num_of_flows} -f m -o iperflog.txt &')
    sink_node.cmd(f'iperf -s -P {num_of_flows} -f m -o iperflog.txt &') 
    iperfcmd = "iperf -c {} -n {}K &"

    total_flow_size = 0
    for i in range(gen_time):
        for k in range(intensity):
            flow_size = gen_func(_type)
            total_flow_size += flow_size
            print(f"running command: {iperfcmd.format(sink_ip, flow_size)}")
            source_node.cmd(iperfcmd.format(sink_ip, flow_size))
        time.sleep(1) # wait 1s 

    if(debug):
    	print(f"waiting for senders to finish, total data to send:{total_flow_size/1000}Mb over {num_of_flows} flows")
    sink_node.cmd("wait") 

    iperf_out = subprocess.getoutput("grep -v 'SUM' iperflog.txt | grep -e '[1-9]] [0-9]'")
    times = []
    data_sent = 0
    for lines in iperf_out.split('\n'):
        times.append(float(re.findall("[0-9]+\.?[0-9]*", lines)[2]))
        
        temp       = float(re.findall("[0-9]+\.?[0-9]*", lines)[3])
        if re.search("Kbytes", lines):
            data_sent += temp/1000
        elif re.search("Gbytes", lines):
            data_sent += temp*1000
        else:
            data_sent += temp
    return times, data_sent             

#The different types of distributions from normal data traffic of a data center network flow, returns a flow size
def dataCDF(_):
	return math.ceil(np.interp(random.random(),y_data,x_data)/1000)
	
def webCDF(_):
	return math.ceil(np.interp(random.random(),y_web,x_web)/1000)
		
def expCDF(_type):
	mean_flow = traffic_types[_type]['flow']
	return math.ceil(np.random.default_rng().exponential(mean_flow)/1000)


def getRandomHosts():
	return random.sample(list(range(1,17)), 2)


parser = argparse.ArgumentParser(description='Generates and executes data center traffic on mininet.')
parser.add_argument('-e2h_bw',nargs = '*', help ='Sets the bandwidth between the edge layer switches and hosts in Mbps, default 20', type = int, default=[20])
parser.add_argument('-a2e_bw',nargs = '*', help ='Sets the bandwidth between the aggregation layer switches and the edge layer switches in Mbps, default 20', type = int , default=[20])
parser.add_argument('-c2a_bw',nargs = '*', help ='Sets the bandwidth between the aggregation layer switches and the core layer switch in Mbps, default 20', type = int , default=[20])
parser.add_argument('-d',action = 'store_true', help ='Sets debug mode active')
parser.add_argument('-t', nargs = '?', type = int, default = 10, help ='Sets the generation time, default time is 10s')
args = parser.parse_args()



if(args.d):
	print(args)
	debug = True
	setLogLevel('info')
	
if(not len(args.e2h_bw) == len(args.a2e_bw) == len(args.c2a_bw)):
	print('Bandwidth arguments must be of equal length')
	exit()
	
for i in range(len(args.e2h_bw)):
	edge_to_host_bw = args.e2h_bw[i]
	agr_to_core_bw = args.a2e_bw[i]
	agr_to_edge_bw = args.c2a_bw[i]
	topos = MyTopo()
	net = Mininet(topos, link=TCLink)
	net.start()
	evaluation(1,args.t)
	evaluation(2,args.t)
	net.stop()  
