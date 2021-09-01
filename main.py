#!/usr/bin/python
import argparse
from GraphConverter import *
from Graph import *
import sys
from argparse import ArgumentParser

args = sys.argv


class Cgen:
    npos = -1
    version = '0.1'

    def __init__(self):
        sys.setrecursionlimit(10 ** 6)

    def convert_to_mofset(self, input_node, p, n: float, l: float, use_sizing: bool, output, file_output):
        pun = input_node.deMorgan()
        params = f"\n.param Lmin={l}\n"
        params += f".param n={n}\n"
        params += f".param p={p}\n"
        print(params)
        print("PUN: ", pun)
        pdn = pun.invert()
        print("PDN: ", pdn)
        transistor_count_inverters = 0
        transistor_count = [0]
        inverters = {}
        if use_sizing:
            mosfet = pun.mosfet("Vdd", "y", Network.PUN, inverters, transistor_count, p * l, l)
            output += params + "\n"
            output += "==============\nPUN Network: \n" + mosfet
            file_output += "\n*** PUN Network: \n" + mosfet
            mosfet = pdn.mosfet("y", "gnd", Network.PDN, inverters, transistor_count, n * l, l)
            output += "==============\nPDN Network: \n" + mosfet
            file_output += "\n*** PDN Network: \n" + mosfet
        else:
            mosfet = pun.mosfet("Vdd", "y", Network.PUN, inverters, transistor_count)
            output += "==============\nPDN Network: \n" + mosfet
            file_output += "\n*** PDN Network: \n" + mosfet
            mosfet = pdn.mosfet("y", "gnd", Network.PDN, inverters, transistor_count)
            output += "==============\nPDN Network: \n" + mosfet
            file_output += "\n*** PDN Network: \n" + mosfet
        if len(inverters) > 0:
            output2 = "Inverters:\n"
            file_output_2 = ''
            if use_sizing:
                for inverter in inverters.keys():
                    mosfet = "*** Inv\n"
                    mosfet += "Mi" + f'{transistor_count_inverters}' + "P" + " wb_" + inverter + " " + inverter + \
                              " Vdd Vdd PMOS W=" + "'p*Lmin'" + " L=" + "'Lmin'" + "\n"
                    transistor_count_inverters += 1
                    mosfet += "Mi" + f'{transistor_count_inverters}' + "N" + " wb_" + inverter + " " + inverter + \
                              " gnd gnd NMOS W=" + "'n*Lmin'" + " L=" + "'Lmin'" + "\n"
                    transistor_count_inverters += 1
                    file_output_2 += mosfet
                    output2 += "The inverter circuit for " + inverter + " is used " + f'{inverters[inverter]}' + \
                               " times: \n" + mosfet
            else:
                for inverter in inverters.keys():
                    mosfet = "*** Inv\n"
                    mosfet += "Mi" + f'{transistor_count_inverters}' + "P" + " wb_" + inverter + " " + inverter + \
                              " Vdd Vdd PMOS\n"
                    transistor_count_inverters += 1
                    mosfet += "Mi" + f'{transistor_count_inverters}' + "N" + " wb_" + inverter + " " + inverter + \
                              " gnd gnd NMOS\n"
                    transistor_count_inverters += 1
                    file_output_2 += mosfet
                    output2 += "The inverter circuit for " + inverter + " is used " + f'{inverters[inverter]}' + \
                               " times: \n" + mosfet
            file_output = params + "\n" + file_output_2 + file_output
            output = output2 + output
        output = output + "Total Number of transistors: " + f'{transistor_count_inverters + transistor_count[0]}'
        return output, file_output

    # <-------------------------------------------------------------------------------------------------------------------->
    def help_mode(self):
        print(" -h : help")
        print(" -i : interactive")
        print(" -f : input_file_path")
        print(" -t : type")
        print(" -o : output_file_path\n")
        print('<---------------------------------------------------------------------------------->\n')
        print("func2cmos: Boolean function to CMOS synthesizer Version:", self.version)
        print("Boolean logic uses |, &, and ' without spaces in function declaration:")
        print("Syntax:")
        print("\tfunnction_name=f'(v1, v2, ..., vn)  [p=<value> L=<value> n=<value>]")
        print("\tL>=Lmin ")
        print("\tn=Wn/L ")
        print("\tp=Wp/L ")
        print("Note: If any of p, L, or n are not defined, sizing will not be calculated.")
        print("Also, only use spaces to seperate the parameters ")
        print("Use inverting functions.")
        print("\tGood:     vo=(vi&(b|c'))' p=4 L=2 n=2")
        print("\tNot Good: vo=vi&(b|c') p=4 L=2 n=2")
        print("Example(s):")
        print("\tf1=(vi&(b|c')|e&(f|g))' p=4 L=2 n=2")
        print("\tf2=((vi&(b|c'))|e&(f|g)|(k&L&P&U)|(W|R))' p=4 L=2 n=2")
        print("\tf3=((vi&(b|c'))|e&(f'|g)|(k'&L&P&U)|(W|R))' p=4 L=2 n=2")

    def interactive_mode(self, input_file, output_path_file, ):
        n = 0.0
        p = 0.0
        l = 0.0
        input_string = input("Please insert your input: ") if input_file is None else input_file
        input_string = input_string.split()
        for token in input_string:
            if token[0] == 'l' or token[0] == 'L':
                found = token.find('=')
                if found != self.npos:
                    val = token[found + 1:]
                    l = float(val)

            elif token[0] == 'n' or token[0] == 'N':
                found = token.find('=')
                if found != self.npos:
                    val = token[found + 1:]
                    n = float(val)

            elif token[0] == 'p' or token[0] == 'P':
                found = token.find('=')
                if found != self.npos:
                    val = token[found + 1:]
                    p = float(val)

            else:
                found = token.find('=')
                if found != self.npos:
                    input_string = token[found + 1:]
                else:
                    input_string = token

        conv = GraphConverter()
        node_tree = conv.convert_to_nodes(input_string)
        print('input: ', node_tree)
        use_sizing = n != 0.0 and p != 0.0 and l != 0.0
        output = ''
        file_output = ''
        output, file_output = self.convert_to_mofset(node_tree, p, n, l, use_sizing, output, file_output)
        print(output)
        path = input("Please input a path to write to txt file. Type q to quit and ignore writing to file: ") \
            if output_path_file is None else output_path_file

        if path != 'q' and path != 'Q':
            if not path.endswith('.txt'):
                path += '.txt'
            f = open(path, "wt")
            f.writelines("*** Input function: " + input_string)
            f.writelines(file_output)
            f.close()


class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
            # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


if __name__ == '__main__':
    cgen = Cgen()
    if len(args) == 1 or args[1] == '-h':
        cgen.help_mode()
    elif args[1] == '-i':
        cgen.interactive_mode(None, None)
    elif args[1] == '-f':
        input_path = args[2]
        mode = args[4]
        output_path = args[6]
        f = open(input_path, "rt")
        input_string = f.read()
        f.close()
        cgen.interactive_mode(input_string, output_path)
    else:
        cgen.help_mode()
