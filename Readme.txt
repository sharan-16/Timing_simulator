File Descriptions:

1. ar7999_sa6951_funcsimulator : This is the functional simulator file that checks the functionality and also generates the trace.
   Run command for the dot prod: python .\ar7999_sa6951_funcsimulator.py --iodir .\dot_prod\
   Run command for the fully connected: python .\ar7999_sa6951_funcsimulator.py --iodir .\fully_connected\
  
2. timing_simulator : This is the timing simulator that uses the trace perviously generated and displays the total cycles to run the program on console.
   Run command for dot prod:  python .\timing_simulator.py --iodir .\dot_prod\
   Run command for fully connected : python .\timing_simulator.py --iodir .\fully_connected\

3. fully_connected 
	a. fully_connected_manual : This provides the explanation of code.asm program.
	b. TMEMOP.txt : This is the trace generated
	
	


