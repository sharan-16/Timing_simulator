LS SR1 SR0 0 
LS SR2 SR0 1 
LS SR3 SR0 2 
LS SR5 SR0 3 
LS SR7 SR0 4 
LV VR0 SR3
ADD SR3 SR3 SR2 
LV VR1 SR3
ADD SR3 SR3 SR2 
LV VR2 SR3
ADD SR3 SR3 SR2 
LV VR3 SR3
AND SR3 SR3 SR0 
MTCL SR2
LV VR4 SR4 
ADD SR4 SR4 SR2 
LV VR5 SR4 
ADD SR4 SR4 SR2 
LV VR6 SR4 
ADD SR4 SR4 SR2 
LV VR7 SR4 
MULVV VR4 VR4 VR0
MULVV VR5 VR5 VR1
MULVV VR6 VR6 VR2
MULVV VR7 VR7 VR3
ADDVV VR4 VR4 VR5
ADDVV VR6 VR6 VR7
ADDVV VR4 VR4 VR6
LS SR6 SR0 1
SV VR4 SR0
SRL SR6 SR6 SR5
MTCL SR6
LV VR5 SR6 
ADDVV VR4 VR4 VR5
BGT SR6 SR5 -5
LS SR1 SR3 5 
ADDVS VR4 VR4 SR1
LS SR1 SR0 0 
SV VR4 SR7
ADD SR7 SR7 SR5	 
ADD SR3 SR3 SR5
BLT SR3 SR1 -28
HALT
