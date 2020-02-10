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

names_map = {
    "FAMILY": NodeType.FAMILY,
    "MODULE": NodeType.MODULE,
    "LOOP": NodeType.LOOP,
    "SWITCH": NodeType.SWITCH,
    "TASK": NodeType.TASK,
    "NPASSTASK": NodeType.NPASSTASK,
    "FOREACH": NodeType.FOREACH
}
class FlowVisitor:
    def __init__(self, node_path, exp_home, switch_args=None):
        self.xml_context = ET.parse(f'{exp_home}/EntryModule/flow.xml')
        self.node_path = node_path
        self.exp_home = exp_home
        self.datestamp = ""
        self.switch_args = switch_args
        # new_flow_visitor->context->node = new_flow_visitor->context->doc->children;
        self.current_flow_node = self.xml_context.getroot()
        self.current_node_type = names_map[self.current_flow_node.tag]
        print(f'in __init__: current_node_type = {self.current_node_type}')
        print(f'in __init__: current_flow_node = {self.current_flow_node}')
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
            print(f'following token "{token}"')
            self.follow_token(token)

    def follow_token(self, token):
        token_node = self.current_flow_node.find(f"*[@name='{token}']")
        # print("result fo find(@name='{token})' " + str(token_node))
        name = token_node.attrib['name']
        if name != token:
            raise RuntimeError("xml find function didn't do what I asked")
        node_type = names_map[token_node.tag]

        name = token_node.attrib['name']
        print(f'{token_node.tag}: {token_node} (name = {name})')
        if token_node.tag == 'MODULE':
            self.follow_token_module(token)
        elif token_node.tag == 'SWITCH':
            self.follow_token_switch(token_node, token)
        else:
            self.current_flow_node = token_node
               
    def follow_token_switch(self, switch_xml_node, token):
        switch_type = switch_xml_node.attrib['type']
        for d in switch_xml_node:
            print(f'|--> Switch item : {d}')
            if True:
                self.current_flow_node = d
                return
    
    def follow_token_module(self, token):
        new_xml_filename = f'{self.exp_home}/modules/{token}/flow.xml'
        new_xml_context = ET.parse(new_xml_filename)
        new_root = new_xml_context.getroot()
        self.current_flow_node = new_root
        self.current_node_type = 'MODULE'
        print(new_root)
        print(f'MODULE : {new_root} (name = {new_root.attrib["name"]})')


f = FlowVisitor('module2/dhour_switch/loop/family/task', os.getcwd() + '/experiments/sample_exp')
