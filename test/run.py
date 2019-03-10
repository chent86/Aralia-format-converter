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
statistic = "Benchmark  #Event  #Gate   #Module #prime imp  Time(s) Memory(K)\n"

for roots,dirs,files in os.walk("../raw"):
    break

file_list = ["baobab3.dag",
             "chinese.dag",
             "das9201.dag",
             "das9202.dag",
             "das9203.dag",
             "das9204.dag",
             "das9205.dag",
             "das9206.dag",
             "das9207.dag",
             "das9208.dag",
             "edf9201.dag",
             "edf9202.dag",
             "edf9205.dag",
             "edfpa14p.dag",
             "edfpa14r.dag",
             "edfpa15b.dag",
             "edfpa15p.dag",
             "edfpa15r.dag",
             "elf9601.dag",
             "ftr10.dag",
             "isp9602.dag",
             "isp9603.dag",
             "isp9604.dag",
             "isp9606.dag",
             "isp9607.dag",
             "jbd9601.dag"
            ]

# for file_name in files:
for file_name in file_list:
    # file_name = "chinese.dag"
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
    print(cmd_output)
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
    # basic_event_num.split(" ")[-1] + " " + \
    # gate_num.split(" ")[-1] + " " + \
    statistic += file_name+ " " +\
                    module_num.split(" ")[-1] + " " + \
                    line_count.read().split(" ")[0] + " " + \
                    str(float(user_time.split(" ")[-1])+float(system_time.split(" ")[-1])) + " " + \
                    resident_size.split(" ")[-1] + "\n"

statistic_file = open("statistic", "w")
statistic_file.write(statistic)
statistic_file.close()

