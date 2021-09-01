import enum
import string


class Network(enum.Enum):
    PUN = 0,
    PDN = 1


class NodeType(enum.Enum):
    INNODE = 0,
    NOTNODE = 1,
    ORNODE = 2,
    ANDNODE = 3


# InNode ---------------------------------------------------------------------------------------------------------------


class InNode:
    def __init__(self, name):
        self.name_ = name

    def get_type(self):
        return NodeType.INNODE

    def traverse(self):
        return self.name_

    def __str__(self):
        return self.traverse()

    def invert(self):
        return NotNode(InNode(self.name_))

    def deMorgan(self):
        return InNode(self.name_)

    def longest_path(self):
        return 1

    def mosfet(self, up, down, network, inverters, transistor_count, width, length):
        if width and length:
            if network == Network.PUN:
                try:
                    inverters[self.name_] += 1
                except KeyError:
                    inverters[self.name_] = 1
                out = "M" + f"{transistor_count[0]}" + "P" + " " + down + " wb_" + self.name_ + " " + up + " " + up + \
                      " PMOS W=" + "'" + f"{width / length}" + "*Lmin'" + " L=" + "'Lmin'" + "\n"
                transistor_count[0] += 1
                return out
            else:
                out = "M" + f"{transistor_count[0]}" + "N" + " " + up + " " + self.name_ + " " + down + " " + down + \
                      " NMOS W=" + "'" + f"{width / length}" + "*Lmin'" + " L=" + "'Lmin'" + "\n"
                transistor_count[0] += 1
                return out
        else:
            if network == Network.PUN:
                try:
                    inverters[self.name_] += 1
                except KeyError:
                    inverters[self.name_] = 1
                out = "M" + f"{transistor_count[0]}" + "P" + " " + down + " wb_" + self.name_ + " " + up + " " + up + " PMOS\n"
                transistor_count += 1
                return out
            else:
                out = "M" + f"{transistor_count[0]}" + "N" + " " + up + " " + self.name_ + " " + down + " " + down + " NMOS\n"
                transistor_count += 1
                return out


# NotNode --------------------------------------------------------------------------------------------------------------


class NotNode:
    def __init__(self, a):
        self.a_ = a

    def get_type(self):
        return NodeType.NOTNODE

    def traverse(self):
        return self.a_.traverse() + "'"

    def __str__(self):
        return self.traverse()

    def invert(self):
        return InNode(self.a_.traverse())

    def deMorgan(self):
        if self.a_.get_type() == NodeType.INNODE:
            return NotNode(InNode(self.a_.traverse()))
        else:
            return self.a_.invert().deMorgan()

    def longest_path(self):
        return self.a_.longest_path()

    def mosfet(self, up, down, network, inverters, transistor_count: dict, width, length):
        if width and length:
            child_name = self.a_.traverse()
            if network == Network.PUN:
                out = "M" + f"{transistor_count[0]}" + "P" + " " + down + " " + child_name + " " + up + " " + up + \
                      " PMOS W=" + "'" + f"{width / length}" + "*Lmin'" + " L=" + "'Lmin'" + "\n"
                transistor_count[0] += 1
                return out
            else:
                try:
                    inverters[child_name] += 1
                except KeyError:
                    inverters[child_name] = 1
                out = "M" + f"{transistor_count[0]}" + "N" + " " + up + " wb_" + child_name + " " + down + " " + down + \
                      " NMOS W=" + "'" + f"{width / length}" + "*Lmin'" + " L=" + "'Lmin'" + "\n "
                transistor_count[0] += 1
                return out
        else:
            child_name = self.a_.traverse()
            if network == Network.PUN:
                out = "M" + f"{transistor_count[0]}" + "P" + " " + down + " " + child_name + " " + up + " " + up + " PMOS\n"
                transistor_count[0] += 1
                return out
            else:
                try:
                    inverters[child_name] += 1
                except KeyError:
                    inverters[child_name] = 1
                out = "M" + f"{transistor_count[0]}" + "N" + " " + up + " wb_" + child_name + " " + down + " " \
                      + down + " NMOS\n"
                transistor_count[0] += 1
                return out


# OrNode ---------------------------------------------------------------------------------------------------------------

class OrNode:
    def __init__(self, a, b):
        self.a_ = a
        self.b_ = b

    def get_type(self):
        return NodeType.ORNODE

    def traverse(self):
        return '(' + self.a_.traverse() + '|' + self.b_.traverse() + ')'

    def __str__(self):
        return self.traverse()

    def invert(self):
        return AndNode(self.a_.invert(), self.b_.invert())

    def deMorgan(self):
        return OrNode(self.a_.deMorgan(), self.b_.deMorgan())

    def longest_path(self):
        a_length = self.a_.longest_path()
        b_length = self.b_.longest_path()
        return a_length if (a_length > b_length) else b_length

    def mosfet(self, up, down, network, inverters, transistor_count, width, length):
        if width and length:
            out = self.a_.mosfet(up, down, network, inverters, transistor_count, width, length)
            out += self.b_.mosfet(up, down, network, inverters, transistor_count, width, length)
            return out
        else:
            out = self.a_.mosfet(up, down, network, inverters, transistor_count)
            out += self.b_.mosfet(up, down, network, inverters, transistor_count)
            return out


# AndNode --------------------------------------------------------------------------------------------------------------


class AndNode:
    wire_count = 0

    def __init__(self, a, b):
        self.a_ = a
        self.b_ = b

    def get_type(self):
        return NodeType.ANDNODE

    def traverse(self):
        return '(' + self.a_.traverse() + '&' + self.b_.traverse() + ')'

    def __str__(self):
        return self.traverse()

    def invert(self):
        return OrNode(self.a_.invert(), self.b_.invert())

    def deMorgan(self):
        return AndNode(self.a_.deMorgan(), self.b_.deMorgan())

    def longest_path(self):
        return self.a_.longest_path() + self.b_.longest_path()

    def mosfet(self, up, down, network, inverters, transistor_count, width, length):
        if not (width is None) and not (length is None):
            wire_name = "w_" + f"{AndNode.wire_count}"
            AndNode.wire_count += 1
            la = self.a_.longest_path()
            lb = self.b_.longest_path()
            lab = la + lb
            out = self.a_.mosfet(up, wire_name, network, inverters, transistor_count, (lab * width / la), length)
            out += self.b_.mosfet(wire_name, down, network, inverters, transistor_count, (lab * width / lb), length)
            return out
        else:
            wire_name = "w_" + f"{AndNode.wire_count}"
            AndNode.wire_count += 1
            out = self.a_.mosfet(up, wire_name, network, inverters, transistor_count)
            return out
