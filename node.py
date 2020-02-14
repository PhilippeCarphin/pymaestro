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

class DependsScope(enum.Enum):
    INTRA_SUITE = 1
    INTRA_USER = 2
    INTER_USER = 3

class DependsType(enum.Enum):
    NODE_DEPENDENCY = 1
    DATE_DEPENDENCY = 2

class SeqDependency:
    @classmethod
    def from_xml_node(cls, xml_node):
        return SeqDependency(
            dep_type=DependsType.NODE_DEPENDENCY,
            dep_name=xml_node.attrib.get('dep_name'),
            exp_home=xml_node.attrib.get('exp'),
            index=xml_node.attrib.get('index'),
            local_index=xml_node.attrib.get('local_index'),
            node_path=xml_node.attrib.get('path'),
            hour=xml_node.attrib.get('hour'),
            valid_hour=xml_node.attrib.get('valid_hour'),
            valid_dow=xml_node.attrib.get('valid_dow'),
            time_delta=xml_node.attrib.get('time_delta'),
            protocol=xml_node.attrib.get('protocol', 'polling'),
            status=xml_node.attrib.get('status', 'end')
        )

    def __init__(self, *args, **kwargs):
        self.depends_type = kwargs.get('depends_type')
        self.exp_scope = kwargs.get('exp_scope', DependsType.NODE_DEPENDENCY)
        self.node_name = kwargs.get('node_name')
        self.node_path = kwargs.get('node_path')
        self.exp_home = kwargs.get('exp_home')
        self.status = kwargs.get('status')
        self.index = kwargs.get('index')
        self.ext = kwargs.get('ext')
        self.local_index = kwargs.get('local_index')
        self.local_ext = kwargs.get('local_ext')
        self.hour = kwargs.get('hour')
        self.time_delts = kwargs.get('time_delts')
        self.datestamp = kwargs.get('datestamp')
        self.valid_hour = kwargs.get('valid_hour')
        self.valid_dow = kwargs.get('valid_dow')
        self.protocol = kwargs.get('protocol')
    
    def validate_local_args(self):
        return False
        pass
    def validate_args(self):
        return False
        pass
    def get_loop_args(self, dep_args, local_args):
        return False
        pass
    def validate_indices(self, dep_args, local_args):
        self.validate_local_args()
        self.validate_args()
        self.index = self.get_loop_args(dep_args, local_args)
        self.local_index = self.get_loop_args(local_args, local_args)

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
    """ The 'ExperimentRun' is an experiment 'at' a particular datestamp.

    Certain nodes 'exist' or do not 'exist' depending on the datestamp.
    """
    def __init__(self, exp_home, datestamp=None):
        self.exp_home = exp_home
        self.datestamp = datestamp
    def get_xml_node_from_path(self, node_path, switch_args=None):
        path_tokens = node_path.strip('/').split('/')
        intramodule_path = ''

        current_node = ET.parse(f'{self.exp_home}/EntryModule/flow.xml').getroot()

        ndp = ExperimentRunNode(xml_node=None, node_path=node_path, exp_run=self, intramodule_path=intramodule_path, name=None, node_name=None, module=None, datestamp=None, exp_home=self.exp_home, node_function=lambda e: print(e))
        sub_path = ''
        for token in path_tokens:
            sub_path += '/' + token
            previous_node = current_node
            current_node, intramodule_path = self.parse_token(token, current_node, intramodule_path)
            self.check_work_unit(ndp, current_node, previous_node, sub_path)
        return current_node, intramodule_path

    def check_work_unit(self, ndp, xml_node, previous_xml_node, sub_path):
        def Resource_parseWorkerPath(current_node, exp_home, ndp):
            def get_worker_path(n):
                if 'worker_path' in n.attrib:
                    ndp.worker_path = n.attrib['worker_path']
            rv = ResourceVisitor(exp_home=self.exp_home, datestamp=self.datestamp)
            rv.visit_resources('module' + sub_path, get_worker_path, ndp=ndp)
        # - 
        if xml_node.tag == 'MODULE':
            context = previous_xml_node
        else:
            context = xml_node
        res = context.findall('*[@work_unit]')
        if res:
            print(f'Node {context} has a WORKER child')
            Resource_parseWorkerPath(xml_node, self.exp_home, ndp)
        else:
            print(f'Node {context} has no child with "work_unit" attribute')


    def parse_token(self, token, current_node, intramodule_path):
        print(f'parsing token {token}')
        token_node = current_node.find(f"*[@name='{token}']")
        if token_node is None:
            raise PathTokenError(f"'{token}'")
        name = token_node.attrib['name']
        if name != token:
            raise RuntimeError("xml find function didn't do what I asked")
        node_type = get_node_type(token_node.tag)

        if node_type is NodeType.MODULE:
            intramodule_path = ''
        else:
            intramodule_path += '/' + token
        if node_type is NodeType.MODULE:
            current_node = self.follow_token_module(token)
        elif node_type is NodeType.SWITCH:
            current_node = self.follow_token_switch(token_node, token)
        elif node_type is NodeType.LOOP:
            current_node = token_node
        else:
            current_node = token_node
        return current_node, intramodule_path


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
    
    def get_maestro_node_from_path(self, node_path):
        xml_node, intramodule_path = self.get_xml_node_from_path(node_path)
        n = ExperimentRunNode(xml_node=xml_node, node_path=node_path, exp_run=self, intramodule_path=intramodule_path, name=None, node_name=None, module=None, datestamp=None, exp_home=self.exp_home, node_function=lambda e: print(e))

class ResourceVisitor:
    def __init__(self, exp_home, datestamp=None):
        self.exp_home = exp_home
        self.datestamp = datestamp
    def visit_resources(self, node_path, function, ndp):
        if not ndp:
            ndp = ExperimentRunNode(exp_home=self.exp_home, datestamp=None, name=None, node_name=node_path, module=None, intramodule_path=None, node_function=lambda e: print(e))
        xml_resource_file = f'{self.exp_home}/resources/{node_path}/container.xml'
        if not os.path.exists(xml_resource_file):
            self.xml_fallbackDoc(xml_resource_file, NodeType.LOOP)
        first_xml_context = ET.parse(xml_resource_file)
        root = first_xml_context.getroot()
        self.visit_node_dfs_preorder(ndp, root, function)
    def visit_node_dfs_preorder(self, ndp, node, function=None, depth=0):
        # TODO : I could define a base step and a recursion step function
        #        and use that to make the two revisit functions
        function(node)
        self.getLoopAttributes(ndp, node)
        self.visit_non_validity_children(node, function=function)
        for child in node.findall('VALIDITY'):
            self.visit_node_dfs_preorder(ndp, child, function, depth+1)
    def visit_node_dfs_postorder(self, node, function=None, depth=0):
        for child in node.findall('VALIDITY'):
            self.visit_node_dfs_postorder(child, function, depth+1)
        self.visit_non_validity_children(node, function=function)
        function(node)
    def visit_non_validity_children(self, node, function=None):
        for loop in node.findall('LOOP'):
            function(loop)

    def xml_fallbackDoc(self, xmlFile, nodeType):
        content = '<NODE_RESOURCES>\n'
        
        if nodeType is NodeType.LOOP:
            content += '    <LOOP start="0" set="1" end="1" step="1"/>\n'
        content += '</NODE_RESOURCES>'
        with open(xmlFile, 'a+') as f:
            f.write(content)
        xml_tree = ET.parse(xmlFile)
        return xml_tree.getroot()
    def parse_node_specifics(self, ndp, node_type, xml_node):
        for child in xml_node:
            ndp.specific_data.update(child.attrib)
            print(child.attrib)
        if node_type is NodeType.LOOP:
            ndp.specific_data['TYPE'] = "DEFAULT"
    def getLoopAttributes(self, ndp, xml_node):
        self.parse_node_specifics(ndp, NodeType.LOOP, xml_node)
        resources_found = False
        if resources_found == False:
            return True
    def parseForeachTarget(self, ndp, xml_node):
        ndp.foreach_target.node = xml_node.attrib.get('node')
        ndp.foreach_target.index = xml_node.attrib.get('node')
        ndp.foreach_target.exp = xml_node.attrib.get('node')
        ndp.foreach_target.hour = xml_node.attrib.get('node')
    def getForEachAttributes(self, ndp, xml_node):
        self.parseForeachTarget(ndp, xml_node)
    def parse_batch_resources(self, ndp, xml_node):
        ndp.cpu_multiplier = xml_node.attrib.get('cpu_multiplier')
        ndp.machine = xml_node.attrib.get('machine')
        ndp.memory = xml_node.attrib.get('memory')
        ndp.queue = xml_node.attrib.get('queue')
        ndp.mpi = xml_node.attrib.get('mpi')
        ndp.soumet_args = xml_node.attrib.get('soumet_args')
        ndp.workq = xml_node.attrib.get('workq')
        ndp.wallclock = xml_node.attrib.get('wallclock')
        ndp.immediate = xml_node.attrib.get('immediate')
        ndp.catchup = xml_node.attrib.get('catchup')
        ndp.shell = xml_node.attrib.get('shell')
    def getBatchAttributes(self, ndp, xml_node):
        self.parse_batch_resources(ndp, xml_node)
    def parse_depends(self, ndp, xml_node):
        for dep in xml_node.findall('DEPENDS_ON'):
            # Create a Dependency instance from the attributes of the dep xml node
            # Append it to ndp.dependencies
            print(dep)
    def getDependencies(self, ndp, xml_node):
        self.parse_depends(ndp, xml_node)
    def getAbortActions(self, ndp, xml_node):
        for abort_action in xml_node.findall('ABORT_ACTION'):
            ndp.abort_actions.append(abort_action.attrib['name'])
    def getNodeLoopContainersAttr (self, ndp, xml_node):
        self.visit_node_dfs_preorder(ndp, xml_node, self.get_container_loop_attributes)
    def get_container_loop_attributes(self, ndp, xml_node):
        for child in xml_node.find('LOOP'):
            ndp.loops.append(child.attrib)
    def getWorkerPath(self, ndp, xml_node):
        for worker in xml_node.find('WORKER'):
            ndp.worker_path = worker.attrib['path']
    def setWorkerData(self, ndp, xml_node):
        self.visit_node_dfs_preorder(ndp, xml_node, self.getBatchAttributes)
    def validateMachine(self, ndp, xml_node):
        ndp.machine = 'eccc-ppp4'
    def setShell(self, ndp, xml_node):
        ndp.shell = '/bin/bash'
    def do_all(self, ndp, xml_node):
        if ndp.type is NodeType.LOOP:
            self.getLoopAttributes(ndp, xml_node)
        elif ndp.type is NodeType.FOREACH:
            self.getForEachAttributes(ndp, xml_node)
        self.getBatchAttributes(ndp, xml_node)
        self.getDependencies(ndp, xml_node)
        self.getAbortActions(ndp, xml_node)

        

    #def parseWorkerPath( const char * pathToNode, const char * _seq_exp_home, SeqNodeDataPtr _nodeDataPtr);
    #def getNodeResources(SeqNodeDataPtr _nodeDataPtr, const char * expHome, const char * nodePath);

            
class ForeachTarget:
    def __init__(self):
        self.index = ""
        self.exp = ""
        self.node = ""
        self.houre = ""
class ExperimentRunNode:
    def __init__(self, *args, **kwargs):
        self.specific_data = {}
        self.name = kwargs['name']
        self.node_name = kwargs['node_name']
        # From SeqNode_createNode
        self.container = None if not kwargs.get('container') else self.name.split('/')[:-1]
        self.node_basename = None if not kwargs.get('container') else self.name.split('/')[-1]
        self.intramodule_container = kwargs['intramodule_path']
        self.module = kwargs['module']
        self.silent = kwargs.get('silent', 0)
        self.catchup = kwargs.get('catchup', 0)
        self.mpi = kwargs.get('mpi', 0)
        self.wallclock = kwargs.get('wallclock', 0)
        self.is_last_arg = kwargs.get('is_last_arg', False)
        self.queue = kwargs.get('queue', 0)
        self.machine = kwargs.get('machine', 'eccc-ppp4')
        self.memory = kwargs.get('memory', '10GB')
        self.cpu = kwargs.get('cpu', 1)
        self.npex = kwargs.get('npex', '')
        self.npey = kwargs.get('npey', '')
        self.omp = kwargs.get('omp', '')
        self.soumet_args = kwargs.get('soumet_args', '')
        self.work_queue = kwargs.get('work_queue', '')
        self.worker_path = kwargs.get('worker_path', '')
        self.alias = kwargs.get('alias', '')
        self.args = kwargs.get('args', '')
        self.datestamp = kwargs['datestamp']
        self.submit_origin = kwargs.get('submit_origin')
        self.work_dir = kwargs.get('work_dir', None)
        self.exp_home = kwargs['exp_home']
        self.shell = kwargs.get('shell', '/bin/bash')
        self.switch_answers = kwargs.get('switch_answers', []) # TODO Needs to be built up while parsing the path
        self.foreach_target = ForeachTarget()
        self.dependencies = kwargs.get('dependencies', [])
        self.submits = kwargs.get('submits', [])
        self.abort_actions = kwargs.get('abort_actions', [])
        self.siblings = kwargs.get('siblings', [])
        self.parent_loops = kwargs.get('paren_loop', [])
        self.data = kwargs.get('data', {})
        self.loop_args = kwargs.get('loop_args', {})
        self.loop_extension = kwargs.get('loop_extension', '')
        # Same as intramodule_path
        self.task_path = kwargs.get('task_path', None)


# Resource_createContext
# if ( nodeType == Loop || nodeType == ForEach ){
#          raiseError("createResourceContext(): Cannot access mandatory resource file %s\n", xmlFile);
#       } else {
#          context = NULL;
#          goto out;
#       }

if __name__ == "__main__":
    p_good = 'module2/dhour_switch/loop/family/task'
    p_bad = 'module2/dhour_switch/lop/family/task'
    v = FlowVisitor(os.getcwd() + '/experiments/sample_exp/')
    v.visit_flow()
    exp = ExperimentRun(exp_home=f'{os.getcwd()}/experiments/sample_exp/')
    exp.get_maestro_node_from_path(p_good)
    print(f"Trying with path = {p_good}")
    n, imp = exp.get_xml_node_from_path(p_good)
    print(f'>> Found element {n}, [intramodule_path:{imp}]')
    print(f"Trying with path = {p_bad}")
    # try:
    #     exp.get_xml_node_from_path(p_bad)
    # except PathTokenError as e:
    #     print(f"ERROR: Bad token {e} in path '{p_bad}'")
    exp_home = f'{os.getcwd()}/experiments/sample_exp'
    node_path_with_resources = 'module/module2/dhour_switch/loop'
    rv = ResourceVisitor(exp_home)
    rv.visit_resources(node_path_with_resources, lambda n: print(n), None)

