from parser import parse
from xftar import process
import os

def run(branch_name):
    print("===================== " + branch_name + " parse stage  =====================")
    parse("example", branch_name)
    print("===================== " + branch_name + " xftar stage  =====================")
    process("example", branch_name)


if __name__ == '__main__':
    os.system("rm -rf example/output")
    os.system("mkdir example/output")
    run("ft")
