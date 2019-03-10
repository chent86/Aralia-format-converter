import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re
import subprocess
import collections
import xlwt

wb = xlwt.Workbook(encoding = 'ascii')
ws = wb.add_sheet('My Worksheet')         
ws.write(0,0,"Benchmark")
ws.write(0,3,"#Module")
ws.write(0,4,"#prime imp")
ws.write(0,5,"Time(s)")
ws.write(0,6,"Memory(K)")
xls_line = 0   
# wb.save('test.xls')  


os.system("rm -rf xftar_result")
os.system("mkdir xftar_result")
raw = open("script.xml", "r")
file_context = raw.read()
root = ET.fromstring(file_context)
output = ""
statistic = "Benchmark #Module #prime imp  Time(s) Memory(K)\n"

for roots,dirs,files in os.walk("../raw"):
    break

file_list = [
            #  "baobab1.dag",
            #  "baobab2.dag",
            #  "baobab3.dag",
            # # "cea9601.dag",
            #  "chinese.dag",
            #  "das9201.dag",
            #  "das9202.dag",
            #  "das9203.dag",
            #  "das9204.dag",
            #  "das9205.dag",
            #  "das9206.dag",
            #  "das9207.dag",
            #  "das9208.dag",
            # #  "das9209.dag",
            #  "das9601.dag",
            # # segmentation "das9701.dag",
            #  "edf9201.dag",
            #  "edf9202.dag",
            # #  "edf9203.dag",
            # #  "edf9204.dag",
            #  "edf9205.dag",
            # #  "edf9206.dag",
            # #  "edfpa14b.dag",
            # #  "edfpa14o.dag",
            #  "edfpa14p.dag",
            # #  "edfpa14q.dag",
            #  "edfpa14r.dag",
            #  "edfpa15b.dag",
            #  "edfpa15o.dag",
            #  "edfpa15p.dag",
            #  "edfpa15q.dag",
            #  "edfpa15r.dag",
            #  "elf9601.dag",
            #  "ftr10.dag",
            #  "isp9601.dag",
            #  "isp9602.dag",
            #  "isp9603.dag",
            #  "isp9604.dag",
            #  "isp9605.dag",
            #  "isp9606.dag",
            #  "isp9607.dag",
            #  "jbd9601.dag",
            # #  "nus9601.dag"

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
    line_tmp = line_count.read().split(" ")[0]
    statistic += file_name+ " " +\
                    module_num.split(" ")[-1] + " " + \
                    line_tmp + " " + \
                    str(float(user_time.split(" ")[-1])+float(system_time.split(" ")[-1])) + " " + \
                    resident_size.split(" ")[-1] + "\n"
    xls_line += 1
    ws.write(xls_line, 0, file_name)
    ws.write(xls_line, 3, module_num.split(" ")[-1])
    ws.write(xls_line, 4, line_tmp)
    ws.write(xls_line, 5, str(float(user_time.split(" ")[-1])+float(system_time.split(" ")[-1])))
    ws.write(xls_line, 6, resident_size.split(" ")[-1])

statistic_file = open("statistic", "w")
statistic_file.write(statistic)
statistic_file.close()
wb.save('statistic.xls')  

