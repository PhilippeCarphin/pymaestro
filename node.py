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
        self.xml_context = ET.parse(f'{exp_home}/EntryModule/flow.xml')
        self.current_flow_node = self.xml_context.getroot()
        self.current_node_type = get_node_type(self.current_flow_node.tag)
        self.exp_home = exp_home
        self.depth = 0
    def node_function(self, node, path):
        self.depth_print(f"{node} (name = '{node.attrib['name']}, path = {path})")
    def depth_print(self, message):
        print("    "* self.depth + str(message))
    def visit_flow(self):
        self.visit_node(self.xml_context.getroot(), '')
    def visit_node(self, node, path):
        self.depth += 1
        for child in node.findall('*[@name]'):
            path += "/" + child.attrib['name']
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

if __name__ == "__main__":
    v = FlowVisitor(os.getcwd() + '/experiments/sample_exp/')
    v.visit_flow()
    quit()
    

class NodeInfoHelper:
    def __init__(self, node_path, exp_home, switch_args=None):
        self.xml_context = ET.parse(f'{exp_home}/EntryModule/flow.xml')
        self.node_path = node_path
        self.exp_home = exp_home
        self.datestamp = ""
        self.switch_args = switch_args
        self.current_flow_node = self.xml_context.getroot()
        self.current_node_type = get_node_type(self.current_flow_node.tag)
        self.suite_name = None
        self.task_path = None
        self.module = None
        self.intramodule_path = None
        self.context_stack = []

        self.parse_path()


    def parse_path(self):
        path_tokens = self.node_path.strip('/').split('/')
        for token in path_tokens:
            self.follow_token(token)
        self.do_final_stuff()

    def do_final_stuff(self):
        self.MaestroNode = None
        print(f'Found Node : {self.current_flow_node}')
        pass

    def follow_token(self, token):
        token_node = self.current_flow_node.find(f"*[@name='{token}']")
        if token_node is None:
            raise PathTokenError(f"'{token}'")
        name = token_node.attrib['name']
        if name != token:
            raise RuntimeError("xml find function didn't do what I asked")
        node_type = get_node_type(token_node.tag)
        if node_type is NodeType.MODULE:
            self.follow_token_module(token)
        elif node_type is NodeType.SWITCH:
            self.follow_token_switch(token_node, token)
        elif node_type is NodeType.LOOP:
            self.current_flow_node = token_node
        else:
            self.current_flow_node = token_node
               
    def follow_token_switch(self, switch_xml_node, token):
        """ Just enter the first switch item for now """
        switch_type = switch_xml_node.attrib['type']
        for d in switch_xml_node:
            if True:
                self.current_flow_node = d
                return
    
    def follow_token_module(self, token):
        new_xml_filename = f'{self.exp_home}/modules/{token}/flow.xml'
        new_xml_context = ET.parse(new_xml_filename)
        new_root = new_xml_context.getroot()
        self.current_flow_node = new_root
        self.current_node_type = 'MODULE'

    def node(self):
        """ Return the MaestroNode instance with all the info (like what nodeinfo function returns) """
        return None

def nodeinfo(exp_home, node_path, datestamp=None):
    nh = NodeInfoHelper(node_path, exp_home)
    return nh.node()

p_good = 'module2/dhour_switch/loop/family/task'
p_bad = 'module2/dhour_switch/lop/family/task'
print(f"Trying with path = {p_good}")
nodeinfo(os.getcwd() + '/experiments/sample_exp', p_good)
print(f"Trying with path = {p_bad}")
try:
    nodeinfo(os.getcwd() + '/experiments/sample_exp', p_bad)
except PathTokenError as e:
    print(f"ERROR: Bad token {e} in path '{p_bad}'")
