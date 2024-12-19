from lxml import etree


def generate_html_from_xsd(xsd_file):
    tree = etree.parse(xsd_file)
    root = tree.getroot()

    html_code = []
    visited = set()

    def process_element(element, path=""):
        name = element.get("name")
        type_ref = element.get("type", "")
        element_id = (path, name)

        print(f"Processing element: name={name}, type_ref={type_ref}, path={path}")

        if not name or element_id in visited:
            print(f"Skipping element: name={name}, path={path} (already visited or no name)")
            return

        visited.add(element_id)
        input_name = f"{path}[{name}]" if path else name

        if type_ref.startswith("dac6:"):
            type_ref = type_ref.split(':')[-1]

        if type_ref.startswith("xsd:"):
            print(f"Found base type: {type_ref}")
            if type_ref == "xsd:string":
                html_code.append(f'<label>{name}: <input type="text" name="{input_name}" required></label><br>')
            elif type_ref == "xsd:integer":
                html_code.append(f'<label>{name}: <input type="number" name="{input_name}"></label><br>')
            elif type_ref == "xsd:boolean":
                print(html_code)
                html_code.append(f'<label>{name}: <input type="checkbox" name="{input_name}"></label><br>')
            elif type_ref == "xsd:date":
                html_code.append(f'<label>{name}: <input type="date" name="{input_name}"></label><br>')
            return

        print(f"Searching for complexType: {type_ref}")
        complex_type = root.find(f".//xsd:complexType[@name='{type_ref}']",
                                 namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
        if complex_type is not None:
            print(f"Found complexType: {type_ref}")
            html_code.append(f'<fieldset id="{input_name}_container"><legend>{name}</legend>')
            sequence = complex_type.find("xsd:sequence", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if sequence is not None:
                for child in sequence.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                    process_element(child, input_name)
            html_code.append("</fieldset>")
            return

        print(f"Searching for local complexType in element: {name}")
        local_complex_type = element.find("xsd:complexType", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
        if local_complex_type is not None:
            print(f"Found local complexType in element: {name}")
            html_code.append(f'<fieldset id="{input_name}_container"><legend>{name}</legend>')
            sequence = local_complex_type.find("xsd:sequence", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if sequence is not None:
                for child in sequence.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                    process_element(child, input_name)
            html_code.append("</fieldset>")
            return

        print(f"Searching for simpleType: {type_ref}")
        simple_type = root.find(f".//xsd:simpleType[@name='{type_ref}']",
                                namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
        if simple_type is not None:
            restriction = simple_type.find("xsd:restriction", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            base_type = restriction.get("base") if restriction is not None else ""
            print(f"Found simpleType: {type_ref}, base_type={base_type}, simpleType name={simple_type.get('name')}")
            if base_type == "xsd:string":
                html_code.append(f'<label>{name}: <input type="text" name="{input_name}" required></label><br>')
            elif base_type == "xsd:integer":
                html_code.append(f'<label>{name}: <input type="number" name="{input_name}"></label><br>')
            elif base_type == "xsd:boolean":
                html_code.append(f'<label>{name}: <input type="checkbox" name="{input_name}"></label><br>')
            elif base_type == "xsd:date":
                html_code.append(f'<label>{name}: <input type="date" name="{input_name}"></label><br>')
            return

    top_element = root.find(".//xsd:element[@name='DAC6Dispositif']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
    if top_element is not None:
        process_element(top_element)

    html_code.insert(0, "<form id='dac6-form'>")
    html_code.append("<button type='submit'>Soumettre</button>")
    html_code.append("</form>")

    return "\n".join(html_code)

# Exemple d'utilisation
xsd_file = '/Users/antoine/Downloads/Dac6XML_FR_V.3.02.xsd'
html_output = generate_html_from_xsd(xsd_file)

# Sauvegarde dans un fichier HTML
output_file = 'output.html'
with open(output_file, 'w') as f:
    f.write(html_output)

print(f"Formulaire généré et enregistré dans {output_file}")
