// Fonction modifiée pour extraire les données des attributs
function extractData(form) {
    const data = {};

    function parseElement(element, parent) {
        const name = element.getAttribute("name");
        if (!name) return;

        const isAttribute = name.includes("__attribute__");
        const path = name.split('[').map(p => p.replace(']', ''));

        let current = parent;
        let currentParent = null;
        let currentKey = null;

        for (let i = 0; i < path.length; i++) {
            currentKey = path[i].replace("__attribute__", "");

            if (i === path.length - 1) {
                // Dernier niveau
                if (isAttribute) {
                    if (!current.attributes) {
                        current.attributes = {};
                    }
                    current.attributes[currentKey] = element.value;
                } else {
                    current[currentKey] = element.type === "checkbox" ? element.checked : element.value;
                }
            } else {
                // Niveaux intermédiaires
                if (!current[currentKey]) {
                    current[currentKey] = { attributes: {}, children: {} };
                }
                currentParent = current[currentKey];
                current = current[currentKey].children;
            }
        }
    }

    form.querySelectorAll("[name]").forEach(el => parseElement(el, data));
    return data;
}

// Fonction modifiée pour inclure les attributs lors de la génération du XML
function generateXML(parent, data, doc) {
    for (let key in data) {
        const cleanKey = key.replace(/_item_\d+$/, "");
        const elementData = data[key];

        // Ne pas dupliquer les balises : ignorer si c'est un attribut seul
        if (Object.keys(elementData).length === 1 && elementData.attributes) {
            continue;
        }

        // Créer un élément XML
        const child = doc.createElement(cleanKey);

        // Ajouter les attributs, s'ils existent
        if (elementData.attributes) {
            for (let attrName in elementData.attributes) {
                child.setAttribute(attrName, elementData.attributes[attrName]);
            }
        }

        // Ajouter les enfants récursivement
        if (elementData.children) {
            generateXML(child, elementData.children, doc);
        } else if (typeof elementData === "string" || typeof elementData === "boolean") {
            child.textContent = elementData;
        }

        parent.appendChild(child);
    }
}

// Exemple de fonction pour générer le XML
function genererXML() {
    const form = document.querySelector("#dac6-form");
    const formData = extractData(form);
    const doc = document.implementation.createDocument("", "DAC6Dispositif", null);

    generateXML(doc.documentElement, formData, doc);

    const xmlString = new XMLSerializer().serializeToString(doc);
    console.log(xmlString);
    alert("XML généré! Consultez la console du navigateur.");
}
