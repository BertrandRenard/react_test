from lxml import etree

html_code = []


def handle_node(name, input_name, type_ref, restriction="", annotation=""):

    #  handle restriction, handle attribute

    if type_ref == "xsd:string":
        html_code.append(f'<label>{name}{annotation}: <input type="text" name="{input_name}" {restriction}></label><br>')
    elif type_ref in ["xsd:integer", "xsd:long"]:
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

    def process_element(element, path="", annotation="", restriction="", is_attribute=False, is_template=False, nested=0):

        name = element.get("name")
        type_ref = element.get("type", "")

        min_occurs = element.get("minOccurs", "1")
        max_occurs = element.get("maxOccurs", "1")

        if min_occurs != "1" or max_occurs != "1":
            is_template = True
            print("maxxx", max_occurs)

        print(f"Processing element: name={name}, type_ref={type_ref}, path={path}, minOccurs={min_occurs} maxOccurs={max_occurs}")

        template_suffix = "_template" if is_template else ""

        if is_attribute:
            input_name = f"{path}[{name}{template_suffix}__is_attribute__]" if path else f"{name}{template_suffix}"
        else:
            input_name = f"{path}[{name}{template_suffix}]" if path else f"{name}{template_suffix}"

        if type_ref.startswith("dac6:"):
            type_ref = type_ref.split(':')[-1]

        if type_ref in ["xsd:string", "xsd:integer", "xsd:boolean", "xsd:date", "xsd:dateTime", "xsd:long"]:
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
                if max_occurs == "unbounded":
                    max_occurs = 1000
                html_code.append(f'<button type="button" minoccurs={min_occurs} maxoccurs={max_occurs} nested={nested} onclick="addElement(\'{path}\', \'{name}\', {max_occurs})">Ajouter un {name}</button>')
                html_code.append(f'<fieldset id="{input_name}_container" style="display:none;"><legend>{name}</legend>')
                html_code.append(f'<button type="button" onclick="deleteElement(this)">Supprimer</button>')
            else:
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
                        process_element(attribute, path, annotation, is_attribute=True, nested=nested+1)
                process_element(etree.Element("element", name=name, type=base_type), path, nested=nested+1)

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
                        process_element(attribute, path, annotation, is_attribute=True, nested=nested+1)
                process_element(etree.Element("element", name=name, type=base_type), path, nested=nested+1)

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
                    process_element(child, input_name, nested=nested+1)
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
                        process_element(child, input_name, nested=nested+1)
                        html_code.append('</div>')
                else:
                    for child in sequence.findall("xsd:element", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"}):
                        process_element(child, input_name, nested=nested+1)

            html_code.append("</fieldset>")

        simple_type = root.find(f".//xsd:simpleType[@name='{type_ref}']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

        if simple_type is None:
            simple_type = element.find(f"xsd:simpleType", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

        if simple_type is not None:

            if is_template:
                if max_occurs == "unbounded":
                    max_occurs = 1000
                html_code.append(f'<button type="button" minoccurs={min_occurs} maxoccurs={max_occurs} nested={nested} onclick="addElement(\'{path}\', \'{name}\', {max_occurs})">Ajouter un {name}</button>')
                html_code.append(f'<fieldset id="{input_name}_container" style="display:none;"><legend>{name}</legend>')
                html_code.append(f'<button type="button" onclick="deleteElement(this)">Supprimer</button>')
            else:
                html_code.append(f'<fieldset id="{input_name}_container"><legend>{name}</legend>')

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
                    elif base_type in ["xsd:integer", "xsd:long"]:
                        html_code.append(f'<label>{name}: <input type="number" name="{input_name}"></label><br>')
                    elif base_type == "xsd:boolean":
                        html_code.append(f'<label>{name}: <input type="checkbox" name="{input_name}"></label><br>')
                    elif base_type == "xsd:date":
                        html_code.append(f'<label>{name}: <input type="date" name="{input_name}"></label><br>')
                    elif base_type == "xsd:dateTime":
                        html_code.append(f'<label>{name}: <input type="datetime-local" name="{input_name}"></label><br>')
                    else:
                        process_element(etree.Element("element", name=name, type=base_type), path, nested=nested+1)
            html_code.append("</fieldset>")

    top_element = root.find(".//xsd:element[@name='DAC6Dispositif']", namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"})

    if top_element is not None:
        process_element(top_element)

    html_code.insert(0, "<form id='dac6-form'>")
    html_code.append("<button type='submit'>Soumettre</button>")
    html_code.append('<button type="button" onclick="genererXML()">Générer XML</button>')
    html_code.append("</form>")

    html_code.append("""<script>
    
    const countObject = {}
    
    function handleChoiceChange(select, baseId) {
          const options = select.options;
          for (let i = 1; i < options.length; i++) {
            const childId = `${baseId}_${options[i].value}_container`;
            const element = document.getElementById(childId);
            if (element) {
              element.style.display = options[i].value === select.value ? "block" : "none";
            }
  }}
  
  function deleteElement(component){
    const parent = component.parentElement; // Récupérer le parent direct
    parent.remove();
  }
  
  function addElement(baseId, name, maxNb) {
  
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
  
  // const nbElement = existingElements.length;
  
  // console.log(maxNb);
  
  const templateId = `${baseId}[${name}_template]_container`;
  const template = document.getElementById(templateId);
  
  if (templateId in countObject) {
    countObject[templateId]++;
    } else {
        countObject[templateId] = 1;
    }
    
  const newIndex = countObject[templateId]
  
  if (template) {
    const clone = template.cloneNode(true);
    clone.id = `${baseId}[${name}_item_${newIndex}]_container`;
    clone.style.display = "block";

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
    
    const selectsOnChange = clone.querySelectorAll('select[name$="_choice"]');
    
    selectsOnChange.forEach(select => {
        let currentOnChange = select.getAttribute('onchange');
        currentOnChange = currentOnChange.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
        select.setAttribute('onchange', currentOnChange);
    });
    
    const selectsOnClick = clone.querySelectorAll('button');
    
    selectsOnClick.forEach(select => {
        let currentOnChange = select.getAttribute('onclick');
        currentOnChange = currentOnChange.replace(`${baseId}[${name}_template]`, `${baseId}[${name}_item_${newIndex}]`);
        select.setAttribute('onclick', currentOnChange);
    });
    
    const lastSibling = existingElements[existingElements.length - 1] || container;
    
    lastSibling.insertAdjacentElement('afterend', clone);
  } else {
    console.error(`Template with ID ${templateId} not found.`);
  }
}


function extractData(form) {
    const data = {};
    function parseElement(element, parent) {
        const name = element.getAttribute("name");
        if (!name) return;
        const path = name.split('[').map(p => p.replace(']', ''));
        let current = parent;
        for (let i = 0; i < path.length - 1; i++) {
            if (!current[path[i]]) {
                current[path[i]] = {};
            }
            current = current[path[i]];
        }
        current[path[path.length - 1]] = element.type === "checkbox" ? element.checked : element.value;
    }
    form.querySelectorAll("[name]").forEach(el => parseElement(el, data));
    return data;
}

function generateXML(parent, data, doc) {
    for (let key in data) {
        const cleanKey = key.replace(/_item_\d+$/, "");
        const child = doc.createElement(cleanKey);
        if (typeof data[key] === "object" && data[key] !== null) {
            generateXML(child, data[key], doc);
        } else {
            child.textContent = data[key];
        }
        parent.appendChild(child);
    }
}

function genererXML() {

    const form = document.querySelector("#dac6-form");
    const formData = extractData(form);
    const doc = document.implementation.createDocument("", "DAC6Dispositif", null);

    generateXML(doc.documentElement, formData, doc);

    const xmlString = new XMLSerializer().serializeToString(doc);
    console.log(xmlString);
    alert("XML généré! Consultez la console du navigateur.");
    
}


document.addEventListener('DOMContentLoaded', () => {

    const buttons = document.querySelectorAll('button[nested]');
    const maxNested = Array.from(buttons).map(button => parseInt(button.getAttribute('nested'), 10));
    const maxValueNested = Math.max(...maxNested);
        
    for (let i = maxValueNested; i >= 0; i--) {
        
        const buttons = document.querySelectorAll(`button[nested="${i}"][minOccurs]:not([minOccurs="0"])`);
        
        buttons.forEach(button => {
            button.click();
        });
    
}


});


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
