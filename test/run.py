import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import subprocess

os.system("rm -rf xftar_result")
os.system("mkdir xftar_result")
raw = open("script.xml", "r")
file_context = raw.read()
root = ET.fromstring(file_context)
output = ""

for roots,dirs,files in os.walk("../raw"):
    break
for file_name in files:
    if file_name == "das9701.dag" or file_name == "das9601.dag":
        continue
    print(file_name)
    os.system("mkdir -p xftar_result/"+file_name[0:len(file_name)-4])
    root.getchildren()[0].getchildren()[0].set("input", "../result/"+file_name[0:len(file_name)-4]+".xml")
    root.getchildren()[0].getchildren()[1].set("input", "../result/"+file_name[0:len(file_name)-4]+"-basic-events.xml")
    root.getchildren()[3].getchildren()[0].set("output", "xftar_result/"+file_name[0:len(file_name)-4]+"/msc")
    root.getchildren()[4].getchildren()[0].set("output", "xftar_result/"+file_name[0:len(file_name)-4]+"/pr")
    root.getchildren()[4].getchildren()[1].set("output", "xftar_result/"+file_name[0:len(file_name)-4]+"/if")

    rough_string = ET.tostring(root, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    with open("script.xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ")
    # proc = subprocess.Popen(["./xftar", "script.xml"], stdout=subprocess.PIPE, shell=True)
    # (out, err) = proc.communicate()
    # output += out.decode("utf-8")
    os.system("./xftar script.xml")