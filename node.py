import xml.etree.cElementTree as ET
import os
class FlowVisitor:
    def __init__(self, node_path, exp_home, switch_args=None):
        self.xml_context = ET.parse(f'{exp_home}/EntryModule/flow.xml')
        self.node_path = node_path
        self.exp_home = exp_home
        self.datestamp = ""
        self.switch_args = switch_args
        # new_flow_visitor->context->node = new_flow_visitor->context->doc->children;
        self.current_flow_node = self.xml_context.getroot()
        self.current_node_type = 'Task'
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
                raise RuntimeError("Should never reach here")
            if 'name' in c.attrib and c.attrib['name'] == token:
                name = c.attrib['name']
                print(f'{c.tag}: {c} (name = {name})')
                if c.tag == 'MODULE':
                    new_xml_filename = f'{self.exp_home}/modules/{token}/flow.xml'
                    new_xml_context = ET.parse(new_xml_filename)
                    new_root = new_xml_context.getroot()
                    self.current_flow_node = new_root
                    self.current_node_type = 'MODULE'
                    print(new_root)
                    print(f'MODULE : {new_root} (name = {new_root.attrib["name"]})')
                elif c.tag == 'SUBMITS':
                    self.current_flow_node = c
                elif c.tag == 'SWITCH':
                    switch_type = c.attrib['type']
                    for d in c:
                        print(f'|--> Switch item : {d}')
                        if True:
                            self.current_flow_node = d
                            break
                else:
                    self.current_flow_node = c
               
    
    def follow_token_module(self, token):
        pass


f = FlowVisitor('module2/dhour_switch/loop/family/task', os.getcwd() + '/experiments/sample_exp')
