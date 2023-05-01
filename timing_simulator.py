import os
import argparse
from queue import Queue

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "TMEMOP.txt"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.strip() for ins in insf.readlines()]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)

    def Read(self, idx): # Use this to read from IMEM.
        #print("Instr"+str(self.instructions));
        if idx < self.size:
            return self.instructions[idx]
        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class Instr():
    def __init__(self):
        self.instr_type =  None # scalar/vector comp or memory op
        self.exe_time = [0]*3
        self.regs_used = []*4
        self.mems = Queue(maxsize=64)
        self.ls_element_flags = []

class vls_Memory():
    def __init__(self, access_time):
        #all parameters from config file
        self.banks = 16
        self.bank_busy = [0]*16 # all banks are intially free and need to check before issuing the request
        self.bank_access_count = [access_time]*16
        self.access_time = access_time 

    def issue_request(self, bank_no):
       self.bank_access_count[bank_no] = self.access_time
       self.bank_busy[bank_no] = 1 #set busy
       #self.bank_access_count[bank_no] = self.access_time

    def bank_execute_one_cycle(self):
        for i in range(0,self.banks):
            if self.bank_busy[i] != 0:
                self.bank_access_count[i] = self.bank_access_count[i] - 1 if (self.bank_access_count[i] - 1) > 0 else 0
                if self.bank_access_count[i] == 0 : 
                    self.bank_busy[i] = 0
        print(f"accesss times - {self.bank_access_count}")
        print(f"bank busy -     {self.bank_busy}")


class arch_state():
    def __init__(self, a, b, c):
        self.IMEM = None
        self.PC = 0
        #all parameters from config file
        self.data_queue_depth = a
        self.comp_queue_depth = b
        self.num_lanes = c
        

        #busy boards
        self.busy_board = []
        self.busy_lanes = [0]*self.num_lanes
        self.vls_busy_lanes = [0]*self.num_lanes
        #self.ls_element_flags = []

        #arch state
        self.WB = Instr()
        self.vcomp_exe = [Instr()]*self.num_lanes
        self.vls_exe = [Instr()]*self.num_lanes
        self.scalar_exe = Instr()
        self.decode = Instr()
        self.fetch = Instr()

        self.vls_queue = Queue(maxsize=self.data_queue_depth)
        self.vcomp_queue = Queue(maxsize=self.comp_queue_depth)
        self.scalar_queue = Queue(maxsize=1)

        #pipline flags
        self.pipeline_busy = 0
        #self.mem_busy = 0

    def shift(self):


        #WB stage --> udating the busy board, busy lanes and 
        #clear the busy board --> empty list
        

        
        #shifting into queues
        #print(f"check busy board - {self.busy_board}, regs used {self.decode.regs_used}")
        #print(f"check - {not(self.decode.regs_used in self.busy_board)}")
        if not(self.vls_queue.full()) and (self.decode.instr_type == 'v_ls') and not(set(self.decode.regs_used) & set(self.busy_board)):
            self.vls_queue.put(Vmips.decode)
            self.pipeline_busy = 0
        elif not(self.vcomp_queue.full()) and self.decode.instr_type == 'v_comp' and not(set(self.decode.regs_used) & set(self.busy_board)):
            self.vcomp_queue.put(Vmips.decode)
            self.pipeline_busy = 0
            #print('*'*14 + self.vcomp_queue.queue[0])
        elif not(self.scalar_queue.full()) and self.decode.instr_type == 'scalar' and not(set(self.decode.regs_used) & set(self.busy_board)):
            self.scalar_queue.put(Vmips.decode)
            self.pipeline_busy = 0
        elif self.decode.instr_type == None:
            self.pipeline_busy = 0
        else:
            self.pipeline_busy = 1
        #popping from queues
        for i in range(0,self.num_lanes):
            if self.busy_lanes[i] == 0 and not(self.vcomp_queue.empty()):
                #if not(self.vcomp_queue.queue[0].regs_used in self.busy_board):
                self.vcomp_exe[i] = self.vcomp_queue.get()
                #print('*'*14 + self.vcomp_exe[i].instr_type)
        for i in range(0,self.num_lanes):
            if self.vls_exe[i].exe_time[2] == 0 and not(self.vls_queue.empty()):
                #if not(self.vls_queue.queue[0].regs_used in self.busy_board):
                self.vls_exe[i] = self.vls_queue.get()
        if self.scalar_exe.exe_time[2] == 0 and not(self.scalar_queue.empty()):
            self.scalar_exe = self.scalar_queue.get()


        #decode stage
        if self.fetch.exe_time[0] == 0 and not(self.pipeline_busy):
            self.decode = self.fetch
        if self.decode.instr_type == 'HALT':
            global Halt_condition
            Halt_condition = 1
            self.pipeline_busy = 1

        #fetch stage
        if not(self.pipeline_busy):
            Instr = self.IMEM.Read(self.PC)
            #print("*"*8+Instr)
            self.fetch = decode(Instr)
            self.PC = self.PC + 1

    def execute_one_cycle(self):
        #execution stage
        #v comp 
        #for i in range(0,self.num_lanes):
        #    self.vcomp_exe[i].exe_time[2] = self.vcomp_exe[i].exe_time[2] - 1 if self.vcomp_exe[i].exe_time[2] - 1 > 0 else 0

        #vls
        for i in range(0,self.num_lanes):
            self.vcomp_exe[i].exe_time[2] = self.vcomp_exe[i].exe_time[2] - 1 if self.vcomp_exe[i].exe_time[2] - 1 > 0 else 0

            if self.vls_busy_lanes[i] == 1 and not(self.vls_exe[i].mems.empty()):
                #print(f"check check - {self.vls_exe[i].mems.queue[0]}")
                if self.vls_exe[i].exe_time[2] == 4 and vls_mem.bank_busy[self.vls_exe[i].mems.queue[0]] == 0:
                    vls_mem.issue_request(self.vls_exe[i].mems.get())
                else:
                    self.vls_exe[i].exe_time[2] = self.vls_exe[i].exe_time[2] - 1 if self.vls_exe[i].exe_time[2] - 1 > 4 else 4
            elif self.vls_exe[i].mems.empty():
                self.vls_exe[i].exe_time[2] = self.vls_exe[i].exe_time[2] - 1 if self.vls_exe[i].exe_time[2] - 1 > 0 else 0
        vls_mem.bank_execute_one_cycle()
        self.scalar_exe.exe_time[2] = self.scalar_exe.exe_time[2]-1 if self.scalar_exe.exe_time[2]-1>0 else 0
        #self.vls_exe[i].exe_time[2] = self.vls_exe[i].exe_time[2] - 1 if self.vls_exe[i].exe_time[2] - 1 > 0 else 0

        self.decode.exe_time[1] = self.decode.exe_time[1] - 1 if self.decode.exe_time[1] - 1 > 0 else 0
        self.fetch.exe_time[0] = self.fetch.exe_time[0] - 1 if self.fetch.exe_time[0] - 1 > 0 else 0

        self.busy_board.clear()
        for i in range(0,self.num_lanes):
            #print('check exe time, {}' .format(self.vcomp_exe[i].exe_time[2]))
            if self.vcomp_exe[i].exe_time[2] == 0:
                #print(self.busy_lanes)
                self.busy_lanes[i] = 0
            else:
                self.busy_lanes[i] = 1
                self.busy_board = list(set().union(set(self.vcomp_exe[i].regs_used), set(self.busy_board)))
            if self.vls_exe[i].exe_time[2] == 0:
                self.vls_busy_lanes[i] = 0
            else:
                self.vls_busy_lanes[i] = 1
                self.busy_board = list(set().union(set(self.vls_exe[i].regs_used), set(self.busy_board)))
        
        #if self.vls_exe[i].exe_time == 0:
        #        pass # do nothing the exe comlted instr is overwritten by a new one
        #else:
        #    self.busy_board = list(set().union(set(self.vls_exe[i].regs), set(self.busy_board)))

        if self.scalar_exe.exe_time[2] == 0:
                pass
        else:
            self.busy_board = list(set().union(set(self.scalar_exe.regs_used), set(self.busy_board)))

mul_pipe_depth = 12
add_pipe_depth = 2
div_pipe_depth = 8
num_banks = 1
vls_pipe_depth = 1
program_counter = 0
Halt_condition = 0

def decode(instr=str):
    instr = instr.split(' ')
    #print(instr[0])
    if ('VV' in instr[0]) or ('VS' in instr[0]) or ("MTCL" in instr[0]) or ("MFCL" in instr[0]):
        a = Instr()
        a.instr_type = 'v_comp'
        a.exe_time[0] = 1 #fetch
        a.exe_time[1] = 1 #decode
        #a.exe_time[3] = 1 #WB

        if ('ADD' in instr[0]) or ('SUB' in instr[0]):
            a.exe_time[2] = add_pipe_depth
        elif 'MUL' in instr[0]:
            a.exe_time[2] = mul_pipe_depth
        elif 'DIV' in instr[0]:
            a.exe_time[2] = div_pipe_depth
        else:
            a.exe_time[2] = 1
        a.regs_used = instr[1:] # registers used
    elif ('LV' in instr[0]) or ('SV' in instr[0]):
        a = Instr()
        a.instr_type = 'v_ls'
        a.exe_time = [1,1,vls_pipe_depth + 5]
        #print(instr[-1][1:-1])
        temp =  list(map(int, instr[-1][1:-1].split(',')))
        #temp = temp
        [a.mems.put(k%16) for k in temp]#
        a.regs_used = instr[1:-1] # registers used
        a.ls_element_flags = [0]*len(temp)
    elif "HALT" == instr[0]:
        a = Instr()
        a.instr_type = 'HALT'
    elif (None == instr[0]) or 'None' == instr[0]:
        a = Instr()
        #a.instr_type = 'HALT'
    else:
        a = Instr()
        a.instr_type = 'scalar'
        a.exe_time = [1,1,1]
        a.regs_used = instr[1:] # registers used
        #print("Aish"+str(instr))
    return a

#def vls_time(q):
#    temp = [a%num_banks for a in q]
#   temp = Counter(temp).values()
#   return vls_pipe_depth + (max(list) - 1)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    #print("Imem="+str(imem[0]))
    Vmips = arch_state(4,4,4)
    Vmips.IMEM = imem
    vls_mem = vls_Memory(6)

    #Vmips.fetch = decode(instr)


    cycle_count = 0




    while(True):
        
        if (Halt_condition == 1 and Vmips.busy_lanes == [0]*Vmips.num_lanes and Vmips.vls_busy_lanes == [0]*Vmips.num_lanes and Vmips.scalar_exe.exe_time[2] == 0 
            and Vmips.vcomp_queue.empty() and Vmips.vls_queue.empty() and Vmips.scalar_queue.empty()):
            print('HALT Encountered')
            print(cycle_count)
            break


        #1st
        cycle_count = cycle_count + 1
        Vmips.shift()
        Vmips.execute_one_cycle()
        #Vmips.shift()
        print('#'*12)
        print(Vmips.fetch.instr_type, Vmips.fetch.exe_time, Vmips.decode.instr_type, Vmips.decode.exe_time)
        for i in range(0,Vmips.num_lanes):
            print(Vmips.vls_exe[i].instr_type, Vmips.vls_exe[i].exe_time[2])
            print(Vmips.vcomp_exe[i].instr_type, Vmips.vcomp_exe[i].exe_time[2])
        print("pipeline busy - {}".format(Vmips.pipeline_busy))
        print(Halt_condition)
        print(Vmips.busy_lanes == [0]*Vmips.num_lanes, Vmips.vls_busy_lanes == [0]* Vmips.num_lanes, Vmips.scalar_exe.exe_time[2] == 0 
                , Vmips.vcomp_queue.empty() , Vmips.vls_queue.empty() , Vmips.scalar_queue.empty())
        print(Vmips.busy_lanes, Vmips.vls_busy_lanes, Vmips.busy_board)

        if (Halt_condition == 1 and Vmips.busy_lanes == [0]*Vmips.num_lanes and Vmips.vls_busy_lanes == [0]*Vmips.num_lanes and Vmips.scalar_exe.exe_time[2] == 0 
            and Vmips.vcomp_queue.empty() and Vmips.vls_queue.empty() and Vmips.scalar_queue.empty()):
            print('HALT Encountered')
            print(cycle_count)
            break


    
    

    