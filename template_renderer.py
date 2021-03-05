import colorsys
import json

from jinja2 import Environment, PackageLoader
import graph


def create_html(formatted_nodes, formatted_edges, role_color_map, output_name):
    env = Environment(loader=PackageLoader('visualisation', '.'))
    template = env.get_template('visualisation.template')
    default_filters = list(graph.type_properties.keys())
    all_roles=list(role_color_map.keys())
    print(all_roles)
    html = template.render(formatted_nodes=formatted_nodes,
                           formatted_edges=formatted_edges,
                           type_properties=graph.type_properties,
                           default_filters=default_filters,
                           all_roles=all_roles)
    with open(output_name, "w+") as resource_file:
        resource_file.write(html)




def get_description(node):
    desc = node.get_type_name() + "</br>"
    if node.title:
        desc = desc + node.title + "</br>"
    if node.properties:
        for k, v in node.properties.items():
            desc = desc + k + ": " + str(v) + "</br>"
    return desc


def render(nodes, edges, output_name):
    color_map = roles_to_color_map(edges=edges)
    formatted_nodes, formatted_edges = format_graph(nodes, edges, color_map)

    create_html(formatted_nodes, formatted_edges, color_map, output_name)


def color_for_role(role, all_roles):
    hue = float(all_roles.index(role)) / len(all_roles)
    return '#%02x%02x%02x' % tuple(int(c) * 255 for c in colorsys.hsv_to_rgb(hue, 1, 0.85))


def sanitise_role(role):
    return str(role).replace('roles/', '') \
        .lower() \
        .replace('writer', 'editor') \
        .replace('reader', 'viewer')


def roles_to_color_map(edges):
    all_roles = list({sanitise_role(e.role) for e in edges if e.role})
    role_map = {}
    for role in all_roles:
        role_map[role] = color_for_role(role, all_roles)
    role_map['other'] = '#00c0ff'
    return role_map


def format_graph(nodes, edges, role_color_map):
    nodes_list = []
    node_ids = {}

    for counter, node in enumerate(nodes):
        node_ids[node.id] = counter
        value = {
            'id': counter,
            'shape': 'icon',
            'label': node.name,
            'type': node.node_type,
            'icon': {
                'face': 'Font Awesome 5 Free',
                'code': node.get_font_code(),
                'size': node.get_size(),
                'color': node.get_color(),
                'weight': 'bold'
            }
        }
        description = get_description(node)
        if description:
            value['title'] = description
        nodes_list.append(json.dumps(value).replace("\\\\", "\\"))

    edges_list = []

    for edge in edges:
        value = {
            'from': node_ids[edge.node_from.id],
            'to': node_ids[edge.node_to.id],
            'arrows': 'to',
        }
        if edge.label:
            value['label'] = edge.label
        if edge.title:
            value['title'] = edge.title
        value['role'] = sanitise_role(edge.role) if edge.role else 'other'
        value['color'] = role_color_map[value['role']]
        edges_list.append(json.dumps(value))
    return nodes_list, edges_list