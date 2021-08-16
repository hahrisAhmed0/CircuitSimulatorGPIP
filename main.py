import csv
import random
import graphviz
from graphviz import Digraph
# Circuit file with test addition 
# Hahris Ahmed GPIP Summer 2021
# Class used to store information for a wire
class Node(object):
    def __init__(self, name, value, gatetype, innames):
        self.name = name         # string
        self.value = value        # char: '0', '1', 'U' for unknown
       #self.faulty = value
        self.gatetype = gatetype    # string such as "AND", "OR" etc
        self.interms = []     # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them ("ab")
        self.is_input = False    # boolean: true if this wire is a primary input of the circuit
        self.is_output = False   # boolean: true if this wire is a primary output of the circuit

    def set_value(self, v):
        self.value = v 
    
    def getName(self):
        return self.name
    def getValue(self):
        return self.value
    def getGatetype(self):
        return self.gatetype
    def getInnames(self):
        return self.innames
    def isInput(self):
        return self.is_input
    def isOutput(self):
        return self.is_output
    

        

    def display(self):     # print out the node nicely on one line
        
        if self.is_input:
            # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}" 
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}" 
            print(nodeinfo)
            return 
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:               # internal nodes   
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name)+" "
            interm_val_str += str(i.value)+" "

        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"

        print(nodeinfo)
        return 

    # calculates the value of a node based on its gate type and values at interms
    def calculate_value(self):

        for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
            if i.value != "0" and i.value !="1":
                return "U"

        if self.gatetype == "AND":
            val = "1"
            for i in self.interms:
                if i.value == "0":
                    val = "0"
            self.value = val
            return val
        elif self.gatetype == "OR":
            val = "0"
            for i in self.interms:
                if i.value == '1':
                    val = "1"
            self.value = val
            return val
        elif self.gatetype == "NAND":
            flag = "1"
            for i in self.interms:
                if i.value == "0":
                    flag = "0"
            val = str(1-int(flag))
            self.value = val
            return val
        elif self.gatetype == "NOT":
            val = self.interms[0].value
            self.value = str(1-int(val))
            return val
        elif self.gatetype == "XOR":
            num_of_1 = 0
            for i in self.interms:
                if i.value == "1":
                    num_of_1 = num_of_1 + 1
            val = num_of_1 % 2
            val = str(val)
            self.value = val
            return val
        elif self.gatetype == "XNOR":
            num_of_1 = 0
            for i in self.interms:
                if i.value == "1":
                    num_of_1 = num_of_1 + 1
            val = num_of_1 % 2
            self.value = str(1-val)
            return val
        elif self.gatetype == "NOR":
            flag = "0"
            for i in self.interms:
                if i.value == "1":
                    flag = "1"
            val = str(1-int(flag))
            self.value = val
            return val
        elif self.gatetype == "BUFF":
            val = self.interms[0].value
            self.value = val
            return val



# Take a line from the circuit file which represents a gatetype operation and returns a node that stores the gatetype

def parse_gate(rawline):
# example rawline is: a' = NAND(b', 256, c')

# should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

    # get rid of all spaces
    line = rawline.replace(" ", "")
    # now line = a'=NAND(b',256,c')

    name_end_idx = line.find("=")
    node_name = line[0:name_end_idx]
    # now node_name = a'

    gt_start_idx = line.find("=") + 1
    gt_end_idx = line.find("(")
    node_gatetype = line[gt_start_idx:gt_end_idx]
    # now node_gatetype = NAND

    # get the string of interms between ( ) to build tp_list
    interm_start_idx = line.find("(") + 1
    end_position = line.find(")")
    temp_str = line[interm_start_idx:end_position]
    tp_list = temp_str.split(",")
    # now tp_list = [b', 256, c]

    node_innames = [i for i in tp_list]
    # now node_innames = [b', 256, c]

    return node_name, node_gatetype, node_innames


# Create circuit node list from input file
def construct_nodelist():
    o_name_list = []

    for line in input_file_values:
        if line == "\n":
            continue

        if line.startswith("#"):
            continue

        # TODO: clean this up
        if line.startswith("INPUT"):
            index = line.find(")")
            # intValue = str(line[6:index])
            name = str(line[6:index])
            n = Node(name, "U", "PI", [])
            n.is_input = True
            node_list.append(n)


        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)


        else:   # majority of internal gates processed here
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "U", node_gatetype, node_innames)
            node_list.append(n)

    # now mark all the gates that are output as is_output
    for n in node_list:
        if n.name in o_name_list:
            n.is_output = True


    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    for node in node_list:
        for cur_name in node.innames:
            for target_node in node_list:
                if target_node.name == cur_name:
                    node.interms.append(target_node)

    return 

#to generate random binary string
def rand_key(p):
  key1 = ""
  for i in range(p):
    temp = str(random.randint(0,1))
    key1+=temp
  return (key1)

def readInput(node_list, input_list, output_list, input_val, output_val, output_val_stats, randomBinary, isRandom):
  #input_list = []
  output_list = []
  input_val = []
  output_val = []
  # Clear all nodes values to U in between simulation runs
  for node in node_list:
        node.set_value("U")

  strindex = 0
    # Set value of input node
  for node in node_list:
        if node.is_input:
            if strindex > len(randomBinary)-1:
                break
            node.set_value(randomBinary[strindex])
            strindex = strindex + 1

  print("simulating with the following input values:")

  for node in node_list:
        if node.is_input:
            node.display()
    
  print("--- Begin simulation: ---")


    # simulation by trying calculating each node's value in the list
  updated_count = 1       #initialize to 1 to enter while loop at least once
  iteration = 0
  while updated_count > 0:
        updated_count = 0
        iteration += 1
        for n in node_list:
            if n.value == "U":
                n.calculate_value()
                if n.value == "0" or n.value == "1":
                    updated_count +=1
            if isRandom == False :
              n.display()
        if isRandom == False :
          print (f'--- iteration {iteration} finished: updated {updated_count} values--- ')


  print("\n--- Simulation results: ---")

  input_list= [i.name for i in node_list if i.is_input]
  
  input_val = [i.value for i in node_list if i.is_input]

  print("input: \t", end="")
  print(*input_list, end = "")
  print("\t = \t", end = "")
  print(*input_val)

  output_list = [i.name for i in node_list if i.is_output]
  output_val = [i.value for i in node_list if i.is_output]
  output_val_stats += output_val

  print("output:\t", end="")
  print(*output_list, end = "")
  print("\t = \t", end = "")
  print(*output_val)
  print ("\n")
  print ("\n")
  return node_list, input_list, output_list, input_val, output_val, output_val_stats
    

# TODO: make a circuit class, containing a nodelist, display function, and simulation method.


# Main function starts

# Step 1: get circuit file name from command line
wantToInputCircuitFile = str(
    input("Provide a benchfile name (return to accept circuit.bench by default):\n"))

if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
        f = open(circuitFile)
        f.close()
    except FileNotFoundError:
        print('File does not exist, setting circuit file to default')
        circuitFile = "circuit.bench"
else:
    circuitFile = "circuit.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
node_list = []
construct_nodelist()
# printing list of constructed nodes
for n in node_list:
    n.display()

# for n in node_list 
# gates/input/output are node's node name and gatetype, and innames(inputs), if it's primary input, if it's primary output

# dot = Digraph(comment = 'Circuit')
# for n in node_list:
#     dot.node(n.getValue(), n.getName())
# for n in node_list:
#   if (n.isInput()==False and n.isOutput()==False):
#     dot.edge(n.getInnames(),n.getName())
#    print(n.getInnames)
#   elif  n.isOutput()==True:
#     dot.edge(n.getInnames(),n.getName())
#     print(n.getInnames)

# print (dot.source)

# dot.render('test-output/round-table.gv.pdf', view=True)
# 'test-output/round-table.gv.pdf'

print ("---------------")

# Analysis to CSV file
print(" Random Input Analysis? Type Y or N")
answer = input()
if answer == "Y" :
      print("You pressed Y !\n")
      print("How many runs?")
      runs = int(input())
      print('\n')
      filename = circuitFile[0:len(circuitFile)-6] + "_" + str(runs) + ".csv"
      with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        isRandom = True
        input_list = []
        output_list = []
        output_val_stats = []
        input_val = []
        output_val = []
        headerList = []
        headerList.append("I/O")
        x = 0
        y = 0
        sizeOutputList = 0
        sizeInputList = 0
        print ("**TEST RUN\n")
        node_list, input_list, output_list, input_val, output_val, output_val_stats = readInput(node_list, input_list, output_list, input_val, output_val,output_val_stats, "1010", isRandom)
        
        for i in output_list:
          sizeOutputList+=1
        for i in input_list:
          sizeInputList+=1
        output_val_stats = []
        input_val = []
        output_val = []
       # print("Input List Size is:" , sizeInputList)
        
        while x < len(input_list):
          headerList.append("I")
          x+=1
        while y < len(output_list):
          headerList.append("O")
          y+=1
        
        csvwriter.writerow(headerList)
        newList = input_list + output_list
        newList.insert(0,"run")
        csvwriter.writerow(newList)
        list0Count = []
        list1Count = []
        list0CountO = []
        list1CountO = []
        repeatedOutput = []
        for x in range(sizeInputList):
          list0Count.append(0)
        for x in range(sizeInputList):
          list1Count.append(0)
        
        for x in range(sizeOutputList):
          list0CountO.append(0)
        for x in range(sizeOutputList):
          list1CountO.append(0)
        n = 1
        while n < runs+1:
          newVal = []
          randomBinary = rand_key(sizeInputList)
          message = "**RUN" + str(n)
          print (message)
          print ("\n")
          node_list, input_list, output_list, input_val, output_val, output_val_stats = readInput(node_list,input_list,   output_list, input_val, output_val, output_val_stats, randomBinary, isRandom)
          index = 0
          
          for i in input_val:
            if i == "0" :
             list0Count[index]+=1
            elif i == "1":
             list1Count[index]+=1
            index+=1
          index = 0
          for i in output_val:
            if i == "0" :
             list0CountO[index]+=1
            elif i == "1":
             list1CountO[index]+=1
            index+=1
          
          repeatedOutput.append(output_val)
          newVal = input_val + output_val
          newVal.insert(0, str(n))
          csvwriter.writerow(newVal)
          n+=1
        index = 0

        print("**VALUES IN INPUT BITS**\n")
        for i in input_list:
          print("0 Count in "+ i + ":")
          print(list0Count[index])
          print("1 Count in "+ i + ":")
          print(list1Count[index])
          print("\n")
          index+=1
       
        index = 0
        print("**VALUES IN OUTPUT BITS**\n")
        for i in output_list:
          print("0 Count in "+ i + ":")
          print(list0CountO[index])
          print("1 Count in "+ i + ":")
          print(list1CountO[index])
          print("\n")
          index = index + 1
       
        counter = 0
        num = repeatedOutput[0]

        for i in repeatedOutput:
          curr_frequency = repeatedOutput.count(i)
          if(curr_frequency>counter):
            counter = curr_frequency
            num = i
       
        print("Most common output is: " , num)

        
        zeroCount = 0
        OneCount = 0
        for i in output_val_stats :
          if i == "0" :
            zeroCount+=1
          elif i == "1" :
            OneCount+=1
      

        if OneCount == zeroCount :
          print("Balanced Output!")
        else :
          print("Unbalanced Output.")
      

    
line_of_val = input("Start simulation with input values (return to exit):\n")

isRandom = False
while True :
  if len(line_of_val)==0 :
    break
  node_list, input_list, output_list, input_val, output_val, output_val_stats = readInput(node_list, input_list, output_list, input_val, output_val, output_val_stats, line_of_val, isRandom)
  line_of_val = input("Start simulation with input values (return to exit):\n")
print(f"Finished - bye!")