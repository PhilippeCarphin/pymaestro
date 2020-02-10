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
        for c in self.current_flow_node:
            if c.tag == 'SWITCH_ITEM':
                # If c is a 'SWITCH', then we go in the right
                # switch item right away.  Therefore finding
                # a 'c' here that is a switch item is an
                # unrecoverable error
                raise RuntimeError("Should never reach here")
            if 'name' in c.attrib and c.attrib['name'] == token:
                name = c.attrib['name']
                node_type = names_map[c.tag]
                print(f'{c.tag}: {c} (name = {name})')
                if c.tag == 'MODULE':
                    self.follow_token_module(token)
                elif c.tag == 'SUBMITS':
                    # SUBMITS tags only have a 'sub_name' attribute
                    # and are not meant to be looked at in the
                    # path parsing part.
                    raise RuntimeError("SUBMITS tags should not have a name attrib")
                elif c.tag == 'SWITCH':
                    self.follow_token_switch(c, token)
                else:
                    self.current_flow_node = c
               
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
