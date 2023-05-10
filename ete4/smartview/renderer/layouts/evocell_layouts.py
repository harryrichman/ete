from ..faces import RectFace, TextFace
from ..treelayout import TreeLayout
from collections import  OrderedDict

__all__ = [ "LayoutHumanOGs", "LayoutUCSC", "LayoutUCSCtrans", "LayoutSciName", "LayoutColorClade", "LayoutEvolEvents"]

sciName2color = {}
taxid2color = {}
try:
    with open(Path(__file__).parent / 'spongilla_taxa_color_codes.csv') as t:
        for line in t:
            if not line.startswith('#'):
                info = line.split('\t')
                sciName2color[(info[0])] = info[3].strip()
                taxid2color[int(info[1])] = info[3].strip()
except:
    pass

class LayoutHumanOGs(TreeLayout):
    def __init__(self, name="Human OGs", human_orth_prop="human_orth",
                 column=5, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.human_orth_prop = human_orth_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            human_orth = node.props.get(self.human_orth_prop)
            if human_orth and human_orth != 'NaN':
                human_orth = " ".join(human_orth.split('|'))
                human_orth_face = TextFace(human_orth, color=self.color)
                # human_orth_face = RectFace(width=20, height=None, color=self.color, \
                #     padding_x=1 , padding_y=0, tooltip=None)
                node.add_face(human_orth_face, column=self.column, position="aligned")

class LayoutUCSC(TreeLayout):
    def __init__(self, name="UCSC", column=6,
                 nodecolor="#800000", nodesize=5,
                 textcolor="#c43b5d"):
        super().__init__(name)
        self.aligned_faces = True
        self.column = column
        self.nodecolor = nodecolor
        self.nodesize = nodesize
        self.textcolor = textcolor

    def set_node_style(self, node):
        if not node.is_leaf():
            return

        if node.props.get('UCSC') and node.props.get('UCSC') != 'NaN':
            ucsc = node.props.get('UCSC')
            #ucsc_face = TextFace(ucsc, color=self.textcolor)
            #node.add_face(ucsc_face, column=self.column, position="aligned")
            node.sm_style["bgcolor"] = self.nodecolor # highligh clade
            
            if node.props.get('tooltip'):
                pass
            else:
                tooltip = '<ul>'+'<br>'.join(f'{key}: {add_ucsc_link(value) if key == "UCSC" else value}'
                                  for key, value in node.props.items()) + '</ul>'
                node.add_prop("tooltip", tooltip)

            while (node):
                node = node.up
                if node:
                    node.sm_style["hz_line_width"] = self.nodesize

def add_ucsc_link(text):
    output_html = []
    ucsc_portals = text.split('|')
    for sub_portal in ucsc_portals:
        entry, specie, organism = sub_portal.split('__')
        html = f'<li><a target="_blank" href="https://cells-test.gi.ucsc.edu/?ds=evocell+{entry}">{organism} {specie}</a></li>'
        output_html.append(html)
    return ''.join(output_html)

class LayoutUCSCtrans(TreeLayout):
    def __init__(self, name="UCSC Gene", ucsc_trans_prop="ucsc_trans",
                 column=4, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.ucsc_trans_prop = ucsc_trans_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            ucsc_trans = node.props.get(self.ucsc_trans_prop)
            if ucsc_trans and ucsc_trans != 'NaN':
                ucsc_trans = " ".join(ucsc_trans.split('|'))
                ucsc_trans_face = TextFace(ucsc_trans, color=self.color)
                # ucsc_trans_face = RectFace(width=70, height=None, color=self.color, \
                #     padding_x=1 , padding_y=0, tooltip=None)
                node.add_face(ucsc_trans_face, column=self.column, position="aligned")

class LayoutSciName(TreeLayout):
    def __init__(self, name="Scientific name"):
        super().__init__(name, aligned_faces=True)

    def set_node_style(self, node):
        if node.is_leaf():
           
            sci_name = node.props.get('sci_name')
            prot_id = node.name.split('.', 1)[1]

            if node.props.get('sci_name_color'):
                color = node.props.get('sci_name_color')
                # node.sm_style["hz_line_color"] = color
                # node.sm_style["hz_line_width"] = 2
            else:
                color = 'black'
            node.add_face(TextFace(sci_name, color = color, padding_x=2),
                column=0, position="branch_right")
            # if len(prot_id) > 40:
            #     prot_id = prot_id[0:37] + " ..."
            
            # node.add_face(TextFace(prot_id, color = 'Gray', padding_x=2), column = 2, position = "aligned")
        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                # if text in sciName2color.keys():
                #     color = sciName2color[text]
                # else:
                color = 'black'
                node.add_face(TextFace(text, padding_x=2, color = color),
                        position="branch_right", column=1, collapsed_only=True)

class LayoutColorClade(TreeLayout):
    def __init__(self, name="Taxa Clade"):
        super().__init__(name, aligned_faces=True)
    
    def set_node_style(self, node):
        if node.props.get('sci_name_color'):
            sci_name = node.props.get('sci_name')
            if node.props.get('sci_name_color'):
                color = node.props.get('sci_name_color')
                node.sm_style["hz_line_color"] = color
                node.sm_style["hz_line_width"] = 2
                node.sm_style["vt_line_color"] = color
                node.sm_style["vt_line_width"] = 2

            else:
                color = 'black'
            node.add_face(TextFace(sci_name, color = color, padding_x=2),
                column=0, position="branch_right")

class LayoutEvolEvents(TreeLayout):
    def __init__(self, name="Evolutionary events", 
            prop="evoltype",
            speciation_color="blue", 
            duplication_color="red",
            legend=True):
        super().__init__(name)
        
        self.prop = prop
        self.speciation_color = speciation_color
        self.duplication_color = duplication_color
        self.legend = legend

        self.active = True

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)
        if self.legend:
            colormap = { "Speciation event": self.speciation_color,
                         "Duplication event": self.duplication_color }
            tree_style.add_legend(title=self.name, 
                    variable="discrete",
                    colormap=colormap)

    def set_node_style(self, node):
        if not node.is_leaf():
            if node.props.get(self.prop, "") == "S":
                node.sm_style["fgcolor"] = self.speciation_color
                node.sm_style["size"] = 2

            elif node.props.get(self.prop, "") == "D":
                node.sm_style["fgcolor"] = self.duplication_color
                node.sm_style["size"] = 2

def summary(nodes):
    "Return a list of names summarizing the given list of nodes"
    return list(OrderedDict((first_name(node), None) for node in nodes).keys())

def first_name(tree):
    "Return the name of the first node that has a name"
    
    sci_names = []
    for node in tree.traverse('preorder'):
        if node.is_leaf():
            sci_name = node.props.get('sci_name')
            sci_names.append(sci_name)

    return next(iter(sci_names))
