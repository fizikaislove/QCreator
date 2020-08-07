import numpy as np
# import sympy
# from scipy.optimize import fsolve
from scipy.constants import epsilon_0, mu_0
import math

# from scipy.optimize import root
# from scipy.optimize import minimize

#def triangulation(M):

# def sympy_to_numpy(Matrix):
#     matrix = np.array(Matrix)
#     x = np.zeros((np.shape(matrix)[0], np.shape(matrix)[1]))
#     for i in range(np.shape(matrix)[0]):
#         for j in range(np.shape(matrix)[1]):
#             x[i][j] = matrix[i][j]
#     return x

def det_gauss_elimination(a):
       '''
       calculate determinant using gauss-elimination method
       '''
       a = np.copy(a)

       assert(a.shape[0] == a.shape[1])
       n = a.shape[0]

       # Set up scale factors
       s = np.zeros(n)

       mult = 0
       for i in range(n):
           s[i] = max(np.abs(a[i,:])) # find the max of each row
       for k in range(0, n-1): #pivot row
           # Row interchange, if needed
           p = np.argmax(np.abs(a[k:n,k])/s[k:n]) + k
           if p != k:
               a[[k,p],:] = a[[p, k],:]
               s[k],s[p] = s[p],s[k]
               mult = mult + 1

           # convert a to upper triangular matrix
           for i in range(k+1,n):
               if a[i,k] != 0.0: # skip if a(i,k) is already zero
                   lam = a [i,k]/a[k,k]
                   a[i,k:n] = a[i,k:n] - lam*a[k,k:n]

       determinant = np.prod(np.diag(a))* (-1)**mult
       return determinant

class resistor:
    def num_terminals(self):
        return 2
    def num_degrees_of_freedom(self):
        return 0
    def boundary_condition(self, omega):
        return np.asarray([[1, -1, 0, self.R],[0,0,1,1]], dtype=complex)
    def __init__(self, R=None):
        self.R = R
        pass

class capacitor:
    def num_terminals(self):
        return 2
    def num_degrees_of_freedom(self):
        return 0
    def boundary_condition(self, omega):
        return np.asarray([[1j*omega*self.C, -1j*omega*self.C, 0, 1], [0,0,1,1]], dtype=complex)
    def __init__(self, C=None):
        self.C = C
        pass
class inductor:
    def num_terminals(self):
        return 2
    def num_degrees_of_freedom(self):
        return 0
    def boundary_condition(self, omega):
        return np.asarray([[1, -1, 0, 1j*omega*self.L], [0,0,1,1]], dtype=complex)
    def __init__(self, L=None):
        self.L = L
        pass

class short:
    def num_terminals(self):
        return 1
    def num_degrees_of_freedom(self):
        return 0
    def boundary_condition(self, omega):
        return np.asarray([[1, 0]], dtype=complex)
    def __init__(self):
        pass


class port:
    def num_terminals(self):
        return 1
    def num_degrees_of_freedom(self):
        return 1
    def boundary_condition(self, omega):
        return np.asarray([[1,0,self.Z0], [0,-1,1]], dtype=complex)
    def __init__(self, Z0=None):
        self.Z0 = Z0

class transmission_line_coupler:
    '''
    Here n is a number of conductors in  TL CPW coupler
    '''
    def num_terminals(self):
        return self.n*2
    def num_degrees_of_freedom(self):
        return self.n*2
    def propagating_modes(self):
        '''
        numpy.hstack puts together two matrix horizontally
        numpy.vstack puts together two matrix vertically
        '''
        M = np.hstack((np.vstack((self.Rl, self.Cl)), np.vstack((self.Ll, self.Gl))))
        #print(M)


        cl, mode_amplitudes = np.linalg.eig(M)
        # print('cl=',cl)
        # print('mode_amplitudes=',mode_amplitudes)

        # M = sympy.Matrix(M)
        # mode_amplitudes, cl = M.diagonalize()
        # cl = sympy.Matrix([cl[i,i] for i in range(M.shape[0])])
        #
        # cl = sympy_to_numpy(cl)
        # mode_amplitudes = sympy_to_numpy(mode_amplitudes)

        #print('cl=',cl)
        #print('mode_amplitudes=',mode_amplitudes)

        gammas = -cl
        modes = []

        for mode_id, gamma in enumerate(gammas):
            modes.append((gamma, mode_amplitudes[:,mode_id]))
        return modes

    def boundary_condition(self, omega):
        boundary_condition_matrix = np.zeros((self.num_terminals()*2, self.num_terminals()*2+self.num_degrees_of_freedom()), dtype=complex)
        boundary_condition_matrix[:, :self.num_terminals()*2] = np.identity(self.num_terminals()*2)


        for mode_pair_id, mode_pair in enumerate(self.propagating_modes()):
            '''
            boundary_condition_matrix[       0:self.n,  self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][:self.n])
            boundary_condition_matrix[  self.n:self.n*2,self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][:self.n])*np.exp(mode_pair[0]*self.l*omega)
            boundary_condition_matrix[self.n*2:self.n*3,self.n*4+mode_pair_id] = np.asarray(mode_pair[1][self.n:])
            boundary_condition_matrix[self.n*3:        ,self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][self.n:])*np.exp(mode_pair[0]*self.l*omega)
            '''


            boundary_condition_matrix[       0:self.n,  self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][:self.n])
            boundary_condition_matrix[  self.n:self.n*2,self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][:self.n])*(complex(np.round(np.cos(mode_pair[0]*self.l*omega), 4)) + complex(1j*np.round(np.sin(mode_pair[0]*self.l*omega), 4)))
            boundary_condition_matrix[self.n*2:self.n*3,self.n*4+mode_pair_id] = np.asarray(mode_pair[1][self.n:])
            boundary_condition_matrix[self.n*3:        ,self.n*4+mode_pair_id] = -np.asarray(mode_pair[1][self.n:])*(complex(np.round(np.cos(mode_pair[0]*self.l*omega), 4)) + complex(1j*np.round(np.sin(mode_pair[0]*self.l*omega), 4)))
        #print(mode_pair)
        return boundary_condition_matrix

    def __init__(self, n=2, l=None, Ll=None, Cl=None, Rl=None, Gl=None):
        self.n = n
        self.l = l
        self.Ll = Ll
        self.Cl = Cl
        self.Rl = Rl
        self.Gl = Gl
        pass




class transmission_line_system:
    def __init__(self):
        self.nodes = []   #list of all nodes [0,1,2...]
        self.elements = []   #list of all elements [<transmission_line_simulator_new.name_of_element>, ...]
        self.node_multiplicity = {}   #dictionary of node's multiplicity {node1: node1's multiplicity, node2: node2's multiplicity, ...}
        self.terminal_node_mapping = []   #list of terminals's nodes [terminal1's nodes=[], node2's multiplicity=[], ...]
        self.dof_mapping = []   #???

    def add_element(self, element, nodes):
        self.elements.append(element)
        for node in nodes:
            if node not in self.nodes:
                self.node_multiplicity[node] = 0
                self.nodes.append(node)
            self.node_multiplicity[node] += 1
        self.terminal_node_mapping.append(nodes)
        return


    def create_boundary_problem_matrix(self, omega):
        # count nodes
        self.dof_mapping = [n for n in self.nodes] # nodal voltages
        self.dof_mapping.extend([(e_id, p_id) for e_id, e in enumerate(self.elements) for p_id in range(e.num_terminals())])
                                                     # currents incident into each terminal
        self.dof_mapping.extend([(e_id, int_dof_id) for e_id, e in enumerate(self.elements) for int_dof_id in range(e.num_degrees_of_freedom())])
                                                     # number of element-internal degrees of freedom

        # full dof number
        num_dof = len(self.dof_mapping)

        # number of nodes
        node_no = len(self.nodes)
        # number of internal dofs
        internal_dof_no = np.sum(e.num_degrees_of_freedom() for e in self.elements)
        # number of terminals
        terminal_no = np.sum(e.num_terminals() for e in self.elements)

        # dynamic equations reflect the element's IV characteristic
        dynamic_equation_no = terminal_no + internal_dof_no
        # kinetic equations are Kirchhof's law that the sum of nodal currents is zero
        kinetic_equation_no = node_no

        num_equations = dynamic_equation_no + kinetic_equation_no

        boundary_condition_matrix = np.zeros((num_equations, num_dof), dtype=complex)

        # filling dynamic equations
        equation_id = 0
        current_offset = 0
        internal_dof_offset = 0
        for e_id, e in enumerate(self.elements):
            equations = e.boundary_condition(omega)
            for element_equation_id in range(equations.shape[0]):
                equation = equations[element_equation_id, :]
                for terminal_id, terminal_node in enumerate(self.terminal_node_mapping[e_id]):
                    node_id = self.nodes.index(terminal_node)
                    boundary_condition_matrix[equation_id, node_id] = equation[terminal_id] #nodal voltages
                    boundary_condition_matrix[equation_id, node_no+current_offset+terminal_id] = equation[terminal_id+e.num_terminals()] #nodal current
                for internal_dof_id in range(e.num_degrees_of_freedom()):
                    boundary_condition_matrix[equation_id, node_no+terminal_no+internal_dof_offset+internal_dof_id] = equation[2*e.num_terminals() + internal_dof_id]
                equation_id += 1
            internal_dof_offset += e.num_degrees_of_freedom()
            current_offset += e.num_terminals()

        full_terminal_id = 0
        # filling kinetic equations
        for e_id, e in enumerate(self.elements):
            for terminal_id, node in enumerate(self.terminal_node_mapping[e_id]):
                boundary_condition_matrix[dynamic_equation_no+self.nodes.index(node), node_no+full_terminal_id] = 1
                full_terminal_id += 1
        return boundary_condition_matrix

    def boundary_condition_matrix_det(self, omega):
        matrix = self.create_boundary_problem_matrix(omega)
        return np.linalg.det(matrix)

    def boundary_condition_matrix_abs_det(self, omega):
        matrix = self.create_boundary_problem_matrix(omega)
        det = np.linalg.det(matrix)
        return np.log10((det.real)**2 + (det.imag)**2)

    def solve_problem(self, frequency_approximation, epsilon, step):

        '''
        This is a stupid method for solving the problem. It looks like gradient descent method
        '''

        x = frequency_approximation
        func = self.create_boundary_problem_matrix(frequency_approximation)

        number_of_iterations = 0

        while (self.create_boundary_problem_matrix(x) - 0) > epsilon:
            number_of_iterations = number_of_iterations + 1
            print('not', number_of_iterations)
            print(x)
            grad = (self.create_boundary_problem_matrix(x+step) - self.create_boundary_problem_matrix(x))/step

            if grad < 0:
                x = x + step#*grad
            elif grad > 0:
                x = x - step#*grad
            else:
                print('Problem')
                break
        result = x



        return result


    def res(self):
        print('self.nodes', self.nodes)
        print('self.elements', self.elements)
        print('self.node_multiplicity', self.node_multiplicity)
        print('self.terminal_node_mapping', self.terminal_node_mapping)
        print('self.dof_mapping', self.dof_mapping)

        print('self.nodes', type(self.nodes))
        print('self.elements', type(self.elements))
        print('self.node_multiplicity', type(self.node_multiplicity))
        print('self.terminal_node_mapping', type(self.terminal_node_mapping))
        print('self.dof_mapping', type(self.dof_mapping))
        return
