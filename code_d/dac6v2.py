from lxml import etree

html_code = []


def handle_node(name, input_name, type_ref, restriction="", annotation=""):

    #  handle restriction, handle attribute

    if type_ref == "xsd:string":
        html_code.append(f'<label>{name}{annotation}: <input type="text" name="{input_name}" {restriction}></label><br>')
    elif type_ref == "xsd:integer":
        html_code.append(f'<label>{name}{annotation}: <input type="number" name="{input_name}" {restriction}></label><br>')
    elif type_ref == "xsd:boolean":
        html_code.append(f'<label>{name}{annotation}: <input type="checkbox" name="{input_name}" {restriction}></label><br>')
    elif type_ref == "xsd:date":
        html_code.append(f'<label>{name}{annotation}: <input type="date" name="{input_name}" {restriction}></label><br>')
    elif type_ref == "xsd:dateTime":
        html_code.append(f'<label>{name}{annotation}: <input type= "datetime-local" name="{input_name}" {restriction}></label><br>')
    return


def generate_html_from_xsd(xsd_file):

    tree = etree.parse(xsd_file)
    root = tree.getroot()

    def process_element(element, path="", annotation="", restriction="", is_attribute=False, is_template=False):

        name = element.get("name")
        type_ref = element.get("type", "")

        max_occurs = element.get("maxOccurs", "")

        if max_occurs:
            is_template = True
            print("maxxx", max_occurs)

        print(f"Processing element: name={name}, type_ref={type_ref}, path={path}")

        template_suffix = "_template" if is_template else ""

        if is_attribute:
            input_name = f"{path}[{name}{template_suffix}§is_attribute]" if path else f"{name}{template_suffix}"
        else:
            input_name = f"{path}[{name}{template_suffix}]" if path else f"{name}{template_suffix}"

        if type_ref.startswith("dac6:"):
            type_ref = type_ref.split(':')[-1]

        if type_ref in ["xsd:string", "xsd:integer", "xsd:boolean", "xsd:date", "xsd:dateTime"]:
            print("in node")
            handle_node(name, input_name, type_ref, annotation, restriction)
            return

        complex_type = root.find(f".//xsd:complexType[@name='{type_ref}']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
        print(f".//xsd:complexType[@name='{type_ref}']")

        if complex_type is None:
            print("local complex type")
            complex_type = element.find("xsd:complexType", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
        else:
            print("global complex type")

        if complex_type is not None:
            print("in complex")

            if is_template:
                html_code.append(f'<button type="button" onclick="addElement(\'{path}\', \'{name}\')">Ajouter un {name}</button>')

            html_code.append(f'<fieldset id="{input_name}_container"><legend>{name}</legend>')

            annotation = complex_type.find("xsd:annotation/xsd:documentation", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if annotation is not None:
                print("in annot")
                annotation = annotation.text
                html_code.append(f"<label>{annotation}</label>")

            simple_content = complex_type.find("xsd:simpleContent", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if simple_content is not None:
                print("in simple")
                extension = simple_content.find("xsd:extension", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                base_type = extension.get("base", "")
                if base_type.startswith("dac6:"):
                    base_type = base_type.split(':')[-1]
                attributes = extension.findall("xsd:attribute", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                if len(attributes) > 0:
                    for attribute in attributes:
                        annotation = attribute.find("xsd:annotation/xsd:documentation", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                        if annotation is not None:
                            annotation = annotation.text
                        else:
                            annotation = ""
                        process_element(attribute, path, annotation, is_attribute=True)
                process_element(etree.Element("element", name=name, type=base_type), path)

            complex_content = complex_type.find("xsd:complexContent", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if complex_content is not None:
                print("in complex content")
                extension = complex_content.find("xsd:extension", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                base_type = extension.get("base", "")
                if base_type.startswith("dac6:"):
                    base_type = base_type.split(':')[-1]
                attributes = extension.findall("xsd:attribute", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                if len(attributes) > 0:
                    for attribute in attributes:
                        annotation = attribute.find("xsd:annotation/xsd:documentation", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                        if annotation is not None:
                            annotation = annotation.text
                        else:
                            annotation = ""
                        process_element(attribute, path, annotation, is_attribute=True)
                print("'name"*100, name)
                process_element(etree.Element("element", name=name, type=base_type), path)

            choice = complex_type.find("xsd:choice", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

            if choice is not None:
                print("choice")
                select_name = f"{input_name}_choice"
                html_code.append(f'<label>{name}: <select name="{select_name}" onchange="handleChoiceChange(this, \'{input_name}\')">')
                html_code.append('<option value="">Sélectionner une option</option>')
                for child in choice.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                    child_name = child.get("name")
                    html_code.append(f'<option value="{child_name}">{child_name}</option>')
                html_code.append('</select></label><br>')
                for child in choice.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                    child_name = child.get("name")
                    print("choice child name", child_name)
                    html_code.append(f'<div id="{input_name}_{child_name}_container" style="display:none;">')
                    process_element(child, input_name)
                    html_code.append('</div>')

            sequence = complex_type.find("xsd:sequence", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if sequence is not None:
                print("in sequence")
                choice = sequence.find("xsd:choice", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
                if choice is not None:
                    print("choice")
                    select_name = f"{input_name}_choice"
                    html_code.append(f'<label>{name}: <select name="{select_name}" onchange="handleChoiceChange(this, \'{input_name}\')">')
                    html_code.append('<option value="">Sélectionner une option </option>')
                    for child in choice.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                        child_name = child.get("name")
                        html_code.append(f'<option value="{child_name}">{child_name}</option>')
                    html_code.append('</select></label><br>')
                    for child in choice.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                        child_name = child.get("name")
                        print("choice child name", child_name)
                        html_code.append(f'<div id="{input_name}_{child_name}_container" style="display:none;">')
                        process_element(child, input_name)
                        html_code.append('</div>')
                else:
                    for child in sequence.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                        process_element(child, input_name)

            html_code.append("</fieldset>")

        simple_type = root.find(f".//xsd:simpleType[@name='{type_ref}']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

        if simple_type is None:
            simple_type = element.find(f"xsd:simpleType", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

        if simple_type is not None:
            print("in simple type")
            annotation = simple_type.find("xsd:annotation/xsd:documentation", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            if annotation is not None:
                print("in annot")
                annotation = annotation.text
                print(annotation)
                html_code.append(f"<label>{annotation}</label>")

            restriction = simple_type.find("xsd:restriction", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})
            base_type = restriction.get("base")

            if restriction is not None:

                enumeration = restriction.findall("xsd:enumeration", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

                if enumeration:
                    print("in enumeration simple")
                    html_code.append(f'<label>{name}: <select name="{input_name}">')
                    html_code.append("<option value="">Sélectionner une option</option>")
                    for child in enumeration:
                        child_value = child.get("value")
                        print(child_value)
                        value = child.find("xsd:annotation/xsd:documentation", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

                        if value is not None:
                            value = value.text
                        else:
                            value = child_value

                        html_code.append(f'<option value="{child_value}">{child_value}: {value}</option>')
                    html_code.append('</select></label>')

                else:
                    if base_type == "xsd:string":
                        html_code.append(f'<label>{name}: <input type="text" name="{input_name}" required></label><br>')
                    elif base_type == "xsd:integer":
                        html_code.append(f'<label>{name}: <input type="number" name="{input_name}"></label><br>')
                    elif base_type == "xsd:boolean":
                        html_code.append(f'<label>{name}: <input type="checkbox" name="{input_name}"></label><br>')
                    elif base_type == "xsd:date":
                        html_code.append(f'<label>{name}: <input type="date" name="{input_name}"></label><br>')
                    elif base_type == "xsd:dateTime":
                        html_code.append(f'<label>{name}: <input type="datetime-local" name="{input_name}"></label><br>')
                    else:
                        process_element(etree.Element("element", name=name, type=base_type), path)

    top_element = root.find(".//xsd:element[@name='DAC6Dispositif']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

    if top_element is not None:
        process_element(top_element)

    html_code.insert(0, "<form id='dac6-form'>")
    html_code.append("<button type='submit'>Soumettre</button>")
    html_code.append("</form>")

    html_code.append("""<script>
    function handleChoiceChange(select, baseId) {
          const options = select.options;
          for (let i = 1; i < options.length; i++) {
            const childId = `${baseId}_${options[i].value}_container`;
            const element = document.getElementById(childId);
            if (element) {
              element.style.display = options[i].value === select.value ? "block" : "none";
            }
  }}
  
  function addElement(baseId, name) {
  
  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\\]/g, '\\\$&'); // Échappe tous les caractères spéciaux
    }
  
  const container = document.getElementById(`${baseId}[${name}_template]_container`);
  if (!container) {
    console.error(`Container with ID ${baseId}[${name}_template]_container not found.`);
    return;
  }
  
  const escaped = escapeRegex(`${baseId}[${name}`);
  const regex = new RegExp(`^${escaped}_item_\\\d+\\\]_container$`);
  const existingElements = Array.from(document.querySelectorAll('[id]')).filter(el => regex.test(el.id));
  
  const newIndex = existingElements.length;
  const templateId = `${baseId}[${name}_template]_container`;
  const template = document.getElementById(templateId);
  
  if (template) {
    const clone = template.cloneNode(true);
    clone.id = `${baseId}[${name}_item_${newIndex}]_container`;
    clone.style.display = "block";

    // Mettre à jour les attributs "name" des champs clonés
    const inputsName = clone.querySelectorAll("[name]");
    inputsName.forEach(input => {
      const originalName = input.name;
      input.name = originalName.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
    });
    
    const inputsId = clone.querySelectorAll("[id]");
    inputsId.forEach(input => {
      const originalName = input.id;
      input.id = originalName.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
    });

    // Trouver le dernier sibling pour insérer après
    // const lastSibling = existingElements[existingElements.length - 1] || container;
    
    const selectsOnChange = clone.querySelectorAll('select[name$="_choice"]');
    
    // Obtenir et modifier un paramètre spécifique
    selectsOnChange.forEach(select => {
        let currentOnChange = select.getAttribute('onchange');
        currentOnChange = currentOnChange.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
        select.setAttribute('onchange', currentOnChange);
    });
    
    const selectsOnClick = clone.querySelectorAll('button');
    
    // Obtenir et modifier un paramètre spécifique
    selectsOnClick.forEach(select => {
        let currentOnChange = select.getAttribute('onclick');
        currentOnChange = currentOnChange.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
        select.setAttribute('onclick', currentOnChange);
    });

    console.log(clone);
    
    container.insertAdjacentElement('afterend', clone);
  } else {
    console.error(`Template with ID ${templateId} not found.`);
  }
}

</script>""")

    return "\n".join(html_code)

# Exemple d'utilisation
xsd_file = '/Users/antoine/Documents/IT/dac6/data/Dac6XML_FR_V.4.04.xsd'
html_output = generate_html_from_xsd(xsd_file)

# Sauvegarde dans un fichier HTML
output_file = 'output.html'
with open(output_file, 'w') as f:
    f.write(html_output)

print(f"Formulaire généré et enregistré dans {output_file}")
