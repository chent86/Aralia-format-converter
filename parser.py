import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import xlwt
import sys
from tools import node, node_helper

def parse(branch_dir, branch_name):
    branch_path = branch_dir + "/" + branch_name
    branch_output_path = branch_dir + "/output/" + branch_name
    os.system("mkdir " + branch_output_path)
    operator_tag = {"|":"or", "&":"and", "#":"xor", "-":"not"}

    wb = xlwt.Workbook(encoding = 'ascii')
    ws = wb.add_sheet('My Worksheet')         
    ws.write(0,1,"#Event")
    ws.write(0,2,"#Gate")
    xls_line = 0  

    for root, dirs, files in os.walk(branch_path):
        break

    for dir_name in dirs:
        output_dir_path = branch_output_path + "/" + dir_name
        os.system("mkdir " + output_dir_path)
        file_name = dir_name + "/" + dir_name + ".dag"
        print(file_name)
        file_path = branch_path + "/" + file_name
        helper = node_helper()
        helper.parser(file_path)
        open_psa = ET.Element("open-psa")
        define_fault_tree = ET.SubElement(open_psa, "define-fault-tree")
        define_fault_tree.set("name", "r1")

        visited_set = set()
        xml_helper(helper.root_node, define_fault_tree, visited_set)

        rough_string = ET.tostring(open_psa, 'utf-8')
        reared_content = minidom.parseString(rough_string)
        new_file_name = branch_path + "/" + dir_name + "/" + dir_name + ".xml"
        with open(new_file_name, 'w') as fs:
            reared_content.writexml(fs, addindent=" ", newl="\n")

        xls_line += 1
        ws.write(xls_line, 0, file_name[:len(file_name)-4])
        ws.write(xls_line, 1, helper.basic_num)
        ws.write(xls_line, 2, helper.gate_num)
        basic_open_psa = ET.Element("open-psa")
        basic_define_fault_tree = ET.SubElement(basic_open_psa, "define-fault-tree")
        basic_define_fault_tree.set("name", "test")
        for n in helper.node_dict.values():
            if not n.children:
                define_basic_event = ET.SubElement(basic_define_fault_tree, "define-basic-event")
                define_basic_event.set("name", n.name)
                ET.SubElement(define_basic_event, "float").set("value", "1")
        rough_string = ET.tostring(basic_open_psa, 'utf-8')
        reared_content = minidom.parseString(rough_string)
        new_file_name = branch_path + "/" + dir_name + "/" + dir_name + "-basic-events.xml"
        with open(new_file_name, 'w') as fs:
            reared_content.writexml(fs, addindent=" ", newl="\n")

    wb.save(branch_output_path + "/" + "parse_result.xls")

def xml_helper(cur_node, define_fault_tree, visited_set):
    if cur_node.name in visited_set:
        return
    else:
        visited_set.add(cur_node.name)
    define_gate = ET.SubElement(define_fault_tree, "define-gate")
    define_gate.set("name", cur_node.name)
    gate_type = ET.SubElement(define_gate, cur_node.gate_type)
    for child in cur_node.children:
        if cur_node.sign[child.name] == 0:
            event = ET.SubElement(gate_type, "event")
            event.set("name", child.name)
        else:
            not_gate = ET.SubElement(gate_type, "not")
            event = ET.SubElement(not_gate, "event")
            event.set("name", child.name)
        if child.children:
            xml_helper(child, define_fault_tree, visited_set)