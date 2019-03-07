import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

operator_tag = {"|":"or", "&":"and"}

for root,dirs,files in os.walk("../raw"):
    break
for file_name in files:
    print(file_name)
    if file_name == "edfpa15o.dag" or file_name == "edfpa15q.dag" or file_name == "das9601.dag":
        continue
    raw = open("../raw/"+file_name, "r")
    open_psa = ET.Element("open-psa")
    define_fault_tree = ET.SubElement(open_psa, "define-fault-tree")
    top_event = ""
    basic_event = set()
    not_in_one_line = 0
    last_line = ""
    for line in raw:
        if line[len(line)-2] != ";":
            last_line += line
            not_in_one_line = 1
            continue
        if not_in_one_line == 1:
            not_in_one_line = 0
            line = last_line+line
            last_line = ""
        # print(line)
        length = len(line)
        root = ""
        operator = ""
        cur = ""
        i = 0
        flag = 0 # 是否是atleast
        num = ""
        cur_list = []
        for i in range(0, length-1):
            if line[i] == " " or line[i] == ":":
                break
            root += line[i]
        while i < length-1:
            if line[i] == "=":
                if line[i+2] == "(" or line[i+2] == "@": # 处理 1、a := b 2、a := (b&c) 3、 a := @(3,[b,c])
                    i = i+2
                    if line[i] == "@":
                        i = i+2
                        flag = 1
                else:
                    i = i+1
                break
            if line[i] == "/":
                top_event = root
            i = i+1
        if flag == 0:
            while i < length:
                i = i+1
                if line[i] == " ":
                    operator = line[i+1]
                    i = i+2
                    cur_list.append(cur)
                    cur = ""
                    continue
                if line[i] == ")" or line[i] == ";":
                    cur_list.append(cur)
                    cur = ""
                    break
                cur += line[i]
            define_gate = ET.SubElement(define_fault_tree, "define-gate")
            define_gate.set("name", root)
            if operator != "":
                gate_type = ET.SubElement(define_gate, operator_tag[operator])
                for event_name in cur_list:
                    if event_name == "":
                        continue
                    if event_name[0] != "-":
                        event = ET.SubElement(gate_type, "event")
                        event.set("name", event_name)
                        if event_name[0]=="e":
                            basic_event.add(event_name)
                    else:
                        not_gate = ET.SubElement(gate_type, "not")
                        event = ET.SubElement(not_gate, "event")
                        event.set("name", event_name)
                        if event_name[1]=="e":
                            basic_event.add(event_name[1:len(event_name)])
        else:
            while i < length:
                if line[i] == ",":
                    break
                num += line[i]
                i = i+1
            while i < length:
                if line[i] == "[":
                    i = i+1
                    break
                i = i+1
            while i < length:
                if line[i] == ",":
                    cur_list.append(cur)
                    cur = ""
                    i = i+2
                    continue
                if line[i] == "]":
                    cur_list.append(cur)
                    cur = ""
                    break
                cur += line[i]
                i = i+1
            define_gate = ET.SubElement(define_fault_tree, "define-gate")
            define_gate.set("name", root)
            gate_type = ET.SubElement(define_gate, "atleast")
            gate_type.set("min", num)
            for event_name in cur_list:
                if event_name[0] != "-":
                    event = ET.SubElement(gate_type, "event")
                    event.set("name", event_name)
                    if event_name[0]=='e':
                        basic_event.add(event_name)
                else:
                    not_gate = ET.SubElement(gate_type, "not")
                    event = ET.SubElement(not_gate, "event")
                    event.set("name", event_name)
                    if event_name[1]=="e":
                        basic_event.add(event_name[1:len(event_name)])                    
    raw.close()

    define_fault_tree.set("name", top_event)
    rough_string = ET.tostring(open_psa, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    new_file_name = "../result/"+file_name
    with open(new_file_name[0:len(new_file_name)-3]+"xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ", newl="\n")


    basic_open_psa = ET.Element("open-psa")
    basic_define_fault_tree = ET.SubElement(basic_open_psa, "define-fault-tree")
    basic_define_fault_tree.set("name", "test")
    for event in basic_event:
        define_basic_event = ET.SubElement(basic_define_fault_tree, "define-basic-event")
        define_basic_event.set("name", event)
        ET.SubElement(define_basic_event, "float").set("value", "0.01")
    rough_string = ET.tostring(basic_open_psa, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    new_file_name = "../result/"+file_name
    with open(new_file_name[0:len(new_file_name)-4]+"-basic-events.xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ", newl="\n")

