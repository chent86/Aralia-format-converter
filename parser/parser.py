import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import xlwt

operator_tag = {"|":"or", "&":"and", "#":"xor", "-":"not"}

wb = xlwt.Workbook(encoding = 'ascii')
ws = wb.add_sheet('My Worksheet')         
ws.write(0,1,"#Event")
ws.write(0,2,"#Gate")
xls_line = 0  

os.system("rm ../result/*")

for root,dirs,files in os.walk("../raw"):
    break

for file_name in files:
    print(file_name)
    raw = open("../raw/"+file_name, "r")
    open_psa = ET.Element("open-psa")
    define_fault_tree = ET.SubElement(open_psa, "define-fault-tree")
    top_event = "r1"
    basic_event = set()
    root_set = set()
    not_in_one_line = 0
    last_line = ""
    is_annotation = 0 # 一片注释
    xo = 0 # 为xor新增加的门
    for line in raw:
        # 处理空行
        if len(line) == 1:
            continue
        # 处理注释
        if line[0] == "/":
            if line[len(line)-2] != "/":
                is_annotation = 1
            continue
        if is_annotation == 1:
            if line[len(line)-2] != "/":
                continue
            else:
                is_annotation = 0
                continue
        # 处理未在一行的情况
        if line[len(line)-2] != ";": # 最后一个字符是\n
            last_line += line
            not_in_one_line = 1
            continue
        if not_in_one_line == 1:
            not_in_one_line = 0
            line = last_line+line
            last_line = ""
        length = len(line)
        root = ""
        operator = "&"
        cur = ""
        i = 0
        flag = 0 # 是否是atleast
        num = ""
        cur_list = []
        # 读取门的名称
        for i in range(0, length-1):
            if line[i] == " " or line[i] == ":":
                break
            root += line[i]
        root_set.add(root)
        while i < length-1:
            if line[i] == "=":
                i = i+1
                while line[i] == "(" or line[i] == " ":
                    i = i+1
                # 处理 1、a := b 2、a := (b&c) 3、 a := @(3,[b,c])
                if line[i] == "@":
                    i = i+1
                    while line[i] == "(" or line[i] == " ":
                        i = i+1
                    flag = 1
                break
            i = i+1
        if flag == 0:
            while i < length:
                if line[i] == "&" or line[i] == "|" or line[i] == "#":
                    operator = line[i]
                    cur_list.append(cur)
                    cur = ""
                    i = i+1
                    continue
                if line[i] == ")" or line[i] == ";":
                    # if cur[0] == "-":
                    #     operator = "-"
                    #     cur = cur[1:len(cur)]
                    cur_list.append(cur)
                    cur = ""
                    break
                if line[i] != " ":
                    cur += line[i]
                i = i+1
            define_gate = ET.SubElement(define_fault_tree, "define-gate")
            define_gate.set("name", root)
            if operator != "":
                if operator != "#":
                    gate_type = ET.SubElement(define_gate, operator_tag[operator])
                    for event_name in cur_list:
                        # if event_name == "":
                        #     continue
                        if event_name[0] != '-':
                            event = ET.SubElement(gate_type, "event")
                            event.set("name", event_name)
                            if event_name[0]!='g':
                                basic_event.add(event_name)
                        else:
                            not_gate = ET.SubElement(gate_type, "not")
                            event = ET.SubElement(not_gate, "event")
                            event.set("name", event_name[1:len(event_name)])
                            if event_name[1] != 'g':
                                basic_event.add(event_name[1:len(event_name)])
                else: # 临时处理xor(只是两项等)
                    xo += 1
                    name1 = "xo"+str(xo)
                    xo += 1
                    name2 = "xo"+str(xo)
                    or_gate = ET.SubElement(define_gate, "or")
                    xor_gate_1 = ET.SubElement(or_gate, "event")
                    xor_gate_1.set("name", name1)
                    xor_gate_2 = ET.SubElement(or_gate, "event")
                    xor_gate_2.set("name", name2)           

                    define_gate = ET.SubElement(define_fault_tree, "define-gate")
                    define_gate.set("name", name1)
                    and_gate_1 = ET.SubElement(define_gate, "and")
                    not_gate_1 = ET.SubElement(and_gate_1, "not")
                    event = ET.SubElement(not_gate_1, "event")
                    event.set("name", cur_list[0])
                    event = ET.SubElement(and_gate_1, "event")
                    event.set("name", cur_list[1])

                    define_gate = ET.SubElement(define_fault_tree, "define-gate")
                    define_gate.set("name", name2)
                    and_gate_2 = ET.SubElement(define_gate, "and")
                    not_gate_2 = ET.SubElement(and_gate_2, "not")
                    event = ET.SubElement(not_gate_2, "event")
                    event.set("name", cur_list[1])
                    event = ET.SubElement(and_gate_2, "event")
                    event.set("name", cur_list[0])
        else:
            while i < length:
                if line[i] == "," or line[i] == " ":
                    break
                num += line[i]
                i = i+1
            while line[i] != "[":
                i = i+1
            i = i+1
            while line[i] == " ":
                i = i+1
            while i < length:
                if line[i] == ",":
                    cur_list.append(cur)
                    cur = ""
                    i = i+1
                    continue
                if line[i] == "]":
                    cur_list.append(cur)
                    cur = ""
                    break
                if line[i] != " ":
                    cur += line[i]
                i = i+1
            define_gate = ET.SubElement(define_fault_tree, "define-gate")
            define_gate.set("name", root)
            gate_type = ET.SubElement(define_gate, "atleast")
            gate_type.set("min", num)
            for event_name in cur_list:
                if event_name[0] != '-':
                    event = ET.SubElement(gate_type, "event")
                    event.set("name", event_name)
                    if event_name[0]!='g':
                        basic_event.add(event_name)
                else:
                    not_gate = ET.SubElement(gate_type, "not")
                    event = ET.SubElement(not_gate, "event")
                    event.set("name", event_name[1:len(event_name)])
                    if event_name[1] != 'g':
                        basic_event.add(event_name[1:len(event_name)])
    raw.close()

    define_fault_tree.set("name", top_event)
    rough_string = ET.tostring(open_psa, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    new_file_name = "../result/"+file_name
    with open(new_file_name[0:len(new_file_name)-3]+"xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ", newl="\n")

    real_basic_count = 0
    real_basic_event = set()
    for event in basic_event:
        if event not in root_set:
            real_basic_count += 1
            real_basic_event.add(event) #确保basic_event不是gate_event
    basic_event = real_basic_event
    # 包括为xor额外添加的门

    xls_line += 1
    ws.write(xls_line, 0, file_name[0:len(file_name)-4])
    ws.write(xls_line, 1, str(real_basic_count))
    ws.write(xls_line, 2, str(len(root_set)+xo))
    basic_open_psa = ET.Element("open-psa")
    basic_define_fault_tree = ET.SubElement(basic_open_psa, "define-fault-tree")
    basic_define_fault_tree.set("name", "test")
    for event in basic_event:
        define_basic_event = ET.SubElement(basic_define_fault_tree, "define-basic-event")
        define_basic_event.set("name", event)
        ET.SubElement(define_basic_event, "float").set("value", "1")
    rough_string = ET.tostring(basic_open_psa, 'utf-8')
    reared_content = minidom.parseString(rough_string)
    new_file_name = "../result/"+file_name
    with open(new_file_name[0:len(new_file_name)-4]+"-basic-events.xml", 'w') as fs:
        reared_content.writexml(fs, addindent=" ", newl="\n")

wb.save('statistic.xls') 



