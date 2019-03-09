import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re
import subprocess
import collections

os.system("rm -rf xftar_result")
os.system("mkdir xftar_result")
raw = open("script.xml", "r")
file_context = raw.read()
root = ET.fromstring(file_context)
output = ""
statistic = ""

for roots,dirs,files in os.walk("../raw"):
    break

for file_name in files:
    if file_name == "das9701.dag" or file_name == "das9601.dag":
        continue
    file_name = file_name[0:len(file_name)-4]
    print(file_name)
    root.getchildren()[0].getchildren()[0].set("input", "../result/"+file_name+".xml")
    root.getchildren()[0].getchildren()[1].set("input", "../result/"+file_name+"-basic-events.xml")
    root.getchildren()[3].getchildren()[0].set("output", "xftar_result/"+file_name)
    # root.getchildren()[4].getchildren()[0].set("output", "xftar_result/"+file_name+"/pr")
    # root.getchildren()[4].getchildren()[1].set("output", "xftar_result/"+file_name+"/if")

    rough_string = ET.tostring(root, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    with open("script.xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ")

    DEVNULL = open(os.devnull, 'wb', 0)
    p = subprocess.Popen(['/usr/bin/time', '-v'] + 
          ['./xftar', 'script.xml'], stdout=DEVNULL, stderr=subprocess.PIPE)
    with p.stderr:
        q = collections.deque(iter(p.stderr.readline, b''))
    rc = p.wait()
    time_output = b''.join(q).decode().strip()

    r = os.popen("/usr/bin/time -v ./xftar script.xml")
    cmd_output = r.read()
    pattern = r"#Gates.*[0-9]*"
    gate_num = re.findall(pattern, cmd_output)[-1]
    pattern = r"#BE.*[0-9]*"
    basic_event_num = re.findall(pattern, cmd_output)[-1]
    pattern = r"#Modules.*[0-9]*"
    module_num = re.findall(pattern, cmd_output)[-1]
    pattern = r'User time.*[0-9\.]*'
    user_time = re.findall(pattern, time_output)[0]
    pattern = r'System time.*[0-9\.]*'
    system_time = re.findall(pattern, time_output)[0]
    pattern = r'Maximum resident set size.*[0-9]*'
    resident_size = re.findall(pattern, time_output) [0]
    line_count = os.popen("wc xftar_result/"+file_name+" -l")
    statistic += file_name+ " " +\
                 line_count.read().split(" ")[0] + " " + \
                 gate_num.split(" ")[-1] + " " + \
                 basic_event_num.split(" ")[-1] + " " + \
                 module_num.split(" ")[-1] + " " + \
                 user_time.split(" ")[-1] + " " + \
                 system_time.split(" ")[-1] + " " + \
                 resident_size.split(" ")[-1] + "\n"

statistic_file = open("statistic", "w")
statistic_file.write(statistic)
statistic_file.close()

