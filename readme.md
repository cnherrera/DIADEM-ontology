# PEPR Knowledge Graph Infrastructure

An ontology-based collaborative infrastructure for describing a French PEPR programme,
its projects, platforms, work packages, people and competences.

---

## Repository layout

```
pepr-kg/
│
├── ontology/
│   ├── proj-ontology.ttl       # OWL ontology  (base prefix: proj)
│   └── proj-shapes.ttl         # SHACL validation shapes
│
├── data/
│   ├── programme.yaml          # ONE file – describes the whole PEPR
│   └── projects/
│       ├── MYPROJECT.yaml      # one file per project (targeted or AAP)
│       ├── ANOTHERPROJ.yaml
│       └── ...
│
├── templates/
│   └── project_template.yaml   # copy this when adding a new project
│
├── scripts/
│   └── yaml_to_ttl.py          # Python converter + validator
│
├── output/                     # generated – do not edit manually
│   ├── MYPROJECT_instances.ttl
│   └── PEPR-EXAMPLE_instances.ttl   # merged programme graph
│
└── README.md
```

---

## Quick start

### 1 — Install dependencies

```bash
pip install rdflib pyyaml pyshacl
```

### 2 — Add a new project

```bash
cp templates/project_template.yaml data/projects/MYPROJECT.yaml
# edit with your project details
```

### 3 — Convert a single project to Turtle

```bash
python scripts/yaml_to_ttl.py \
    --project data/projects/MYPROJECT.yaml \
    --output  output/MYPROJECT_instances.ttl
```

### 4 — Build the full programme graph (all projects merged)

```bash
python scripts/yaml_to_ttl.py \
    --programme   data/programme.yaml \
    --projects-dir data/projects/ \
    --output      output/PEPR-EXAMPLE_instances.ttl
```

### 5 — Validate with SHACL

```bash
python scripts/yaml_to_ttl.py \
    --programme   data/programme.yaml \
    --projects-dir data/projects/ \
    --validate \
    --shapes   ontology/proj-shapes.ttl
```

---

## Collaboration workflow (Git-based)

Each project team works on **their own YAML file** only.

```
main branch
│
└── projects/
    ├── PROJ_A.yaml   ← maintained by Project A team
    ├── PROJ_B.yaml   ← maintained by Project B team
    └── ...
```

Suggested Git workflow:

1. Fork / clone the repository.
2. Copy `templates/project_template.yaml` → `data/projects/<ACRONYM>.yaml`.
3. Fill the template (see field descriptions below).
4. Run `yaml_to_ttl.py --project …` locally to check for conversion errors.
5. If `pyshacl` is available, run with `--validate` to catch missing required fields.
6. Open a Pull Request.  CI (GitHub Actions) can run validation automatically.

---

## YAML field reference

### `programme.yaml`

| Field | Required | Description |
|-------|----------|-------------|
| `programme.acronym` | ✅ | Short identifier, used as RDF local name |
| `programme.title` | ✅ | Full title |
| `programme.description` | ✅ | Free text |
| `programme.start_date` | ✅ | ISO 8601 date `YYYY-MM-DD` |
| `programme.end_date` | ✅ | ISO 8601 date |
| `programme.documentation_url` | | Programme website |
| `programme.funding.source` | | Funding body (e.g. "ANR / France 2030") |
| `programme.funding.amount` | | Total budget (number) |
| `programme.funding.currency` | | Currency code, e.g. "EUR" |
| `programme.lead` | ✅ | `person` + `institution` sub-blocks |
| `programme.colead` | | Optional |
| `programme.platforms` | | List of platform descriptions |
| `programme.targeted_projects` | | List of project acronyms |
| `programme.aap_projects` | | List of AAP project acronyms |

### `projects/<ACRONYM>.yaml`

| Field | Required | Description |
|-------|----------|-------------|
| `project.type` | ✅ | `targeted` or `aap` |
| `project.acronym` | ✅ | Must be unique across the PEPR |
| `project.title` | ✅ | Full project title |
| `project.description` | ✅ | Scientific description |
| `project.start_date` | ✅ | `YYYY-MM-DD` |
| `project.end_date` | ✅ | `YYYY-MM-DD` |
| `project.documentation_url` | | Project website |
| `project.lead.person` | ✅ | `first_name`, `last_name`, `email`, `orcid` |
| `project.lead.institution` | ✅ | `acronym`, `full_name`, `ror` |
| `project.colead` | | Optional, same structure as `lead` |
| `project.organizations` | ✅ | List of partner organizations |
| `project.work_packages` | | List of WP blocks |

### Work Package sub-block

| Field | Required | Description |
|-------|----------|-------------|
| `number` | ✅ | Integer WP number |
| `title` | ✅ | Short title |
| `description` | ✅ | Free text |
| `lead_institution` | ✅ | Must match an `acronym` in `organizations` |
| `deliverables` | | List: `id`, `title`, `description`, `due_date`, `type` |
| `tasks` | | List: `id`, `title`, `description` |
| `tools` | | List: `acronym`, `full_name`, `url` |
| `products` | | List: `acronym`, `full_name`, `description`, `url` |
| `contributors` | | List of persons; each can have `competences` list |

### Competence sub-block (within a contributor)

```yaml
competences:
  - domain: "Machine learning"
    level:  "expert"          # beginner / intermediate / expert
  - domain: "Data engineering"
    level:  "intermediate"
```

---

## Ontology summary

**Base prefix:** `proj:  <https://w3id.org/pepr/ontology/proj#>`

Key classes:

| Class | Description |
|-------|-------------|
| `proj:Programme` | The unique PEPR |
| `proj:TargetedProject` | Projet ciblé |
| `proj:AAPProject` | Projet AAP |
| `proj:Platform` | Thematic platform |
| `proj:WorkPackage` | WP within a project |
| `proj:Person` | Researcher / contributor |
| `proj:Organization` | Lab, university, company |
| `proj:Competence` | Skill or domain expertise |
| `proj:Deliverable` | WP output |
| `proj:Task` | Atomic work unit |
| `proj:Tool` | Software / instrument |
| `proj:Product` | Dataset / software artefact |

---

## GitHub Actions CI example

Create `.github/workflows/validate.yml`:

```yaml
name: Validate PEPR graphs
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install rdflib pyyaml pyshacl
      - run: |
          python scripts/yaml_to_ttl.py \
            --programme data/programme.yaml \
            --projects-dir data/projects/ \
            --validate \
            --shapes ontology/proj-shapes.ttl
```

This will automatically validate every PR before merging.
