# Guide: How to Fill Your Project's File

Every team is required to retrieve their project's file, verify the auto-populated data, and complete the missing technical details.

> **Not comfortable with YAML?** You do not need to touch it.
> Go to the [`Excel_version/`](Excel_version) folder and work with the **Excel** version of your project's file instead. It contains exactly the same information, laid out in sheets and tables.
>
> **Choose ONE format (YAML or Excel) and send back by e-mail only that one.**

---

## Quick workflow (3 steps)

### 1. Download your file

Your project's file is named after your project:

| Format | Folder | File name |
|---|---|---|
| YAML | `yaml_templates_projects/` | `project_<your_project_name>.yaml` |
| Excel (recommended if you don't use YAML) | [`Excel_version/`](Excel_version) | `project_<your_project_name>.xlsx` |


To download it from GitHub: open the folder, click on your file, then click the **download button** (the arrow pointing down, "Download raw file") at the top right of the file view.

### 2. Verify and complete it

- Check that the pre-filled information is correct and fix anything that is wrong.
- Fill in the missing information, following the guide below.
- **Excel users:** read the `Instructions` sheet first. Empty cells to fill in are highlighted in yellow. Please do not rename sheets, rename or delete columns, or insert rows above the table headers.
- **YAML users:** keep the existing structure and indentation; only edit the values.

### 3. Send it back by email

Email your modified file to **[your-email-address]**.

- Subject: `DIADEM project file - <your_project_name>`
- Attach only the file you worked on, and **keep its original file name**.
- If you add a new keyword, competency or tool (see Step 1 below), mention it in the email.

That's it. If you know Git and prefer to use it, see [the optional Git workflow](#optional-git-workflow) at the end.

---

## What to fill or verify

### Step 1: Use `list_keywords.yaml` as your reference

Before filling out any field, look at `yaml_templates_projects/list_keywords.yaml`. This file contains a preliminary approved vocabulary for keywords, competencies, domains, and tools. It is a plain text list: you can open it directly in the browser on GitHub, and you do not need to edit it.

- **Use existing terms:** always prefer terms already defined in `list_keywords.yaml`.
- **Proposing new terms:** if your project requires a keyword, competency, or tool that is not in `list_keywords.yaml`, add it to your file and mention it in your email, so the ontology team can register it.

### Step 2: Information you must fill or verify

Complete the following sections. The table shows where to find each one in the Excel file.

| What to fill | YAML | Excel |
|---|---|---|
| Scientific domains and methodology | `scientific_domain`, `methodology` | `Keywords` sheet |
| Project-level competencies | `competences` | `Keywords` sheet |
| Methodology-specific tools | `characterization_tools`, `simulation_tools`, `synthesis_tools` | `Keywords` sheet |
| Tools used in each Work Package | `tools` inside each work package | `Work Packages Tools` sheet |
| Products of each Work Package | `products` inside each work package | `Work Packages Products` sheet |
| Deliverables of each Work Package | `deliverables` inside each work package | `Work Packages Deliverables` sheet |
| Competencies of each Work Package | `competences` inside each work package | `Work Packages Competences` sheet |

In the Excel file, the rows of the `Work Packages ...` sheets are linked to their Work Package by the grey `parent_number` and `parent_acronym` columns. When you add a row, copy those two values from the Work Package it belongs to.

#### 1. Core metadata keywords

- `scientific_domain`: specify the primary scientific domains covered by your project.
- `methodology`: specify the general methodological approach.

#### 2. Competencies

Assign competency keywords either at the overall Project level, or at a finer level for each individual Work Package (WP).

#### 3. Methodology-specific tools

Depending on your project's methodology, fill in the corresponding tool lists (use `list_keywords.yaml` for inspiration). In the Excel file, each list is a column of the `Keywords` sheet: write one tool per cell.

In the YAML file:

```yaml
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

#### 4. Work Package (WP) granularity

> **Important:** specific tools used and products/deliverables generated MUST be assigned to their respective Work Package.

For each Work Package in your file, make sure you fill:

- `tools`: specific tools, instruments, or software used within this WP.
- `products` / `deliverables`: any output, dataset, report, hardware, or deliverable produced by this specific WP.

---

