import xml.etree.cElementTree as ET
import os
import enum

class NodeType(enum.Enum):
    FAMILY = 1
    MODULE = 2
    LOOP = 3
    SWITCH = 4
    TASK = 5
    NPASSTASK = 6
    FOREACH = 7

tag_to_enum = {
    "FAMILY": NodeType.FAMILY,
    "MODULE": NodeType.MODULE,
    "LOOP": NodeType.LOOP,
    "SWITCH": NodeType.SWITCH,
    "TASK": NodeType.TASK,
    "NPASS_TASK": NodeType.NPASSTASK,
    "FOREACH": NodeType.FOREACH
}
def get_node_type(tag):
    return tag_to_enum[tag]

class PathTokenError(Exception):
    pass

class FlowVisitor:
    def __init__(self, exp_home, node_function=None):
        self.exp_home = exp_home
        self.depth = -1
    def node_function(self, node, path):
        self.depth_print(f"{node} (name = '{node.attrib['name']}, path = {path})")
    def depth_print(self, message):
        print("    "* self.depth + str(message))
    def visit_flow(self):
        first_xml_context = ET.parse(f'{self.exp_home}/EntryModule/flow.xml')
        self.visit_node(first_xml_context.getroot(), '')
    def visit_node(self, node, path):
        self.depth += 1
        path += "/" + node.attrib['name']
        for child in node.findall('*[@name]'):
            node_type = get_node_type(child.tag)
            if node_type is NodeType.MODULE:
                new_root = self.visit_module(child)
                self.node_function(new_root, path)
                self.visit_node(new_root, path)
            elif node_type is NodeType.SWITCH:
                switch_item = self.visit_switch(child)
                self.node_function(switch_item, path)
                self.visit_node(switch_item, path)
            elif node_type is NodeType.LOOP:
                self.node_function(child, path)
                self.visit_node(child, path)
            else:
                self.node_function(child, path)
                self.visit_node(child, path)
        self.depth -= 1
    def visit_switch(self, switch):
        """ Just enter the first switch item for now """
        switch_type = switch.attrib['type']
        for d in switch:
            if True:
                return d
    def visit_module(self, child):
        module_name = child.attrib['name']
        new_xml_filename = f'{self.exp_home}/modules/{module_name}/flow.xml'
        new_xml_context = ET.parse(new_xml_filename)
        new_root = new_xml_context.getroot()
        return new_root

    

class ExperimentRun:
    def __init__(self, exp_home, datestamp=None):
        self.exp_home = exp_home
        self.intramodule_path = None
        self.context_stack = []
    def get_xml_node_from_path(self, node_path, switch_args=None):
        path_tokens = node_path.strip('/').split('/')
        current_node = ET.parse(f'{self.exp_home}/EntryModule/flow.xml').getroot()
        intramodule_path = ''
        for token in path_tokens:
            intramodule_path += '/' + token
            print(f'intramodule_path = {intramodule_path}')
            token_node = current_node.find(f"*[@name='{token}']")
            if token_node is None:
                raise PathTokenError(f"'{token}'")
            name = token_node.attrib['name']
            if name != token:
                raise RuntimeError("xml find function didn't do what I asked")
            node_type = get_node_type(token_node.tag)
            if node_type is NodeType.MODULE:
                current_node = self.follow_token_module(token)
            elif node_type is NodeType.SWITCH:
                current_node = self.follow_token_switch(token_node, token)
            elif node_type is NodeType.LOOP:
                current_node = token_node
            else:
                current_node = token_node
        return current_node
    def follow_token_switch(self, switch_xml_node, token):
        """ Just enter the first switch item for now """
        switch_type = switch_xml_node.attrib['type']
        for d in switch_xml_node:
            if True:
                self.current_flow_node = d
                return d
    def follow_token_module(self, token):
        new_xml_filename = f'{self.exp_home}/modules/{token}/flow.xml'
        new_xml_context = ET.parse(new_xml_filename)
        new_root = new_xml_context.getroot()
        return new_root
    def find_node(self, node_path):


def nodeinfo(node_path, exp_home, datestamp=None):
    exp = ExperimentRun(exp_home, datestamp)
    print(exp.get_xml_node_from_path(node_path))

if __name__ == "__main__":
    v = FlowVisitor(os.getcwd() + '/experiments/sample_exp/')
    v.visit_flow()
    p_good = 'module2/dhour_switch/loop/family/task'
    p_bad = 'module2/dhour_switch/lop/family/task'
    exp = ExperimentRun(exp_home=f'{os.getcwd()}/experiments/sample_exp/')
    print(f"Trying with path = {p_good}")
    n = exp.get_xml_node_from_path(p_good)
    print(f'>> Found element {n}')
    print(f"Trying with path = {p_bad}")
    try:
        exp.get_xml_node_from_path(p_bad)
    except PathTokenError as e:
        print(f"ERROR: Bad token {e} in path '{p_bad}'")
