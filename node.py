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
    "NPASSTASK": NodeType.NPASSTASK,
    "FOREACH": NodeType.FOREACH
}
def get_node_type(tag):
    return tag_to_enum[tag]

class PathTokenError(Exception):
    pass
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
        self.on_first_node = True

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


p_good = 'module2/dhour_switch/loop/family/task'
p_bad = 'module2/dhour_switch/lop/family/task'
print(f"Trying with path = {p_good}")
f = NodeInfoHelper(p_good , os.getcwd() + '/experiments/sample_exp')
print(f"Trying with path = {p_bad}")
try:
    f = NodeInfoHelper(p_bad , os.getcwd() + '/experiments/sample_exp')
except PathTokenError as e:
    print(f"ERROR: Bad token {e} in path '{p_bad}'")
