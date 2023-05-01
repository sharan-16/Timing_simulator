import os
import argparse
class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.strip() for ins in insf.readlines()]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)

    def Read(self, idx): # Use this to read from DMEM.
        #print("AISH "+str(self.size)+">"+str(idx))
        if idx < self.size:
                #print("AISH "+str(self.data[idx]))
                return self.data[idx]
        pass # Replace this line with your code here.

    def Write(self, idx, val): # Use this to write into DMEM.
        #print("Write"+str(val))
        self.data[idx] = val
        pass # Replace this line with your code here.

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

class TMEM(object):
    def __init__(self, name, iodir, addressLen, data):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = data
        
    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        #print ("AISH read" + str(idx)+" "+str(self.registers))
        return self.registers[idx]
        pass # Replace this line with your code.

    def Write(self, idx, val):
        for e in range(len(val)):
            self.registers[idx][e] = val[e]
        pass # Replace this line with your code.

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)

class Core():
    def __init__(self, imem, sdmem, vdmem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem

        self.PC = 0
        self.branch = False
        self.maskreg = [True]*64
        self.VLR = 64 #vector length register

        #self.LS_flag = False
        self.RegW = False

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}
                    
        self.timing_data = []
        self.t_idx = 0
        
        # Your code here.
        
    def decode(self):
        instr = self.IMEM.Read(self.PC)
        #print("AISH "+instr)
        parsed_instr = instr.split(" ")
        #print("AISH" + str(len(parsed_instr)))
        parsed_instr_final = [None] * 4
        for i in range(4):
            if i<len(parsed_instr):
                parsed_instr_final[i] = parsed_instr[i]
        return parsed_instr_final
    
    def read_RF(self,idx):
        #print("AISH" + str(self.RFs['SRF']))
        #print("idx"+str(idx))
        if 'VR' in idx:
            return self.RFs['VRF'].Read(int(idx.replace('VR','')))
        elif 'SR' in idx:
            return self.RFs['SRF'].Read(int(idx.replace('SR','')))
        else: 
            imm = [int(idx)]  #for immediate values
            return imm

    def write_RF(self,idx, val):
        if 'VR' in idx:
            self.RFs['VRF'].Write(int(idx.replace('VR','')), val)
        elif 'SR' in idx:
            self.RFs['SRF'].Write(int(idx.replace('SR','')), val)
        
    def execute_V(self, operand0, operand1, operand2, opcode, instr):
        result=[0]*self.VLR
        if (opcode == 'ADDVV'): 
            self.RegW = True
            for i in range(self.VLR):
                result[i]=((operand1[i]+operand2[i])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'ADDVS'):  
            self.RegW = True
            for i in range(self.VLR):
               result[i]=((operand1[i]+operand2[0])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'SUBVV'):  
            self.RegW = True
            for i in range(self.VLR):
                result[i]=((operand1[i]-operand2[i])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'SUBVS'):  
            self.RegW = True
            for i in range(self.VLR):
               result[i]=((operand1[i]-operand2[0])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'MULVV'):  
            self.RegW = True
            for i in range(self.VLR):
               result[i]=((operand1[i]*operand2[i])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'MULVS'):  
            self.RegW = True
            for i in range(self.VLR):
               result[i]=((operand1[i]*operand2[0])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'DIVVV'):  
            self.RegW = True
            for i in range(self.VLR):
               result[i]=int((operand1[i]/operand2[i])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif (opcode == 'DIVVS'): 
            self.RegW = True 
            for i in range(self.VLR):
               result[i]=int((operand1[i]/operand2[0])*self.maskreg[i])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            self.t_idx=self.t_idx+1
        elif ('S' in opcode and 'VV' in opcode): 
            self.mask_reg_opVV(opcode,operand0,operand1)
            return None
        elif ('S' in opcode and 'VS' in opcode):  
            self.mask_reg_opVS(opcode,operand0,operand1)
            return None
        elif (opcode == 'LV'):  
            self.RegW = True
            operand1_list = [];
            for i in range(self.VLR):
                #print("i="+str(i)+"self.VLR="+str(self.VLR)+"operand1[0]="+str(operand1[0])+"self.maskreg[i]="+str(self.maskreg[i])+"\n")
                result[i]=(self.VDMEM.Read(operand1[0]+i))*self.maskreg[i]
                operand1_list.append(operand1[0]+i)
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ",""))
            self.t_idx=self.t_idx+1
        elif (opcode == 'SV'):
            operand1_list = []
            for i in range(self.VLR):
                self.VDMEM.Write((operand1[0]+i), operand0[i]*self.maskreg[i])
                operand1_list.append(operand1[0]+i)
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ","")) 
            self.t_idx=self.t_idx+1
            return None
        elif (opcode == 'LVWS'):  
            self.RegW = True
            #print("operands"+ str(self.VLR)+" "+str(operand1)+" "+str(operand2)+" "+str(self.maskreg))
            operand1_list = []
            for i in range(self.VLR):
                result[i]=((self.VDMEM.Read(operand1[0]+i*operand2[0]))*self.maskreg[i])
                operand1_list.append(operand1[0]+i*operand2[0])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ","")) 
        elif (opcode == 'SVWS'):
            operand1_list=[]
            for i in range(self.VLR):
                self.VDMEM.Write((operand1[0]+i*operand2[0]), operand0[i]*self.maskreg[i])
                operand1_list.append(operand1[0]+i*operand2[0])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ",""))
            return None
        elif (opcode == 'LVI'):  
            self.RegW = True
            operand1_list=[]
            for i in range(self.VLR):
                result[i]=(self.VDMEM.Read(operand1[0]+operand2[i])*self.maskreg[i])
                operand1_list.append(operand1[0]+i*operand2[0])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ",""))
        elif (opcode == 'SVI'):
            #print("operands"+ str(self.VLR)+" "+str(operand1)+" "+str(operand2)+" "+str(self.maskreg)+" "+str(operand0))
            operand1_list=[]
            for i in range(self.VLR):
                self.VDMEM.Write((operand1[0]+operand2[i]), operand0[i]*self.maskreg[i])
                operand1_list.append(operand1[0]+i*operand2[0])
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(operand1_list).replace(" ",""))
            return None
        elif (opcode == 'CVM'): 
            self.maskreg = [True]*64
            return None
        return result

    def mask_reg_opVV(self, condition, operand1, operand2):
        #print("operands"+ str(self.VLR)+" "+str(operand1)+" "+str(operand2)+" "+str(self.maskreg))
        if(condition == 'SEQVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]==operand2[i])
        elif(condition == 'SNEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]!=operand2[i])
        elif(condition == 'SGTVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]>operand2[i])
        elif(condition == 'SLTVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]<operand2[i])
        elif(condition == 'SGEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]>=operand2[i])
        elif(condition == 'SLEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]<=operand2[i])

    def mask_reg_opVS(self, condition, operand1, operand2):
        if(condition == 'SEQVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]==operand2)
        elif(condition == 'SNEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]!=operand2)
        elif(condition == 'SGTVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]>operand2)
        elif(condition == 'SLTVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]<operand2)
        elif(condition == 'SGEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]>=operand2)
        elif(condition == 'SLEVV'):
            for i in range(self.VLR):
                self.maskreg[i] = (operand1[i]<=operand2)

        
    def execute_S(self,operand0, operand1,operand2, opcode, instr):
        #print("opcode"+opcode) 
        if (opcode == 'POP'):
            self.RegW = True
            return [sum(self.maskreg)]
        elif (opcode == 'MTCL'): 
            print(str(opcode)+" "+str(operand0))
            self.VLR = operand0
            return None
        elif (opcode == 'MFCL'):
            print(str(opcode)+" "+str(operand0))
            self.RegW = True
            print(self.VLR)
            return [self.VLR] 
        elif (opcode == 'LS'):
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str((operand1+operand2)))
            return [self.SDMEM.Read(operand1+operand2)]
        elif (opcode == 'SS'):
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str((operand1+operand2)))
            self.SDMEM.Write(operand1+operand2, operand0)
            return None
        elif (opcode == 'ADD'):
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            return [operand1 + operand2]
        elif (opcode == 'SUB'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            return [operand1 - operand2]
        elif (opcode == 'AND'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            return [operand1 & operand2]
        elif (opcode == 'OR'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            return [operand1 | operand2]
        elif (opcode == 'XOR'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2])+" "+str(instr[3]))
            return [operand1 ^ operand2]
        elif (opcode == 'SLL'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2]))
            return [int(operand1*(2*(operand2)))]
        elif (opcode == 'SRL'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2]))
            return [int(operand1/(2*(operand2)))]
        elif (opcode == 'SRA'):  
            self.RegW = True
            self.timing_data.append(str(opcode)+" "+str(instr[1])+" "+str(instr[2]))
            return [int(operand1/(2*(operand2)))]
            pass
        
    def branch_func(self, condition, operand1, operand2, operand3):
        if(condition == 'BEQ'):
            if(operand1 == operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 == operand2) else self.PC + 1)
        elif(condition == 'BNE'):
            #print("AISH" + str(operand1) + str(operand2))
            if(operand1 != operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 != operand2) else self.PC + 1)
        elif(condition == 'BGT'):
            if(operand1 > operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 > operand2) else self.PC + 1)
        elif(condition == 'BLT'):
            if(operand1 < operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 < operand2) else self.PC + 1)
        elif(condition == 'BGE'):
            if(operand1 >= operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 >= operand2) else self.PC + 1)
            
        elif(condition == 'BLE'):
            if(operand1 <= operand2):
                self.timing_data.append("B ("+str(self.PC+operand3)+")")
            return(self.PC + operand3 if (operand1 <= operand2) else self.PC + 1)

    def run(self):
        while(True):

            #instruction fetch and decode
            instr = self.decode()
            opcode = instr[0]
            #print("AISH instr" + str(instr))
            #print("AISH opcode" + opcode)
            rd = [0] * 64
            rs1 = [0] * 64
            rs2 = [0] * 64
            if instr[1] is None:
                rd = [0] * 64
            else:
                #print("AISh"+str(self.read_RF(instr[1])))
                rd = self.read_RF(instr[1])

            if instr[2] is None:
                rs1 = [0] * 64
            else:
                rs1 = self.read_RF(instr[2])

            if instr[3] is None:
                rs2 = [0]
            else:
                rs2 = self.read_RF(instr[3])

            if(opcode == 'HALT'):
                break
            
            if(opcode.startswith('B')):
                #print(opcode, rd[0], rs1[0], rs2[0])
                self.PC = self.branch_func(opcode, rd[0], rs1[0], rs2[0]) 
            else:        
                self.PC = self.PC + 1

            #if ('B__' in opcode ):
            #    next_PC = self.PC + self.read_RF(instr['r3']) if (self.read_RF(instr['r1']) > instr.read_RF(instr['r2'])) else self.PC + 1
            #    # need to expand to the other six cases
            #    continue
            #elif(opcode == 'HALT') : break

            ##reading the values
            #operand1 = self.read_RF(instr['r2'])
            #operand2 = self.read_RF(instr['r3'])
            #
            operand0 = rd
            operand1 = rs1
            operand2 = rs2
            #print("AISH operand0"+str(operand0))
            #print("AISH operand1"+str(operand1))
            #print("AISH operand2"+str(operand2))
            print("opcode"+opcode) 

            if ('V' in opcode): 
                result = []
                result = self.execute_V(operand0,operand1,operand2,opcode, instr)
                #print("AISH result" + str(result))
            else:
                result = []
                result = self.execute_S(operand0[0],operand1[0],operand2[0],opcode, instr)
                #print("AISH result" + str(result))

            ##write to the register files and clear the flag
            if(result != None and self.RegW == True): self.write_RF(instr[1], result)
            self.RegW = False

            ##increment the program counter if no exception is encountered
            #self.PC = next_PC



    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 20) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 
    


    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem)

    # Run Core
    vcore.run()   
    vcore.dumpregs(iodir)

    sdmem.dump()
    vdmem.dump()
    vcore.timing_data.append("HALT")
    tmem = TMEM("TMEM",iodir, 30, vcore.timing_data)
    tmem.dump()
    #print("Timing_data"+str(vcore.timing_data))

    # THE END
