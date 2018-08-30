#!/usr/bin/python3

REGISTERS = {
	0: 'zero',
	1: 'at',
	2: 'v0',
	3: 'v1',
	4: 'a0',
	5: 'a1',
	6: 'a2',
	7: 'a3',
	8: 't0',
	9: 't1',
	10: 't2',
	11: 't3',
	12: 't4',
	13: 't5',
	14: 't6',
	15: 't7',
	16: 's0',
	17: 's1',
	18: 's2',
	19: 's3',
	20: 's4',
	21: 's5',
	22: 's6',
	23: 's7',
	24: 't8',
	25: 't9',
	26: 'k0',
	27: 'k1',
	28: 'gp',
	29: 'sp',
	30: 's8',
	31: 'ra'
}

OPCODES = {
	0: {
		32: 'add',
		33: 'addu',
		36: 'and',
		37: 'or',
		39: 'nor',
		42: 'slt',
		43: 'sltu',
		34: 'sub',
		35: 'subu',
		38: 'xor',
		0: 'sll',
		4: 'sllv',
		3: 'sra',
		7: 'srav',
		2: 'srl',
		6: 'srlv',
    26: 'div',
    27: 'divu',
    16: 'mfhi',
    18: 'mflo',
    17: 'mthi',
    19: 'mtlo',
    24: 'mult',
    25: 'multu',
    13: 'break',
    9: 'jalr',
    8: 'jr',
    12: 'syscall'
	},

  32: 'lb',
  36: 'lbu',
  33: 'lh',
  37: 'lhu',
  35: 'lw',
  40: 'sb',
  41: 'sh',
  43: 'sw',
  
  2: 'j',
  3: 'jal',
  4: 'beq',
  5: 'bne',
  
  8: 'addi',
  9: 'addiu',
  12: 'andi',
  15: 'lui',
  13: 'ori',
  10: 'slti',
  11: 'sltiu',
  14: 'xori'
}

REGISTER_STATES = {}

def init_register_states():
  
  global REGISTER_STATES
  for x in range(32):
    REGISTER_STATES[x] = 0

def print_registers():
  
  global REGISTER_STATES
  global REGISTERS
  for key in REGISTER_STATES:
    print(REGISTERS[key] + ':\t' + str(REGISTER_STATES[key]), end='| ')
  print('\n')
  
def state_from_r_type(rs, rt, rd, shift, func):
  
  global REGISTER_STATES
  if func == 32 or func == 33:
    REGISTER_STATES[rd] = REGISTER_STATES[rs] + REGISTER_STATES[rt]
  elif func == 36:
    REGISTER_STATES[rd] = REGISTER_STATES[rs] & REGISTER_STATES[rt]
  elif func == 39:
    REGISTER_STATES[rd] = ~(REGISTER_STATES[rs] | REGISTER_STATES[rt])
  elif func == 37:
    REGISTER_STATES[rd] = REGISTER_STATES[rs] | REGISTER_STATES[rt]
  elif func == 42 or func == 43:
    REGISTER_STATES[rd] = 1 if REGISTER_STATES[rs] < REGISTER_STATES[rt] else 0
  elif func == 34 or func == 35:
    REGISTER_STATES[rd] = REGISTER_STATES[rs] - REGISTER_STATES[rt]
  elif func == 38:
    REGISTER_STATES[rd] = REGISTER_STATES[rs] ^ REGISTER_STATES[rt]
  elif func == 0:
    REGISTER_STATES[rd] = REGISTER_STATES[rt] << shift
  elif func == 4:
    REGISTER_STATES[rd] = REGISTER_STATES[rt] << REGISTER_STATES[rs]

   
def state_from_i_type(opcode, rs, rt, imm):
  
  global REGISTER_STATES
  
  if opcode == 8 or opcode == 9:
    REGISTER_STATES[rt] = REGISTER_STATES[rs] + imm
  elif opcode == 12:
    REGISTER_STATES[rt] = REGISTER_STATES[rs] & imm
  elif opcode == 15:
    REGISTER_STATES[rt] = imm << 16
  elif opcode == 13:
    REGISTER_STATES[rt] = REGISTER_STATES[rs] | imm
  elif opcode == 10 or opcode == 11:
    REGISTER_STATES[rt] = 1 if REGISTER_STATES[rs] < imm else 0
  elif opcode == 14:
    REGISTER_STATES[rt] = REGISTER_STATES[rs] ^ imm
    
    
    
def twos_complement(int_value, bits):

  if (int_value & (1 << (bits - 1))):
    int_value = int_value - (1 << bits)
  return int_value

def r_type(byte_string):

  """For parsing R instructions 6 | 5 | 5 | 5 | 6"""

  opcode = int(byte_string[:6], 2)
  rs = int(byte_string[6:11], 2)
  rt = int(byte_string[11:16], 2)
  rd = int(byte_string[16:21], 2)
  shift = int(byte_string[21:26], 2)
  func = int(byte_string[-6:], 2)
  print(OPCODES[opcode][func] + '\t$' + REGISTERS[rd] + ', $' + REGISTERS[rs] + ', ' + str(shift) + '($' + REGISTERS[rt] + ')')
    
  # try:
    # state_from_r_type(rs, rt, rd, shift, func)
    # print_registers()
  # except Exception as err:
    # print(str(err))
    # pass

def i_type(byte_string):

  """For parsing I instructions 6 | 5 | 5 | 16"""

  opcode = int(byte_string[:6], 2)
  rs = int(byte_string[6:11], 2)
  rt = int(byte_string[11:16], 2)
  imm = int(byte_string[16:], 2)
  if opcode == 8:
    imm = twos_complement(imm, 16)
  if opcode < 44 and opcode > 31:
    print(OPCODES[opcode] + '\t$' + REGISTERS[rt] + ', ' + str(imm) + '($' + REGISTERS[rs] + ')')
  else:
    print(OPCODES[opcode] + '\t$' + REGISTERS[rt] + ', $' + REGISTERS[rs] + ', ' + str(imm))

  # try:
    # state_from_i_type(opcode, rs, rt, imm)
    # print_registers()
  # except Exception as err:
    # print(str(err))
    # pass
    
def j_jal(byte_string):

  """For parsing J or JAL instructions 6 | 26"""

  opcode = int(byte_string[:6], 2)
  target = int(byte_string[6:], 2)
  if opcode == 2:
    target = target << 2
  print(OPCODES[opcode] + '\t' + str(target))


def main():
  import sys
  if len(sys.argv) < 2:
    print('Try ' + sys.argv[0] + ' <mips binary file>\n')
    return -1
  init_register_states()
  go = 1
  try:
    fh = open(sys.argv[1], 'rb')
  except Exception as err:
    print('Failed to read ' + sys.argv[1] + '\n')
    return -1
  while go:
    data = fh.read(4)
    if not data:
      go = 0
    try:
      anal_ysis(data)
    except Exception as err:
      pass
  fh.close()

def anal_ysis(b):

  byte_string = ''
  global REGISTER_STATES
  REGISTER_STATES[31] += 4
  for x in range(4):
    byte = bin(b[x])[2:]
    padding = '0' * (8 - len(byte))
    byte = padding + byte
    byte_string += byte
  # print(byte_string)
  opcode = int(byte_string[:6], 2)
  if opcode == 0:
    r_type(byte_string)
  elif opcode == 2 or opcode == 3:
    j_jal(byte_string)
  else:
    i_type(byte_string)
      

      
if __name__ == '__main__':
  main()
  
