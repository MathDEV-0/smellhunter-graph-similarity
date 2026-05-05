Similarity Graphs & Smell Analysis Pipeline (SmellHunter)
=========================================================

* * * * *

Table of Contents
-----------------

1.  [Overview](#overview)
2.  [Architecture](#architecture)
3.  [Workflow](#workflow)
4.  [Project Structure](#project-structure)
5.  [Prerequisites](#prerequisites)
6.  [Install Dependencies](#install-dependencies)
7.  [Ontology and Input Data](#ontology-and-input-data)
8.  [Configuration](#configuration)
9.  [Running the Project](#running-the-project)
10. [Graph Construction](#graph-construction)
11. [Similarity Methods](#similarity-methods)
12. [Generated Outputs](#generated-outputs)
13. [Metrics Used](#metrics-used)

* * * * *

Overview
--------

This project implements a **semantic graph-based analysis pipeline** for software projects, combining:

-   RDF ontology processing
-   Feature extraction from software projects
-   Graph-based representation (NetworkX)
-   Semantic propagation over relationships
-   Similarity computation between projects
-   Structural and semantic comparison using:
    -   Cosine Similarity
    -   Jaccard Similarity
    -   DeltaCon

The goal is to analyze **software similarity and structural consistency**, supporting research in:

-   Code smells detection (indirectly via structure similarity)
-   Software architecture comparison
-   Clone detection
-   Semantic similarity in software engineering datasets

* * * * *

Architecture
------------

```
flowchart LRA[RDF Ontology TTL] --> B[Label Extraction]B --> C[Filtered Relation Graph]C --> D[Feature Matrix Construction]D --> E[Cosine Similarity]C --> F[Project Feature Graphs]F --> G[Jaccard Similarity]F --> H[DeltaCon Similarity]E --> I[Similarity Matrix]G --> IH --> II --> J[Heatmaps + CSV Outputs]
```

* * * * *

Workflow
--------

1.  Load RDF ontology (.ttl)
2.  Extract labels using RDFLib
3.  Filter important relations
4.  Build global feature graph (NetworkX)
5.  Identify projects and entity types
6.  Build feature matrices (weighted + binary)
7.  Construct semantic propagation graphs
8.  Compute similarity metrics:
    -   Cosine (vector space)
    -   Jaccard (structural overlap)
    -   DeltaCon (graph similarity)
9.  Export results (CSV + heatmaps + graphs)

* * * * *

Project Structure
-----------------

```
smellhunter-similarity/
│
├── ontology_smellhunter.py
├── ontologia_nova_05-05.ttl
├── output/
│├── feature_matrix_weighted.csv
│├── feature_matrix_binary.csv
│├── cosine_similarity.csv
│├── jaccard_matrix.csv
│├── deltacon_matrix.csv
│├── cosine_heatmap.png
│├── deltacon_heatmap.png
│
├── requirements.txt
└── README.md
```

* * * * *

Prerequisites
-------------

Python
------

Python 3.9+ recommended

```
python --version
```

* * * * *

Install Dependencies
--------------------

Create virtual environment (recommended)

### Windows

```
python -m venv venvvenv\Scripts\activate
```

### Linux / Mac

```
python -m venv venvsource venv/bin/activate
```

Install dependencies:

```
pip install rdflib networkx numpy pandas matplotlib scikit-learn scipy
```

* * * * *

Ontology and Input Data
---------------------

The system consumes RDF Turtle files (`.ttl`) containing:

-   Software projects
-   Tools, frameworks, languages
-   Architectural patterns
-   Code smells
-   Development practices
-   Domains

Example relations:

-   usesFramework
-   usesLanguage
-   hasSmell
-   followsArchitecture
-   hasTestCoverageLevel

Only **important relations** are kept for analysis.

* * * * *

Configuration
-------------

Key parameters are defined inside the script:

```
IMPORTANT = {    "usesFramework",    "usesLanguage",    "usesDatabase",    "usesTool",    "followsArchitecture",    "hasSmell",    "followsDevelopmentPractice",    "hasContributorCount",    "hasDocumentationLevel",    "hasTestCoverageLevel"}
```

Semantic propagation depth:

```
max_hops = 1
```

* * * * *

Running the Project
-------------------

Execute:

```
python similarity_pipeline.py
```

The pipeline will:

-   Parse ontology
-   Build graphs
-   Compute similarity matrices
-   Generate visualizations
-   Export CSV outputs

* * * * *

Graph Construction
------------------

Two main representations are built:

### 1\. Feature Graph (Vector Space)

Each project is represented as a feature vector:

-   features = tools, languages, architecture, smells
-   weights applied per relation type
-   used for cosine similarity

### 2\. Semantic Graph (Structure Graph)

Graph where:

-   nodes = features of a project
-   edges = semantic relationships between features
-   used for Jaccard + DeltaCon

This captures **structure beyond simple feature overlap**.

* * * * *

Similarity Methods
------------------

### Cosine Similarity

Measures similarity between weighted feature vectors:

-   Captures intensity of shared technologies
-   Sensitive to feature importance weights

Used for:

-   semantic overlap
-   technology stack similarity

* * * * *

### Jaccard Similarity

Measures structural overlap between graphs:

-   node + edge set comparison
-   ignores weights

Used for:

-   clone detection
-   structural similarity

* * * * *

### DeltaCon

Advanced graph similarity method:

-   based on belief propagation
-   compares global graph structure
-   robust to small local changes

Used for:

-   deep structural equivalence
-   architecture similarity detection

* * * * *

Generated Outputs
-----------------

The pipeline generates:

### Matrices

-   cosine_similarity.csv
-   jaccard_matrix.csv
-   deltacon_matrix.csv

### Feature Space

-   feature_matrix_weighted.csv
-   feature_matrix_binary.csv

### Visualizations

-   cosine_heatmap.png
-   deltacon_heatmap.png

### Debug Outputs

-   per-project graph exports
-   semantic propagation graphs

* * * * *

Metrics Used
------------

### Feature Categories

-   Programming Languages
-   Frameworks
-   Databases
-   Tools
-   Architectural Patterns
-   Code Smells
-   Development Practices
-   Team Size
-   Documentation Level
-   Test Coverage

### Graph Features

-   Nodes: software entities
-   Edges: semantic relationships
-   Relations: weighted by importance

* * * * *

Final Note
----------

This system combines:

-   ontology-based modeling
-   graph theory
-   feature engineering
-   similarity learning

to support **software engineering research and smell-aware structural analysis**.
