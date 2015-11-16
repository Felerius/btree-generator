#!/usr/bin/env python3
"""A script to generate dot files for nice looking B+ tree diagrams."""
import collections
import itertools

GRAPH_TEMPLATE = """digraph G
{{
    splines=false
{nodes}
{connections}
}}"""

NODES_INDENT = 4
CONNECTIONS_INDENT = 4

NODE_TEMPLATE = """"{name}"
[
    shape = none
    label = <<table border="1" cellborder="0" cellspacing="0">
                <tr>
{cells}
                </tr>
            </table>>
]"""

CELL_INDENT = 20
CONNECTOR_TEMPLATE = '<td port="connector{number}"></td>'
CONNECTOR_NAME_TEMPLATE = 'connector{number}'
CELL_TEMPLATE = '<td>{content}</td>'
CELL_MIDDLE_TEMPLATE = '<td port="middle">{content}</td>'
CONNECTION_TEMPLATE = '"{src_node}":"{src_connector}" -> "{dst_node}":"{dst_connector}"'

DUMMY_KEY = '_'


NodeData = collections.namedtuple('NodeData', [
    'name',
    'middle_connector',
    'generated_nodes',
    'generated_connections'
])


def indent(string, num_spaces):
    """Indents a string to a certain level."""
    indent_string = num_spaces * ' '
    return indent_string + string.replace('\n', '\n' + indent_string)


def fill_to_length(item_list, length, fill_item):
    """Appends dummy items to a list to make it a certain length."""
    num_missing = length - len(item_list)
    if length > 0:
        return itertools.chain(
            item_list,
            itertools.repeat(fill_item, num_missing)
        )
    return item_list


def generate_graph(data):
    """Generates a graph in dot language from input data."""
    keys_per_block = data.get('keys_per_block')
    root_data = generate_node_graph(data, '0', keys_per_block)
    nodes = indent('\n'.join(root_data.generated_nodes), NODES_INDENT)
    connections = indent(
        '\n'.join(root_data.generated_connections),
        CONNECTIONS_INDENT
    )
    return GRAPH_TEMPLATE.format(
        nodes=nodes,
        connections=connections
    )


def generate_node_graph(node_data, name, keys_per_block):
    """Generate NodeData for a single node and its descendents."""
    if isinstance(node_data, list):
        node_data = {'keys': node_data}
    if 'keys' not in node_data:
        return NodeData(name, None, [], [])
    keys = fill_to_length(node_data['keys'], keys_per_block, DUMMY_KEY)
    middle_connector, cells = generate_cells(keys, keys_per_block)
    cells_str = indent('\n'.join(cells), CELL_INDENT)
    node = NODE_TEMPLATE.format(name=name, cells=cells_str)
    sub_nodes = []
    if 'children' in node_data:
        sub_nodes = [
            generate_node_graph(child, name + '.' + str(i), keys_per_block)
            for i, child in enumerate(node_data['children'])
        ]
    connections = [
        CONNECTION_TEMPLATE.format(
            src_node=name,
            src_connector=CONNECTOR_NAME_TEMPLATE.format(number=i),
            dst_node=child_node.name,
            dst_connector=child_node.middle_connector
        )
        for i, child_node in enumerate(sub_nodes)
    ]
    all_nodes = itertools.chain(
        [node],
        *(child_node.generated_nodes for child_node in sub_nodes)
    )
    all_connections = itertools.chain(
        connections,
        *(child_node.generated_connections for child_node in sub_nodes)
    )
    return NodeData(name, middle_connector, all_nodes, all_connections)


def generate_cells(keys, keys_per_block):
    """Generate cells for a single block from it's keys.

    Argument keys_per_block is only there, so that we can avoid creating
    lists of keys and instead keep them generators.
    """
    needs_middle = (keys_per_block % 2 == 1)
    cells = []
    for i, key in enumerate(keys):
        cells.append(CONNECTOR_TEMPLATE.format(number=i))
        if needs_middle and i == (keys_per_block // 2):
            cells.append(CELL_MIDDLE_TEMPLATE.format(content=key))
        else:
            cells.append(CELL_TEMPLATE.format(content=key))
    cells.append(CONNECTOR_TEMPLATE.format(number=keys_per_block))
    if needs_middle:
        return 'middle', cells
    return CONNECTOR_NAME_TEMPLATE.format(number=keys_per_block // 2), cells


def main():
    """Main function. Called when run as main module."""
    import sys
    import yaml
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as in_file:
            data = yaml.safe_load(in_file)
    else:
        data = yaml.safe_load(sys.stdin)
    print(generate_graph(data))


if __name__ == '__main__':
    main()
