# Guide: How to Fill Your Project's YAML File

Every team is required to retrieve their project's file, verify the auto-populated data, and complete missing technical details.

## Step 1: Use `list_keywords.yaml` as your reference

Before filling out any field, inspect `yaml_templates_projects/list_keywords.yaml`. This file contains a preliminary approved vocabulary for keywords, competencies, domains, and tools.

 - Use existing terms: Always prefer terms already defined in `list_keywords.yaml`.

 - Proposing new terms: If your project requires a keyword, competency, or tool that is not in `list_keywords.yaml`, add it directly to your YAML file and mention it so the ontology team can register it.

## Step 2: Information you must fill or verify

Please open `yaml_templates_projects/<your_project_name>.yaml` and complete the following sections:

1. Core Metadata keywords

    - `scientific_domain`: Specify the primary scientific domains covered by your project.

    - `methodology`: Specify the general methodological approach.

2. Competencies 

    - Assign competency keywords either at the overall Project level, or fine-grained at the individual Work Package  (WP) level.

3. Methodology-Specific Tools

    - Depending on your project's methodology, fill in the corresponding tool lists (using `list_keywords.yaml` for inspiration):

```
# Fill the list that applies to your project methodology:

# If your methodology includes characterization:
characterization_tools:
  - Tool_Name_1
  - Tool_Name_2

# If your methodology includes simulation:
simulation_tools:
  - Tool_Name_1
  - Tool_Name_2

# If your methodology includes synthesis:
synthesis_tools:
  - Tool_Name_1
  - Tool_Name_2
```


4. Work Package (WP) Granularity

    > **Important**: Specific tools used and products/deliverables generated MUST be assigned to their respective Work Package.

For each Work Package in your file, ensure you fill:

 - `tools`: Specific tools, instruments, or software used within this WP.

 - `products` / `deliverables`: Any output, dataset, report, hardware, or deliverable produced by this specific WP.

# Step-by-Step Workflow for Teams
 
**You can either do the following, or just email us back with your modified file.**


1. Clone the repository:
    
```
git clone [https://github.com/cnherrera/DIADEM-ontology.git](https://github.com/cnherrera/DIADEM-ontology.git)
cd DIADEM-ontology
```

2. Locate your file:
 - Go to `yaml_templates_projects/` and open your project's pre-filled YAML file (`project_<your_project_name>.yaml`).

3. Verify and fill the fields:
   Follow the guide above to check pre-filled information, add competencies, methodology tools, and WP-level deliverables.

4. Submit via Pull Request:
 ```
git checkout -b feature/update-yaml-<your_project_name>
git add yaml_templates_projects/project_<your_project_name>.yaml
git commit -m "docs: complete YAML information for <your_project_name>"
git push origin feature/update-yaml-<your_project_name>
```

