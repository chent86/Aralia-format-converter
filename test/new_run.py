import os
import gc
import re
import subprocess
import signal
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import xlwt

# return 0(memory out); 1(time out); 2(successful) 
def helper(limit_time, output_file, current_xls_line):
	command = "/usr/bin/time -v ./xftar script.xml > "+output_file

	gc.collect()
	p = subprocess.Popen(command, preexec_fn = os.setsid, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	begin_time = time.time()
	is_err = False
	while p.poll() == None:
		now_time = time.time()
		if (now_time - begin_time) > limit_time :
			print('Time out')
			ws.write(current_xls_line, 5, 'Time out')
			is_err = True
			# print 'kill: '+str(p.pid)
			os.killpg(p.pid, signal.SIGTERM)
			break
		else:
			time.sleep(1)

	if is_err:
		return 1
	else:
		statistics = p.stderr.readlines()

		user_time = 0.0
		system_time = 0.0
		memory = 0

		for line in statistics:
			if 'User time (seconds)'.encode('utf-8') in line:
				pattern='[0-9]+.[0-9]+'.encode('utf-8')
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'.encode('utf-8')
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				user_time = float(next(words))
			if 'System time (seconds)'.encode('utf-8') in line:
				pattern='[0-9]+.[0-9]+'.encode('utf-8')
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'.encode('utf-8')
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				system_time = float(next(words))
			if 'Maximum resident set size'.encode('utf-8') in line:
				pattern = '[0-9]+'.encode('utf-8')
				words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				memory = int(next(words))

		
		output = []
		f = open(output_file, 'r')
		for line in f:
			output.append(line)
		f.close()

		# memory out
		if len(output) == 0:
			print('Memory out')
			ws.write(current_xls_line, 6, 'Memory out')
			return 0
		
		cmd_output = ""
		for i in output:
			cmd_output += i
		pattern = r"#Modules.*[0-9]*"
		module_num = re.findall(pattern, cmd_output)[-1]
		ws.write(current_xls_line, 3, module_num.split(" ")[-1])	

		ws.write(current_xls_line, 5, str(user_time + system_time))
		ws.write(current_xls_line, 6, str(memory))
		return 2


wb = xlwt.Workbook(encoding = 'ascii')
ws = wb.add_sheet('My Worksheet')         
ws.write(0,0,"Benchmark")
ws.write(0,3,"#Module")
ws.write(0,4,"#prime imp")
ws.write(0,5,"Time(s)")
ws.write(0,6,"Memory(K)")
xls_line = 0   

file_list = [
             "baobab1.dag",
             "baobab2.dag",
             "baobab3.dag",
            "cea9601.dag",
             "chinese.dag",
             "das9201.dag",
             "das9202.dag",
             "das9203.dag",
             "das9204.dag",
             "das9205.dag",
             "das9206.dag",
             "das9207.dag",
             "das9208.dag",
             "das9209.dag",
             "das9601.dag",
            "das9701.dag",
             "edf9201.dag",
             "edf9202.dag",
             "edf9203.dag",
             "edf9204.dag",
             "edf9205.dag",
             "edf9206.dag",
             "edfpa14b.dag",
             "edfpa14o.dag",
             "edfpa14p.dag",
             "edfpa14q.dag",
             "edfpa14r.dag",
             "edfpa15b.dag",
             "edfpa15o.dag",
             "edfpa15p.dag",
             "edfpa15q.dag",
             "edfpa15r.dag",
             "elf9601.dag",
             "ftr10.dag",
             "isp9601.dag",
             "isp9602.dag",
             "isp9603.dag",
             "isp9604.dag",
             "isp9605.dag",
             "isp9606.dag",
             "isp9607.dag",
             "jbd9601.dag",
             "nus9601.dag"

            "cea9601.dag",
             "das9209.dag",
             "edf9203.dag",
             "edf9204.dag",
             "edf9206.dag",
             "edfpa14b.dag",
             "edfpa14o.dag",
             "edfpa14q.dag",
             "nus9601.dag"
            ]

os.system("rm -rf xftar_result")
os.system("mkdir xftar_result")
raw = open("script.xml", "r")
file_context = raw.read()
root = ET.fromstring(file_context)
output = ""
statistic = "Benchmark #Module #prime imp  Time(s) Memory(K)\n"

for roots,dirs,files in os.walk("../raw"):
    break

# for file_name in files:
for file_name in file_list:
    # file_name = "chinese.dag"
	print(file_name)
	file_name = file_name[0:len(file_name)-4]
	root.getchildren()[0].getchildren()[0].set("input", "../result/"+file_name+".xml")
	root.getchildren()[0].getchildren()[1].set("input", "../result/"+file_name+"-basic-events.xml")
	root.getchildren()[3].getchildren()[0].set("output", "xftar_result/"+file_name)
	rough_string = ET.tostring(root, 'utf-8')
	reared_content = minidom.parseString(rough_string)
	with open("script.xml", 'w') as fs:
		reared_content.writexml(fs, addindent=" ")    
	code = helper(3600, "tmp_output", xls_line+1)
	xls_line += 1
	ws.write(xls_line, 0, file_name)
	if code == 2:
		line_count = os.popen("wc xftar_result/"+file_name+" -l")
		line_tmp = line_count.read().split(" ")[0]
		ws.write(xls_line, 4, line_tmp)

wb.save('statistic.xls')  
