#!/usr/bin/env python3
"""
yaml_to_ttl.py
==============
Converts PEPR YAML description files into RDF/Turtle instance files
using the proj ontology.

Usage
-----
  # Convert a single project:
  python yaml_to_ttl.py --project projects/MYPROJECT.yaml

  # Assemble the full program graph (program + all projects):
  python yaml_to_ttl.py --program program.yaml --projects-dir projects/

  # Validate after conversion (requires pyshacl):
  python yaml_to_ttl.py --program program.yaml --projects-dir projects/ --validate

Requirements
------------
  pip install rdflib pyyaml pyshacl
"""

import argparse
import re
import sys
from pathlib import Path

import yaml
from rdflib import Graph, Literal, Namespace, RDF, OWL, XSD, URIRef
from rdflib.namespace import RDFS

# ── Namespaces ───────────────────────────────────────────────────────────────

INST = Namespace("https://cnherrera.github.io/DIADEM-ontology/PEPR-DIADEM_instances.ttl#")
PROJ = Namespace("https://cnherrera.github.io/DIADEM-ontology/pepr-ontology.ttl#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
SCHEMA = Namespace("https://www.schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")   

# ── Helpers ──────────────────────────────────────────────────────────────────

def slug(text: str) -> str:
    """Turn a string into a safe RDF local name."""
    s = str(text).strip()
    s = re.sub(r"[^\w\-]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def uri(local: str) -> URIRef:
    return INST[local]


def date_lit(val) -> Literal:
    return Literal(str(val), datatype=XSD.date)


def str_lit(val) -> Literal:
    return Literal(str(val), datatype=XSD.string)


def int_lit(val) -> Literal:
    return Literal(int(val), datatype=XSD.integer)


def decimal_lit(val) -> Literal:
    return Literal(float(val), datatype=XSD.decimal)


def uri_lit(val) -> Literal:
    return Literal(str(val), datatype=XSD.anyURI)


# ── Person / Organisation helpers ─────────────────────────────────────────────

def add_person(g: Graph, d: dict) -> URIRef:
    """Add a proj:Person node and return its URI (idempotent on orcid/name)."""
    first = d.get("first_name", "Unknown")
    last  = d.get("last_name",  "Unknown")
    orcid = d.get("orcid")

    node_id = slug(f"{first}_{last}")
    person_uri = uri(f"person/{node_id}")

    g.add((person_uri, RDF.type, PROJ.Person))
    g.add((person_uri, PROJ.firstName, str_lit(first)))
    g.add((person_uri, PROJ.lastName,  str_lit(last)))

    if d.get("email"):
        g.add((person_uri, PROJ.email, str_lit(d["email"])))
    if orcid:
        g.add((person_uri, PROJ.orcid, uri_lit(orcid)))

    # competences
    for comp in d.get("competences", []) or []:
        comp_id = slug(f"{node_id}_{comp.get('domain', 'unknown')}")
        comp_uri = uri(f"competence/{comp_id}")
        g.add((comp_uri, RDF.type, PROJ.Competence))
        if comp.get("domain"):
            g.add((comp_uri, PROJ.competenceDomain, str_lit(comp["domain"])))
        if comp.get("level"):
            g.add((comp_uri, PROJ.competenceLevel, str_lit(comp["level"])))
        g.add((person_uri, PROJ.hasCompetence, comp_uri))

    return person_uri


def add_org(g: Graph, d: dict) -> URIRef:
    """Add a proj:Organization node and return its URI (idempotent on acronym)."""
    acronym = d.get("acronym", "ORG")
    org_uri = uri(f"org/{slug(acronym)}")

    g.add((org_uri, RDF.type, PROJ.Organization))
    g.add((org_uri, PROJ.acronym, str_lit(acronym)))
    if d.get("full_name"):
        g.add((org_uri, RDFS.label, str_lit(d["full_name"])))
    if d.get("ror"):
        g.add((org_uri, PROJ.rorID, uri_lit(d["ror"])))

    return org_uri


def add_lead_colead(g: Graph, subject: URIRef, block: dict | None, is_lead: bool):
    """Attach lead/colead person+institution triples."""
    if not block:
        return
    if block.get("person"):
        p_uri = add_person(g, block["person"])
        prop  = PROJ.hasLeadPerson if is_lead else PROJ.hasCoLeadPerson
        g.add((subject, prop, p_uri))
    if block.get("institution"):
        o_uri = add_org(g, block["institution"])
        prop  = PROJ.hasLeadInstitution if is_lead else PROJ.hasCoLeadInstitution
        g.add((subject, prop, o_uri))


# ── Work Package builder ──────────────────────────────────────────────────────

def add_work_package(g: Graph, project_uri: URIRef, wp_data: dict, project_slug: str) -> URIRef:
    num    = wp_data["number"]
    wp_slug = slug(f"{project_slug}_WP{num}")
    wp_uri  = uri(f"wp/{wp_slug}")

    g.add((wp_uri, RDF.type, PROJ.WorkPackage))
    g.add((wp_uri, PROJ.wpNumber, int_lit(num)))
    if wp_data.get("title"):
        g.add((wp_uri, RDFS.label, str_lit(wp_data["title"])))
    if wp_data.get("description"):
        g.add((wp_uri, PROJ.description, str_lit(wp_data["description"])))

    # lead institution
    if wp_data.get("lead_institution"):
        lead_inst_uri = uri(f"org/{slug(wp_data['lead_institution'])}")
        g.add((wp_uri, PROJ.hasLeadOrganization, lead_inst_uri))

    # deliverables
    for d in wp_data.get("deliverables", []) or []:
        d_id  = slug(f"{wp_slug}_{d['id']}")
        d_uri = uri(f"deliverable/{d_id}")
        g.add((d_uri, RDF.type, PROJ.Deliverable))
        g.add((d_uri, PROJ.identifier, str_lit(d["id"])))
        if d.get("title"):
            g.add((d_uri, RDFS.label, str_lit(d["title"])))
        if d.get("description"):
            g.add((d_uri, PROJ.description, str_lit(d["description"])))
        if d.get("due_date"):
            g.add((d_uri, PROJ.dueDate, date_lit(d["due_date"])))
        if d.get("type"):
            g.add((d_uri, PROJ.deliverableType, str_lit(d["type"])))
        g.add((wp_uri, PROJ.hasDeliverable, d_uri))

    # tasks
    for t in wp_data.get("tasks", []) or []:
        t_id  = slug(f"{wp_slug}_{t['id']}")
        t_uri = uri(f"task/{t_id}")
        g.add((t_uri, RDF.type, PROJ.Task))
        g.add((t_uri, PROJ.identifier, str_lit(t["id"])))
        if t.get("title"):
            g.add((t_uri, RDFS.label, str_lit(t["title"])))
        if t.get("description"):
            g.add((t_uri, PROJ.description, str_lit(t["description"])))
        g.add((wp_uri, PROJ.hasTask, t_uri))

    # tools
    for tool in wp_data.get("tools", []) or []:
        tool_uri = uri(f"tool/{slug(tool.get('acronym', tool.get('full_name', 'TOOL')))}")
        g.add((tool_uri, RDF.type, PROJ.Tool))
        if tool.get("acronym"):
            g.add((tool_uri, PROJ.acronym, str_lit(tool["acronym"])))
        if tool.get("full_name"):
            g.add((tool_uri, RDFS.label, str_lit(tool["full_name"])))
        if tool.get("url"):
            g.add((tool_uri, PROJ.documentationURL, uri_lit(tool["url"])))
        g.add((wp_uri, PROJ.usesTool, tool_uri))

    # products
    for prod in wp_data.get("products", []) or []:
        prod_uri = uri(f"product/{slug(prod.get('acronym', prod.get('full_name', 'PROD')))}")
        g.add((prod_uri, RDF.type, PROJ.Product))
        if prod.get("acronym"):
            g.add((prod_uri, PROJ.acronym, str_lit(prod["acronym"])))
        if prod.get("full_name"):
            g.add((prod_uri, RDFS.label, str_lit(prod["full_name"])))
        if prod.get("description"):
            g.add((prod_uri, PROJ.description, str_lit(prod["description"])))
        if prod.get("url"):
            g.add((prod_uri, PROJ.documentationURL, uri_lit(prod["url"])))
        g.add((wp_uri, PROJ.producesProduct, prod_uri))

    # contributors
    for person_d in wp_data.get("contributors", []) or []:
        p_uri = add_person(g, person_d)
        g.add((wp_uri, PROJ.hasContributor, p_uri))

    g.add((project_uri, PROJ.hasWorkPackage, wp_uri))
    return wp_uri


# ── Project builder ───────────────────────────────────────────────────────────

def build_project_graph(data: dict) -> tuple[Graph, str]:
    """Build an RDF graph for one project YAML file. Returns (graph, acronym)."""
    g = _new_graph()
    
    # Agregar la declaración de ontología del instancia al inicio
    instances_ontology_uri = URIRef("https://cnherrera.github.io/DIADEM-ontology/PEPR-DIADEM_instances.ttl#")
    proj_ontology_uri = URIRef("https://cnherrera.github.io/DIADEM-ontology/pepr-ontology.ttl#")

    g.add((instances_ontology_uri, RDF.type, OWL.Ontology))
    g.add((instances_ontology_uri, OWL.imports, proj_ontology_uri))
#    g.add((instances_ontology_uri, OWL.imports, PROJ))
    g.add((instances_ontology_uri, RDFS.label, Literal("PEPR DIADEM Instances – People, Institutions, Projects, and Platforms", lang="en")))
    g.add((instances_ontology_uri, RDFS.label, Literal("Instances du projet PEPR DIADEM – Personnes, institutions, projets et plateformes", lang="fr")))
    g.add((instances_ontology_uri, DC.description, Literal(
        "Instances for the PEPR DIADEM project, encompassing people and institutions involved in the project, as well as associated projects and platforms.",
        lang="en"
    )))
    g.add((instances_ontology_uri, DC.description, Literal(
        "Instances pour le projet PEPR DIADEM, englobant les personnes et les institutions impliquées dans le projet, ainsi que les projets et plateformes associés.",
        lang="fr"
    )))
    g.add((instances_ontology_uri, OWL.versionInfo, Literal("1.0")))
    
    p = data["project"]
    acronym = p["acronym"]
    ps = slug(acronym)

    ptype   = PROJ.TargetedProject if p.get("type", "targeted") == "targeted" else PROJ.AAPProject
    proj_uri = uri(f"project/{ps}")

    g.add((proj_uri, RDF.type, ptype))
    g.add((proj_uri, PROJ.acronym, str_lit(acronym)))
    if p.get("title"):
        g.add((proj_uri, RDFS.label, str_lit(p["title"])))
    if p.get("description"):
        g.add((proj_uri, PROJ.description, str_lit(p["description"])))
    if p.get("start_date"):
        g.add((proj_uri, PROJ.startDate, date_lit(p["start_date"])))
    if p.get("end_date"):
        g.add((proj_uri, PROJ.endDate, date_lit(p["end_date"])))
    if p.get("documentation_url"):
        g.add((proj_uri, PROJ.documentationURL, uri_lit(p["documentation_url"])))

    add_lead_colead(g, proj_uri, p.get("lead"),   is_lead=True)
    add_lead_colead(g, proj_uri, p.get("colead"), is_lead=False)

    for org_d in p.get("organizations", []) or []:
        o_uri = add_org(g, org_d)
        g.add((proj_uri, PROJ.hasOrganization, o_uri))

    for wp_d in p.get("work_packages", []) or []:
        add_work_package(g, proj_uri, wp_d, ps)

    return g, acronym


# ── Program builder ─────────────────────────────────────────────────────────

def build_program_graph(data: dict, project_graphs: dict[str, Graph]) -> Graph:
    """Build the full program graph, merging all project graphs."""
    g = _new_graph()
    pr = data["program"]
    acronym = pr["acronym"]
    prog_uri = uri(f"program/{slug(acronym)}")
    proj_ontology_uri = URIRef("https://cnherrera.github.io/DIADEM-ontology/pepr-ontology.ttl#")
    
    # Agregar la declaración de ontología del instancia al inicio
    instances_ontology_uri = URIRef("https://cnherrera.github.io/DIADEM-ontology/PEPR-DIADEM_instances.ttl#")
    g.add((instances_ontology_uri, RDF.type, OWL.Ontology))
    #g.add((instances_ontology_uri, OWL.imports, PROJ))
    g.add((instances_ontology_uri, OWL.imports, proj_ontology_uri))
    g.add((instances_ontology_uri, RDFS.label, Literal("PEPR DIADEM Instances – People, Institutions, Projects, and Platforms", lang="en")))
    g.add((instances_ontology_uri, RDFS.label, Literal("Instances du projet PEPR DIADEM – Personnes, institutions, projets et plateformes", lang="fr")))
    g.add((instances_ontology_uri, DC.description, Literal(
        "Instances for the PEPR DIADEM project, encompassing people and institutions involved in the project, as well as associated projects and platforms.",
        lang="en"
    )))
    g.add((instances_ontology_uri, DC.description, Literal(
        "Instances pour le projet PEPR DIADEM, englobant les personnes et les institutions impliquées dans le projet, ainsi que les projets et plateformes associés.",
        lang="fr"
    )))
    g.add((instances_ontology_uri, OWL.versionInfo, Literal("1.0")))

    g.add((prog_uri, RDF.type, PROJ.Program))
    g.add((prog_uri, PROJ.acronym,      str_lit(acronym)))
    if pr.get("title"):
        g.add((prog_uri, RDFS.label,    str_lit(pr["title"])))
    if pr.get("description"):
        g.add((prog_uri, PROJ.description, str_lit(pr["description"])))
    if pr.get("start_date"):
        g.add((prog_uri, PROJ.startDate,  date_lit(pr["start_date"])))
    if pr.get("end_date"):
        g.add((prog_uri, PROJ.endDate,    date_lit(pr["end_date"])))
    if pr.get("documentation_url"):
        g.add((prog_uri, PROJ.documentationURL, uri_lit(pr["documentation_url"])))

    # Funding
    if pr.get("funding"):
        f = pr["funding"]
        fund_uri = uri(f"funding/{slug(acronym)}")
        g.add((fund_uri, RDF.type, PROJ.Funding))
        if f.get("source"):
            g.add((fund_uri, PROJ.fundingSource, str_lit(f["source"])))
        if f.get("amount"):
            g.add((fund_uri, PROJ.fundingAmount, decimal_lit(f["amount"])))
        if f.get("currency"):
            g.add((fund_uri, PROJ.fundingCurrency, str_lit(f["currency"])))
        g.add((prog_uri, PROJ.hasFunding, fund_uri))

    add_lead_colead(g, prog_uri, pr.get("lead"),   is_lead=True)
    add_lead_colead(g, prog_uri, pr.get("colead"), is_lead=False)

    # Merge project sub-graphs
    for pacr, pg in project_graphs.items():
        for triple in pg:
            g.add(triple)
        proj_uri_ref = uri(f"project/{slug(pacr)}")
        # link project to program based on type
        if (proj_uri_ref, RDF.type, PROJ.TargetedProject) in g:
            g.add((prog_uri, PROJ.hasTargetedProject, proj_uri_ref))
        else:
            g.add((prog_uri, PROJ.hasAAPProject, proj_uri_ref))

    # Platforms
    for plat in pr.get("platforms", []) or []:
        plat_slug = slug(plat["acronym"])
        plat_uri  = uri(f"platform/{plat_slug}")
        g.add((plat_uri, RDF.type, PROJ.Platform))
        g.add((plat_uri, PROJ.acronym, str_lit(plat["acronym"])))
        if plat.get("title"):
            g.add((plat_uri, RDFS.label, str_lit(plat["title"])))
        if plat.get("description"):
            g.add((plat_uri, PROJ.description, str_lit(plat["description"])))
        if plat.get("goal_description"):
            g.add((plat_uri, PROJ.goalDescription, str_lit(plat["goal_description"])))
        if plat.get("goal_category"):
            cat_map = {
                "scientific":     PROJ.ScientificGoal,
                "domain":         PROJ.DomainGoal,
                "infrastructure": PROJ.InfrastructureGoal,
                "other":          PROJ.OtherGoal,
            }
            cat_uri = cat_map.get(plat["goal_category"].lower(), PROJ.OtherGoal)
            g.add((plat_uri, PROJ.hasGoalCategory, cat_uri))
        for lp_acronym in plat.get("lead_projects", []) or []:
            lp_uri = uri(f"project/{slug(lp_acronym)}")
            g.add((plat_uri, PROJ.hasPlatformLeadProject, lp_uri))
            g.add((plat_uri, PROJ.hasPlatformProject, lp_uri))
        g.add((prog_uri, PROJ.hasPlatform, plat_uri))

    return g


# ── Graph factory ─────────────────────────────────────────────────────────────

def _new_graph() -> Graph:
    g = Graph()
    g.bind("proj",    PROJ)
    g.bind("inst",    INST)
    g.bind("rdf",     RDF)
    g.bind("rdfs",    RDFS)
    g.bind("xsd",     XSD)
    g.bind("owl",     OWL)
    g.bind("dc",      DC)
    g.bind("schema",  SCHEMA)
    g.bind("skos",    SKOS)
    return g


# ── Validation ────────────────────────────────────────────────────────────────

def validate(data_graph: Graph, shapes_path: Path) -> bool:
    try:
        from pyshacl import validate as shacl_validate
    except ImportError:
        print("⚠  pyshacl not installed – skipping validation.  pip install pyshacl")
        return True

    shapes_graph = Graph().parse(str(shapes_path), format="turtle")
    conforms, results_graph, results_text = shacl_validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
    )
    if conforms:
        print("✅  SHACL validation passed.")
    else:
        print("❌  SHACL validation FAILED:\n")
        print(results_text)
    return conforms


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert PEPR YAML description files to RDF/Turtle."
    )
    parser.add_argument("--project",      help="Path to a single project YAML file.")
    parser.add_argument("--program",    help="Path to the program YAML file.")
    parser.add_argument("--projects-dir", help="Directory containing project YAML files.")
    parser.add_argument("--output",       help="Output .ttl file (default: stdout or auto-named).")
    parser.add_argument("--shapes",       default="proj-shapes.ttl",
                        help="Path to SHACL shapes file (default: proj-shapes.ttl).")
    parser.add_argument("--validate",     action="store_true",
                        help="Run SHACL validation after conversion.")
    args = parser.parse_args()

    if args.project:
        # ── Single project mode ───────────────────────────────────────────
        data = yaml.safe_load(Path(args.project).read_text())
        g, acronym = build_project_graph(data)
        out_path = Path(args.output) if args.output else Path(f"{slug(acronym)}_instances_v2.ttl")
        g.serialize(destination=str(out_path), format="turtle")
        print(f"✔  Written {out_path}  ({len(g)} triples)")

        if args.validate:
            validate(g, Path(args.shapes))

    elif args.program:
        # ── Full program mode ───────────────────────────────────────────
        prog_data = yaml.safe_load(Path(args.program).read_text())

        project_graphs: dict[str, Graph] = {}
        projects_dir = Path(args.projects_dir) if args.projects_dir else None

        if projects_dir and projects_dir.is_dir():
            for yaml_file in sorted(projects_dir.glob("*.yaml")):
                try:
                    pdata = yaml.safe_load(yaml_file.read_text())
                    pg, pacr = build_project_graph(pdata)
                    project_graphs[pacr] = pg
                    print(f"  Loaded project: {pacr}  ({len(pg)} triples)")
                except Exception as exc:
                    print(f"  ⚠  Could not load {yaml_file}: {exc}", file=sys.stderr)

        g = build_program_graph(prog_data, project_graphs)
        out_path = Path(args.output) if args.output else Path(
            f"{slug(prog_data['program']['acronym'])}_instances_v2.ttl"
        )
        g.serialize(destination=str(out_path), format="turtle")
        print(f"✔  Written {out_path}  ({len(g)} triples)")

        if args.validate:
            validate(g, Path(args.shapes))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
