import os
import gc
import re
import subprocess
import signal
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import xlwt
from config import MAX_TIME, OUTPUT_MCS

# return 0(memory out); 1(time out); 2(successful) 
def helper(limit_time, output_file, current_xls_line, ws):
	if OUTPUT_MCS:
		command = "/usr/bin/time -v ./xftar script_with_output.xml > "+output_file
	else:
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
		ws.write(current_xls_line, 3, int(module_num.split(" ")[-1]))	

		ws.write(current_xls_line, 5, user_time + system_time)
		ws.write(current_xls_line, 6, memory)
		return 2

def process(branch_dir, branch_name):
	wb = xlwt.Workbook(encoding = 'ascii')
	ws = wb.add_sheet('My Worksheet')
	ws.write(0,0,"Benchmark")
	ws.write(0,3,"#Module")
	ws.write(0,4,"#prime imp")
	ws.write(0,5,"Time(s)")
	ws.write(0,6,"Memory(K)")
	xls_line = 0   
	if OUTPUT_MCS:
		raw = open("script_with_output.xml", "r")
	else:
		raw = open("script.xml", "r")
	file_context = raw.read()
	root = ET.fromstring(file_context)
	output = ""
	statistic = "Benchmark #Module #prime imp  Time(s) Memory(K)\n"

	branch_dir_path = branch_dir + "/" + branch_name
	output_dir_path = branch_dir + "/output/" + branch_name 
	for roots,dirs,files in os.walk(branch_dir_path):
		break
	for dir_name in dirs:
		print(dir_name)
		root.getchildren()[0].getchildren()[0].set("input", branch_dir_path + "/" + dir_name + "/" + dir_name + ".xml")
		root.getchildren()[0].getchildren()[1].set("input", branch_dir_path + "/" + dir_name + "/" + dir_name + "-basic-events.xml")
		if OUTPUT_MCS:
			root.getchildren()[3].getchildren()[0].set("output", output_dir_path + "/" + dir_name + "/" + dir_name + ".mcs")
		rough_string = ET.tostring(root, 'utf-8')
		reared_content = minidom.parseString(rough_string)
		if OUTPUT_MCS:
			with open("script_with_output.xml", 'w') as fs:
				reared_content.writexml(fs, addindent=" ")
		else:
			with open("script.xml", 'w') as fs:
				reared_content.writexml(fs, addindent=" ")			
		code = helper(MAX_TIME, output_dir_path + "/" + dir_name + "/tmp_output", xls_line+1, ws)
		xls_line += 1
		ws.write(xls_line, 0, dir_name)
		if code == 2 and OUTPUT_MCS:
			line_count = os.popen("wc " + output_dir_path + "/" + dir_name + "/" + dir_name + ".mcs -l")
			line_tmp = line_count.read().split(" ")[0]
			ws.write(xls_line, 4, int(line_tmp))

	wb.save(output_dir_path + "/" + 'xftar_result.xls')  
