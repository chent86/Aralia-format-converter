from parser import parse
from xftar import process
import os

def run(branch_name):
    os.system("rm -rf output")
    os.system("mkdir output")
    print("=====================  parse stage  =====================")
    parse(branch_name)
    print("=====================  xftar stage  =====================")
    process(branch_name)


if __name__ == '__main__':
    run("raw")
