import qiskit
from qiskit import IBMQ, execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.providers.jobstatus import JobStatus, JOB_FINAL_STATES
from math import log2, ceil
from copy import deepcopy
import time
import numpy as np

# custom imports 
from create_ghz_circuit import create_ghz_circuit
from create_qot_circuits import create_qot_circuits
from convert_ibm_returned_result_to_dictionary import convert_ibm_returned_result_to_dictionary
import process_dictionary
from shot_count_from_dict_of_results import shot_count_from_dict_of_results
from shot_count_from_results import shot_count_from_results
from reshape_vec_to_mat import reshape_vec_to_mat
from mgf import MatrixGeneratingFunction
from negativity import Negativity

IBMQ.load_account()
provider = IBMQ.get_provider(hub='ibm-q-community', group='hackathon', project='tokyo-nov-2019')

list_of_backends = provider.backends()
print('\nYou have access to:')
print(list_of_backends)

# number of qubits   
n = 4
# qubit partition sizes
k = 2

# connections for graph state
edges = []
for i in range(n-1):
    edges.append([i,i+1])

quantum_circuit = create_ghz_circuit(edges)

# global hash function    
hash_functions = []
# here we assume powers of 2
num_func = ceil(log2(n)) 

# populates hash table
for i in range(num_func):
    temp_list = []
    for j in range(n):
        # checks if i'th bit is set in j 
        if j & (1 << i):
            temp_list.append(1)
        else:
            temp_list.append(0)
    hash_functions.append(temp_list)
print("hash_functions:", str(hash_functions))
circuit_list = create_qot_circuits(quantum_circuit, hash_functions, k)

simulator_name = 'ibmq_qasm_simulator'
backend = provider.get_backend(simulator_name)
job = execute(circuit_list, backend=backend)

complete = False
status = job.status()
while not complete:
    if job.status() in JOB_FINAL_STATES:
        complete = True
    else:
        time.sleep(3)
        print("computing...")
print("complete!")        

result = job.result()
result_dict = convert_ibm_returned_result_to_dictionary(result)

density_matrix = []
size = (n*(n-1))/2
ones = []
for i in range(int(size)):
	ones.append(1)

density_matrix.append(ones)
density_matrix.append(process_dictionary.process_dictionary_ix_iy_iz("all_x_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_ix_iy_iz("all_y_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_ix_iy_iz("all_z_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xi_yi_zi("all_x_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xi_yi_zi("all_y_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xi_yi_zi("all_z_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xx_yy_zz("all_x_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xx_yy_zz("all_y_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xx_yy_zz("all_z_basis", result_dict))
density_matrix.append(process_dictionary.process_dictionary_xy12(n, result_dict, hash_functions))
density_matrix.append(process_dictionary.process_dictionary_yz12(n, result_dict, hash_functions))
density_matrix.append(process_dictionary.process_dictionary_xz12(n, result_dict, hash_functions))
density_matrix.append(process_dictionary.process_dictionary_zx12(n, result_dict, hash_functions))
density_matrix.append(process_dictionary.process_dictionary_yz12(n, result_dict, hash_functions))
density_matrix.append(process_dictionary.process_dictionary_zy12(n, result_dict, hash_functions))

m = density_matrix
dm = [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))] 
# print("------")
# print(process_dictionary.process_dictionary_xx_yy_zz("all_x_basis", result_dict))
# print("------")
# print(dm)
# print(reshape_vec_to_mat(dm[0]))
# print("------")
for i in range(len(dm)):
	print(Negativity(MatrixGeneratingFunction(reshape_vec_to_mat(dm[i]))))

print(MatrixGeneratingFunction(np.matrix([[0,0,1,0],[0,1,1,0],[0,0,1,0],[1,0,0,0]])))




