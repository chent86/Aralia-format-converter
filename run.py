from parser import parse
from xftar import process
import os

def run(branch_name):
    print("===================== " + branch_name + " parse stage  =====================")
    parse(branch_name)
    print("===================== " + branch_name + " xftar stage  =====================")
    process(branch_name)


if __name__ == '__main__':
    os.system("rm -rf example/output")
    os.system("mkdir example/output")
    run("ft")
    run("qg6")
    run("test")
