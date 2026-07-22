# DIADEM-ontology
Ontology  describing the PEPR DIADEM and all associated projects

## Folder project's information
In the yaml_templates_projects folder 


## Visualization
https://cnherrera.github.io/DIADEM-ontology/onto-viewer.html


# PEPR DIADEM Ontology & Knowledge Graph - preparation

PEPR DIADEM ontology and Knowledge Graph generation repository.

This repository centralizes the ontological models and structured data required to build the unified Knowledge Graph for the ecosystem.

---

## Overview

The main objective of this project is to consolidate data from all DIADEM projects into a single knowledge network. 

To ensure your project's data is correctly integrated into the Knowledge Graph, each team's project  must complete a standardized YAML configuration file containing their project's metadata and specifications.

---

## Repository Structure

Downl
```text
.
├── yaml_templates_projects/   # Project YAML templates folder
│   ├── project_<your_project>.yaml  # Base template to fill out
│   ├── list_keywords.yaml     # Reference list of valid keywords & competencies
│   └── README.md              # Guidelines to fill YAML files
├── proj-ontology.ttl          # Main OWL/RDF ontology definitions
└── README.md                  # Main documentation


