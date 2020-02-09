/* FlowVisitor.h - Visits flow.xml files to assign flow information to a
 * nodeDataPtr.
 * Copyright (C) 2011-2015  Operations division of the Canadian Meteorological Centre
 *                          Environment Canada
 *
 * Maestro is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation,
 * version 2.1 of the License.
 *
 * Maestro is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */
#ifndef _FLOW_VISITOR_H_
#define _FLOW_VISITOR_H_
#include "SeqNode.h"

#define MAX_CONTEXT_STACK_SIZE 20

#define FLOW_SUCCESS 0
#define FLOW_FAILURE -1
#define FLOW_TRUE 1
#define FLOW_FALSE 0

/*
 * IDEA FOR SWITCHES
 *
 * I recently had to find the right switch item to take based off a datestamp
 * yet without having a nodeDataPtr.  This led to some slightly inelegant code
 * with the generic switches coming up, I think I might need to do the
 * following:
 *
 * Finding the correct switch item is only done with the datestamp, but a more
 * general approach, if we want to add attributes that can decide what
 * SWITCH_ITEM is taken would be to have a struct like this
 *
 * struct SwitchContext{
 *    char *datestamp;
 *    char *color;
 *    char *mood;
 * }switch_context;
 *
 * that we could put as an attribute of the FlowVisitor struct.
 *
 * Right now, functions like SwitchReturn() take a nodeDataPtr as an argument
 * but in the context of SeqNodeCensus, we don't have a nodeDataPtr to give to
 * SwitchReturn().  We have to create one, only for the sake of passing a
 * datestamp to it:
 *
 * SeqNodeData nd;
 * nd.datestamp = datestamp;
 * switch_answer = SwitchReturn(&nd, switch_type);
 * // forget about nd.
 */



/********************************************************************************
 * This structure contains information that is passed along through the various
 * functions used in getFlowInfo.  Since various parts of the code modify, add
 * to and use these fields, they are passed through this struct to most of the
 * functions.
 *
 * There is possibly more in here than is needed but this will be dealt with as
 * work progresses.
 *
 * Note on switch_args: Special purpose internal mechanism for controlling the
 * behavior of the visitor when it encounters SWITCH_ITEMS.  The presence (when
 * it is not null) of switch_args in the visitor will cause the visitor to
 * ignore the context when choosing which SWITCH_ITEM to enter and instead, look
 * in the switch_args string to decide.  This is so that the FlowVisitor can be
 * used to create the nodeinfo database required by bug4869.  It is necessary to
 * ignore the context in this situation because we must have all posssible
 * nodes, and not just the ones that 'exist in the current context'.
********************************************************************************/
typedef struct _FlowVisitor{
   char * nodePath;
   char * switch_args;
   const char * expHome;
   const char * datestamp;
   char * currentFlowNode;
   char * taskPath;
   char * suiteName;
   char * module;
   char * intramodulePath;
   int currentNodeType;
   xmlXPathContextPtr context;

   xmlXPathContextPtr _context_stack[MAX_CONTEXT_STACK_SIZE];
   int _stackSize;
} FlowVisitor;

typedef FlowVisitor* FlowVisitorPtr;

int _pushContext(FlowVisitorPtr fv, xmlXPathContextPtr context);
int Flow_saveContext(FlowVisitorPtr fv);
xmlXPathContextPtr _popContext(FlowVisitorPtr fv);
int Flow_restoreContext(FlowVisitorPtr fv);
xmlXPathContextPtr Flow_previousContext(FlowVisitorPtr fv);

/********************************************************************************
 * Initializes the flow_visitor to the entry module;
 * Caller should check if the return pointer is NULL.
********************************************************************************/
FlowVisitorPtr Flow_newVisitor(const char *nodePath, const char *seq_exp_home,
                                                     const char *switch_args);

/********************************************************************************
 * Destructor for the flow_visitor object.
********************************************************************************/
int Flow_deleteVisitor(FlowVisitorPtr _flow_visitor);

/********************************************************************************
 * Parses the given nodePath while gathering information and adding attributes
 * to the nodeDataPtr;
 * returns FLOW_SUCCESS if it is able to completely parse the path
 * returns FLOW_FAILURE otherwise.
********************************************************************************/
int Flow_parsePath(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr,
                                                        const char * _nodePath);

/********************************************************************************
 * Tries to get to the node specified by nodePath.
 * Returns FLOW_FAILURE if it can't get to it,
 * Returns FLOW_SUCCESS if it can go through the whole path without a query
 * failing.
 * Note that if the last query was successful, the path walk is considered
 * successful and we don't have to move to the next switch item.
********************************************************************************/
int Flow_walkPath(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr, const char * nodePath);

/********************************************************************************
 * Sets the XML XPath context's current node to the child of the current node
 * whose name attribute matches the nodeName parameter.
********************************************************************************/
int Flow_doNodeQuery(FlowVisitorPtr _flow_visitor, const char * nodeName, int isFirst);

/********************************************************************************
 * Changes the current module of the flow visitor.
 * returns FLOW_FAILURE if either the XML file cannot be parsed or an initial
 *                      "MODULE" query fails to return a result.
 * returns FLOW_SUCCESS oterwise.
********************************************************************************/
int Flow_changeModule(FlowVisitorPtr _flow_visitor, const char * module);

/********************************************************************************
 * Changes the current xml document and context to a new one specified by
 * xmlFilename and saves the previous document and context.
 * Returns FLOW_SUCCESS if the XML file can be successfuly parsed and
 * Returns FLOW_FAILURE otherwise.
********************************************************************************/
int Flow_changeXmlFile(FlowVisitorPtr _flow_visitor, const char * xmlFilename);

/********************************************************************************
 * Appends things to the various paths we are constructing in getFlowInfo.
********************************************************************************/
int Flow_updatePaths(FlowVisitorPtr _flow_visitor, const char * pathToken, const int container);

/********************************************************************************
 * Parses the attributes of a switch node into the nodeDataPtr.
 * Returns FLOW_SUCCESS if the right switch item (or default) is found.
 * Returns FLOW_FAILURE otherwise.
********************************************************************************/
int Flow_parseSwitchAttributes(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr, int isLast );

/********************************************************************************
 * This function returns the switch type of the current node in the XML XPath
 * context
********************************************************************************/
const char * Flow_findSwitchType(const FlowVisitorPtr _flow_visitor );

/********************************************************************************
 * Moves the flow visitor to the switch item of the current node whose name
 * contains switchValue or to the default if no switch item matches switchValue.
 * Returns FLOW_SUCCESS if a valid switch item is found.
 * Returns FLOW_FAILURE if no switch item is found.
********************************************************************************/
int Flow_findSwitchItem( FlowVisitorPtr _flow_visitor,const char *switchValue );

/********************************************************************************
 * Moves visitor to switch item child that has switchValue if it exists
 * Returns FLOW_FAILURE on failure
 * Returns FLOW_SUCCESS on success
********************************************************************************/
int Flow_findSwitchItemWithValue( FlowVisitorPtr _flow_visitor, const char * switchValue);

/********************************************************************************
 * Moves visitor to default switch item child of current node if it exists.
 * Returns FLOW_FAILURE on failure
 * Returns FLOW_SUCCESS on success
********************************************************************************/
int Flow_findDefaultSwitchItem( FlowVisitorPtr _flow_visitor);

/********************************************************************************
 * Returns FLOW_TRUE if the SWITCH_ITEM currentNodePtr has the argument switchValue as
 * one of the tokens in it's name attribute.
 * Note that we use the XML XPath context to perform the attribute search.  For
 * this, we need to change the context's current node temporarily and restore it
 * upon exiting the function.
********************************************************************************/
int Flow_switchItemHasValue(const FlowVisitorPtr _flow_visitor, xmlNodePtr currentNodePtr, const char*  switchValue);

/********************************************************************************
 * Parses the string name as a comma separated list of values and returns 1 if
 * the argument value is one of those values.
 * Returns FLOW_TRUE if the name does contain the switchValue and
 * returns FLOW_FALSE otherwise.
********************************************************************************/
int switchNameContains(const char * name, const char * switchValue);

/********************************************************************************
 * Parses worker path for current node if said node has a work_unit attribute.
********************************************************************************/
int Flow_checkWorkUnit(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Sets the nodeDataPtr's pathToModule, taskPath, suiteName, module and
 * intramodulePath from info gathered while parsing the xml files.
********************************************************************************/
int Flow_setPathData(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Sets the pathToModule of the node by subtracting the intramodulePath from
 * _nodeDataPtr->container.
********************************************************************************/
int Flow_setPathToModule(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Sets the suiteName based on the experiment home.
********************************************************************************/
int Flow_setSuiteName(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Adds flow dependencies to _nodeDataPtr
 * Returns FLOW_SUCCESS if there are dependencies,
 * Returns FLOW_FAILURE if there are none.  It should probably still return
 * FLOW_SUCCESS even if there are no dependencies.
********************************************************************************/
int Flow_parseDependencies(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Parses submits into _nodeDataPtr
********************************************************************************/
int Flow_parseSubmits(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Parses the preceding sibings and following siblings into _nodeDataPtr
 * We should get this tracinf info out of here, it clutters the code and nobody
 * is going to see it.  There should be a function to print this stuff.
********************************************************************************/
int Flow_parseSiblings(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Calls parseNodeSpecifics with the attributes of the current node of the flow
 * visitor.
********************************************************************************/
int Flow_parseSpecifics(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr);

/********************************************************************************
 * Prints the current information of the visitor
********************************************************************************/
void Flow_print_state(FlowVisitorPtr _flow_visitor, int trace_level);

#endif /* _FLOW_VISITOR_H */
