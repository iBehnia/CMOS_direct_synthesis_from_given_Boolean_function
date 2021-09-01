from Graph import *
from Stack import *


class GraphConverter:
    def __init__(self):
        self.op_stack = Stack()
        self.node_stack = Stack()

    def do_binary(self, char):
        r = self.node_stack.pop()
        l = self.node_stack.pop()

        if char == '&':
            self.node_stack.push(AndNode(l, r))
        elif char == '|':
            self.node_stack.push(OrNode(l, r))
        else:
            print('Nodestack dobinary issue')

    def process_operator(self, char):
        while (not self.op_stack.is_empty()) and self.op_stack.top() != '(' and self.op_stack.top() != '|':
            self.do_binary(self.op_stack.pop())
        self.op_stack.push(char)

    def process_operator2(self, char):
        while (not self.op_stack.is_empty()) and self.op_stack.top() != '(':
            self.do_binary(self.op_stack.pop())
        self.op_stack.push(char)

    def parse_right_parenthesis(self):
        while (not self.op_stack.is_empty()) and self.op_stack.top() != '(':
            self.do_binary(self.op_stack.pop())
        self.op_stack.pop()

    def convert_to_nodes(self, input_string: string):
        i = [0]
        while i[0] < len(input_string):
            c = input_string[i[0]]
            if c == '\'':
                n = self.node_stack.pop()
                self.node_stack.push(NotNode(n))
            elif c == '&':
                self.process_operator(c)
            elif c == '|':
                self.process_operator2(c)
            elif c == '(':
                self.op_stack.push('(')
            elif c == ')':
                self.parse_right_parenthesis()
            else:
                variable = ''
                while i[0] < len(input_string):
                    if input_string[i[0]] == ')' or input_string[i[0]] == '(' or input_string[i[0]] == '|' \
                            or input_string[i[0]] == '\'' or input_string[i[0]] == '&':
                        i[0] -= 1
                        break
                    variable += input_string[i[0]]
                    i[0] += 1
                self.node_stack.push(InNode(variable))
            i[0] += 1
        while not self.op_stack.is_empty():
            self.do_binary(self.op_stack.pop())
        if self.node_stack.size() != 1:
            print('Runtime Error! Incorrectly formed binary logic.')

        return self.node_stack.top()

# endif
