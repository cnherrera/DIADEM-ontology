from rdflib import Graph, Namespace, RDF
import csv

# 1. Definir los Namespaces según tu estructura
DIAM = Namespace("https://raw.githubusercontent.com/cnherrera/DIAMOND_ontology/refs/heads/main/diamond_project_ontology.ttl") # Cambia esto por la URI real si la tienes
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def extraer_info(ttl_file, output_csv):
    g = Graph()
    g.parse(ttl_file, format="turtle")

    # Abrir CSV para escribir
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "URI", "GivenName", "FamilyName", "FullName", "Mbox", 
            "EmployedBy", "WorksOn", "PersonnelType", "Competence", 
            "JoinDate", "LeftDate", "SeeAlso", "IsCurrentMember"
        ])

        # Buscar todas las personas
        for s in g.subjects(RDF.type, DIAM.Person):
            
            # Función auxiliar para obtener valores únicos o múltiples
            def get_val(pred):
                # Retorna el objeto (o una lista unida por | si hay varios)
                objs = list(g.objects(s, pred))
                if not objs: return ""
                return " | ".join([str(o) for o in objs])

            # Extracción
            fila = [
                str(s),
                str(g.value(s, FOAF.givenName, default="")),
                str(g.value(s, FOAF.familyName, default="")),
                str(g.value(s, FOAF.name, default="")),
                str(g.value(s, FOAF.mbox, default="")),
                str(g.value(s, DIAM.employedBy, default="")),
                get_val(DIAM.worksOn),        # Puede haber varios
                str(g.value(s, DIAM.hasPersonnelType, default="")),
                get_val(DIAM.hasCompetence),  # Puede haber varios
                str(g.value(s, DIAM.joinDate, default="")),
                str(g.value(s, DIAM.leftDate, default="")),
                get_val(RDFS.seeAlso),        # Puede haber varios
                str(g.value(s, DIAM.isCurrentMember, default=""))
            ]
            
            writer.writerow(fila)

    print(f"Éxito. Datos guardados en: {output_csv}")

# Ejecución
extraer_info("projects/diamond_instances.ttl", "personas_extraidas.csv")
