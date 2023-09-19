from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import setLogLevel
import math 
import numpy as np
import random
import subprocess
import re

x_web = [0,10_000, 20_000,30_000,50_000,80_000,200_000, 1_000_000, 2_000_000,5_000_000, 10_000_000,30_000_000]	
y_web = [0., 0.18, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98, 1.]
x_data = [0,180,216,560,900,1_100,1_870, 3_160, 10_000, 400_000, 3_160_000, 100_000_000, 1_000_000_000]
y_data = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ,0.97, 0.99, 1.]

edge_to_host_bw = 20
agr_to_core_bw = 20
agr_to_edge_bw = 20

gen_func = None
debug = False

class MyTopo( Topo  ):
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
def genDCTraffic(source = None, sink = None, _type =None, intensity = None, gen_time = None):
    if not _type in traffic_types:
    	print("error type doesn't exist")
 
    source_node = net.get(source)
    source_ip = source_node.IP()
    sink_node = net.get(sink)
    sink_ip = sink_node.IP()

    
    if debug:
    	print(f'Simulating traffic of type: {traffic_types[_type]["name"]}')
    	print(f'From:{source} {source_ip} to {sink} {sink_ip}')
    	print(f'{intensity} flows/s')
    	print(f'For duration: {gen_time} seconds')

    sink_node.cmd('ITGRecv &')
    makeScript(sink_ip,intensity,gen_time, _type)
    command = f'ITGSend script.txt -x recv.log'	
    #print(command)
    source_node.cmd(command)
    sink_node.cmd('kill %ITGRecv')
    
def evaluation(_type):
	print(f'doing: data_{traffic_types[_type]["name"]}_ate-{agr_to_edge_bw}_atc-{agr_to_core_bw}')
	count = 0
	result = np.full(shape = [10,10], fill_value = 0.)
	for k in range(10):
		t1, t2 = getRandomHosts()
		for i in range(1,11):
			genDCTraffic(f'h{t1}',f'h{t2}', _type, i, 10)
			time = subprocess.getoutput("ITGDec recv.log | grep 'Total time' | tail -1")
			result[k][i-1]= float(re.search("[0-9]+.?[0-9]*",time)[0])
			count += 1
			print(count)
	np.save(f'data_{traffic_types[_type]["name"]}_ate-{agr_to_edge_bw}_atc-{agr_to_core_bw}', result)	

def dataCDF(_):
	return math.ceil(np.interp(random.random(),y_data,x_data)/1000)
	
def webCDF(_):
	return math.ceil(np.interp(random.random(),y_web,x_web)/1000)
	
def expCDF(_type):
	mean_flow = traffic_types[_type]['flow']
	return math.ceil(np.random.default_rng().exponential(mean_flow)/1000)
	
def makeScript(sink_ip, intensity, gen_time, traffic_type):
	test = '-T TCP -a {} -rp {} -k {} -d {} -C 10000000\n'
	flow_size = 0
	delay = -1
	script_file = ""
	port = 10_000
	for i in range(intensity * gen_time):
		if i % intensity == 0:
			delay += 1
		flow_size = gen_func(traffic_type)
		script_file += test.format(sink_ip, port, flow_size, delay*1_000)
		port += 1
	f = open('script.txt', "w")
	f.write(script_file)	

def getRandomHosts():
	t1 = random.randint(1,16)
	while True:
		t2 = random.randint(1,16)
		if not t1 == t2:
			break 
	return t1, t2

# setLogLevel('info')

edge_to_host_bw = 20
agr_to_core_bw = 20
agr_to_edge_bw = 20 

gen_func = dataCDF 
# data 20
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
# CLI(net)
evaluation(2)
net.stop()
 
gen_func = webCDF  
# web 20
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
evaluation(1)
net.stop()
 
agr_to_edge_bw = 80 
gen_func = dataCDF 
# data 80
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
evaluation(2)
net.stop()
 
gen_func = webCDF  
# web 80
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
evaluation(1)
net.stop()


agr_to_core_bw = 160
agr_to_edge_bw = 80 
gen_func = dataCDF 
# data 80 anb 160
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
evaluation(2)
net.stop()
 
gen_func = webCDF  
# web 80 anb 160
topos = MyTopo()
net = Mininet(topos, link=TCLink)
net.start()
evaluation(1)
net.stop()
