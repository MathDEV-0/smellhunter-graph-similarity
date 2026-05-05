from rdflib import Graph, RDFS
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

# =========================
# 0. OUTPUT DIR
# =========================
os.makedirs("output", exist_ok=True)

# =========================
# 1. LOAD RDF
# =========================
g = Graph()
g.parse("ontologia_nova_05-05.ttl", format="turtle")

print("RDF triples loaded:", len(g))



# =========================
# 2. LABEL INDEX
# =========================
labels = {}

for s, p, o in g:
    if p == RDFS.label:
        labels[str(s)] = str(o)

def get_label(x):
    return labels.get(str(x), str(x).split("/")[-1])

# =========================
# 3. IMPORTANT RELATIONS
# =========================
IMPORTANT = {
    "usesFramework",
    "usesLanguage",
    "usesDatabase",
    "usesTool",
    "dependsOn",
    "followsArchitecture",
    "hasSmell",

    "followsDevelopmentPractice",
    "hasContributorCount",
    "hasDocumentationLevel",
    "hasTestCoverageLevel"
}

# =========================
# 4. BUILD GRAPH
# =========================
G = nx.Graph()

for s, p, o in g:
    if p == RDFS.label:
        continue

    rel = get_label(p)

    if rel not in IMPORTANT:
        continue

    s_name = get_label(s)
    o_name = get_label(o)

    G.add_edge(s_name, o_name, relation=rel)

print("\n--- GRAPH STATS ---")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# =========================
# 5. PROJECTS
# =========================
PROJECTS = sorted([
    n for n in G.nodes()
    if "Project" in n
])

PROJECTS = [p for p in PROJECTS if p in G]

print("\nProjects:", PROJECTS)

# ====================================================
# 5.1 ENTITY TYPES
# ====================================================
ENTITY_TYPES = {}

for s, p, o in g:

    rel = get_label(p)

    # rdf:type
    if "type" in rel:

        entity = get_label(s)
        entity_type = get_label(o)

        ENTITY_TYPES[entity] = entity_type

print("\n=========================")
print("ENTITY TYPES")
print("=========================")

for entity, etype in sorted(ENTITY_TYPES.items()):
    print(f"{entity} -> {etype}")

# ====================================================
# 5.2 SEMANTIC RELATIONS
# ====================================================
SEMANTIC_RELATIONS = []
SEMANTIC_IMPORTANT = {
    "dependsOn",
    "subClassOf",
    "type",
    "domain",
    "range",
    "subPropertyOf"
}

PROJECT_SET = set(PROJECTS)

for s, p, o in g:

    rel = get_label(p)

    if rel in SEMANTIC_IMPORTANT:

        s_name = get_label(s)
        o_name = get_label(o)
        if s_name in PROJECT_SET or o_name in PROJECT_SET:

            SEMANTIC_RELATIONS.append(
                (s_name, o_name, rel)
            )

print("\n=========================")
print("SEMANTIC RELATIONS")
print("=========================")

for s, o, rel in SEMANTIC_RELATIONS:
    print(f"{s} -- {o} | relation={rel}")

# =========================
# 6. EGONET
# =========================
# =========================
# VISUAL GRAPH
# (Project no centro)
# =========================
def build_visual_subgraph(project):

    nodes = {project}
    edges = []

    for u, v, d in G.edges(data=True):

        if project == u or project == v:

            nodes.add(u)
            nodes.add(v)

            edges.append((u, v, d))

    H = nx.Graph()

    H.add_nodes_from(nodes)

    for u, v, d in edges:

        H.add_edge(
            u,
            v,
            relation=d["relation"]
        )

    return H


# =========================
# SEMANTIC GRAPH
# (Feature -> Feature)
# =========================
def build_semantic_subgraph(project):

    H = nx.Graph()

    features = []

    for u, v, d in G.edges(data=True):

        if u == project:
            features.append((v, d["relation"]))

        elif v == project:
            features.append((u, d["relation"]))

    for i in range(len(features)):

        for j in range(i + 1, len(features)):

            f1, rel1 = features[i]
            f2, rel2 = features[j]

            H.add_edge(
                f1,
                f2,
                relation=f"{rel1}-{rel2}"
            )

    return H

visual_graphs = {
    p: build_visual_subgraph(p)
    for p in PROJECTS
}


# =========================
# 7. SAVE + PLOT GRAPH
# =========================
def draw_graph(graph, title):

    if len(graph.nodes()) == 0:
        print(f"[SKIP] {title} vazio")
        return

    plt.figure(figsize=(8, 5))

    pos = nx.spring_layout(
        graph,
        seed=42
    )

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=900,
        font_size=8
    )

    edge_labels = nx.get_edge_attributes(
        graph,
        "relation"
    )

    nx.draw_networkx_edge_labels(
        graph,
        pos=pos,
        edge_labels=edge_labels,
        font_size=7
    )

    plt.title(title)
    plt.axis("off")

    path = f"output/{title}.png"

    # SALVA ANTES
    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"[SAVED] {path}")

    # OPCIONAL
    plt.show()

    plt.close()

# for p in PROJECTS:
#     draw_graph(
#         visual_graphs[p],
#         p
#     )

# =========================================================
# 8. FEATURE SPACE / ADJACENCY MATRIX
# =========================================================

# FEATURES = [

#     # =========================
#     # PROJECT STRUCTURE
#     # =========================

#     # Languages
#     "Java","JavaScript","Python","TypeScript","C","C++",
#     "CSharp","Kotlin","Go","Rust","Swift","PHP","Ruby",
#     "Scala","R","MATLAB","Dart","Perl","Lua","ObjectiveC",
#     "Shell","Assembly","Julia","Haskell","Elixir","Erlang",
#     "Groovy","VisualBasic","Fortran","COBOL",

#     # Tools
#     "Jenkins","Docker","Kubernetes","Git","GitHub",
#     "GitLab","Bitbucket","SonarQube","Maven","Gradle",
#     "ApacheAnt","Terraform","Ansible","Prometheus",
#     "Grafana","Nginx","ApacheKafka","RabbitMQ","Redis",
#     "Elasticsearch","Logstash","Kibana","Postman",
#     "Swagger","OpenAPI","Helm","Istio","ArgoCD",
#     "TravisCI","CircleCI","Selenium","JUnit",
#     "PyTest","Cypress","TerraformCloud","Vault",
#     "Consul","Vagrant","Packer",

#     # Domains
#     "ECommerce","Healthcare","Finance","Banking",
#     "Education","Entertainment","Gaming","SocialMedia",
#     "Streaming","Telecommunications","Cybersecurity",
#     "DevOps","CloudComputing","ArtificialIntelligence",
#     "MachineLearning","DataScience","InternetOfThings",
#     "EmbeddedSystems","Automotive","Transportation",
#     "Logistics","SupplyChain","Retail","Agriculture",
#     "Energy","Manufacturing","Government","Insurance",
#     "HumanResources","Marketing","CRM","ERP",
#     "ProjectManagement","ContentManagement","Media",
#     "Sports","Tourism","Hospitality","RealEstate",
#     "LegalTech","Bioinformatics","Blockchain",
#     "Cryptocurrency","DigitalLibrary","Messaging",
#     "VideoConference","FoodDelivery","RideSharing",
#     "SmartCity","Automation","Robotics",
#     "ScientificComputing",

#     # Databases
#     "MySQL","MariaDB","SQLite","OracleDatabase",
#     "MicrosoftSQLServer","Cassandra","Neo4j",
#     "CouchDB","Firebase","DynamoDB","InfluxDB",
#     "HBase","AmazonRDS","AmazonAurora",
#     "CockroachDB","ArangoDB","OrientDB","Db2",
#     "Teradata","ClickHouse","BigQuery","Snowflake",
#     "Realm","RavenDB","Memcached","Hive",
#     "Greenplum","TimescaleDB",

#     # Architectures
#     "Monolith","Microservices",
#     "ServiceOrientedArchitecture",
#     "EventDrivenArchitecture",
#     "LayeredArchitecture",
#     "HexagonalArchitecture",
#     "CleanArchitecture",
#     "OnionArchitecture",
#     "ClientServer",
#     "PeerToPeer",
#     "MVC","MVVM","MVP","CQRS",
#     "EventSourcing",
#     "DomainDrivenDesign",
#     "RESTArchitecture",
#     "GraphQLArchitecture",
#     "ServerlessArchitecture",
#     "PipelineArchitecture",
#     "SpaceBasedArchitecture",
#     "MicrokernelArchitecture",
#     "ReactiveArchitecture",
#     "DistributedArchitecture",
#     "CloudNativeArchitecture",
#     "MultiTenantArchitecture",
#     "ModularMonolith",
#     "NLayerArchitecture",
#     "ComponentBasedArchitecture",
#     "DataCentricArchitecture",
#     "BrokerArchitecture",
#     "BlackboardArchitecture",
#     "MessageBusArchitecture",
#     "SagaPattern",
#     "BackendForFrontend",
#     "APIFirst",
#     "ContractFirst",
#     "DatabasePerService",
#     "SharedDatabaseArchitecture",
#     "StranglerFigPattern",
#     "SidecarPattern",
#     "CircuitBreakerPattern",
#     "BulkheadPattern",
#     "ServiceDiscovery",
#     "APIGateway",
#     "Orchestration",
#     "Choreography",

#     # Frameworks
#     "Spring","SpringBoot","Hibernate","JakartaEE",
#     "Quarkus","Micronaut","Vertx","NodeJS",
#     "Express","NestJS","React","NextJS",
#     "Angular","VueJS","NuxtJS","Svelte",
#     "Django","FastAPI","Flask","Pyramid",
#     "RubyOnRails","Laravel","Symfony",
#     "ASPNet","ASPNetCore","Blazor",
#     "Phoenix","Gin","Fiber","Echo",
#     "Beego","Flutter","ReactNative",
#     "Xamarin","Electron","TensorFlow",
#     "PyTorch","Keras","ApacheSpark",
#     "Hadoop",

#     # Code Smells
#     "LongMethod","GodClass","FeatureEnvy",
#     "Bloaters","LargeClass","LargeMethod",
#     "LongParameterList","DataClass",
#     "PrimitiveObsession","DuplicateCode",
#     "LazyClass","SpeculativeGenerality",
#     "TemporaryField","DataClumps",
#     "ShotgunSurgery","MiddleMan",
#     "MessageChains","RefusedBequest",
#     "InappropriateIntimacy",
#     "SwitchStatements",
#     "ParallelInheritanceHierarchies",

#     # =========================
#     # ENGINEERING PRACTICES
#     # =========================

#     # Development Practices
#     "CodeReview",
#     "PairProgramming",
#     "TDD",
#     "CI_CD",
#     "Scrum",
#     "Kanban",
#     "Agile",
#     "StaticAnalysis",

#     # Team Size
#     "SoloDeveloper",
#     "SmallTeam",
#     "MediumTeam",
#     "LargeTeam",
#     "EnterpriseScaleTeam",

#     # Documentation
#     "NoDocumentation",
#     "LowDocumentation",
#     "MediumDocumentation",
#     "HighDocumentation",
#     "ComprehensiveDocumentation",

#     # Test Coverage
#     "NoCoverage",
#     "LowCoverage",
#     "MediumCoverage",
#     "HighCoverage",
#     "VeryHighCoverage",
# ]

# FEATURES = sorted(set(FEATURES))

FEATURES = sorted([
    entity
    for entity, t in ENTITY_TYPES.items()
    if t not in {
        "owl#Class",
        "owl#ObjectProperty",
        "owl#Ontology",
        "Project"
    }
])

# =========================
# FEATURE MATRIX
# =========================
feature_matrix_weighted = pd.DataFrame(
    0,
    index=PROJECTS,
    columns=FEATURES,
    dtype=float
)

feature_matrix_binary = pd.DataFrame(
    0,
    index=PROJECTS,
    columns=FEATURES,
    dtype=int
)

def normalize_node(n):
    n = str(n)
    if n.startswith("Project"):
        return n   # mantém identidade
    return n


def build_feature_graph(project):

    project = normalize_node(project)

    H = nx.Graph()

    project_features = []

    # --------------------------------
    # direct features only
    # --------------------------------
    for u, v, d in G.edges(data=True):

        u = normalize_node(u)
        v = normalize_node(v)

        if u == project:
            project_features.append((v, d["relation"]))

        elif v == project:
            project_features.append((u, d["relation"]))

    # --------------------------------
    # add nodes
    # --------------------------------
    for feature, rel in project_features:
        H.add_node(feature, relation=rel)

    # --------------------------------
    # connect only same-relation features
    # --------------------------------
    for i in range(len(project_features)):

        f1, rel1 = project_features[i]

        for j in range(i + 1, len(project_features)):

            f2, rel2 = project_features[j]

            if rel1 == rel2:
                H.add_edge(f1, f2, relation=rel1)

    return H

RELATION_WEIGHTS = {
    "usesLanguage": 4,
    "usesFramework": 6,
    "usesDatabase": 5,
    "usesTool": 2,
    "followsArchitecture": 8,
    "hasSmell": 7,
    "belongsToDomain": 5,
    "dependsOn": 3,
    "followsDevelopmentPractice": 6,
    "hasContributorCount": 4,
    "hasDocumentationLevel": 5,
    "hasTestCoverageLevel": 7
}

# =========================
# POPULATE FEATURE MATRIX
# =========================
for s, p, o in g:

    rel = get_label(p)

    if rel not in IMPORTANT:
        continue

    s_name = get_label(s)
    o_name = get_label(o)

    weight = RELATION_WEIGHTS.get(rel, 1)

    # Project -> Feature
    if s_name in PROJECTS and o_name in FEATURES:

        # weighted (cosine)
        feature_matrix_weighted.loc[s_name, o_name] = weight

        # binary (deltacon/jaccard)
        feature_matrix_binary.loc[s_name, o_name] = 1

    # Feature -> Project
    if o_name in PROJECTS and s_name in FEATURES:

        feature_matrix_weighted.loc[o_name, s_name] = weight
        feature_matrix_binary.loc[o_name, s_name] = 1

# PARA DELTACON
semantic_graphs = {
    p: build_feature_graph(p)
    for p in PROJECTS
}



# =========================
# SAVE FEATURE MATRIX
# =========================
feature_matrix_weighted.to_csv("output/feature_matrix_weighted.csv")
feature_matrix_binary.to_csv("output/feature_matrix_binary.csv")

print("[SAVED] feature_matrix.csv")

# =========================
# SEMANTIC COSINE SIMILARITY
# =========================
from sklearn.metrics.pairwise import cosine_similarity

cos_matrix = cosine_similarity(
    feature_matrix_weighted.values
)

df_cos = pd.DataFrame(
    cos_matrix,
    index=PROJECTS,
    columns=PROJECTS
)

df_cos.to_csv(
    "output/cosine_similarity.csv"
)

print("\n--- SEMANTIC SIMILARITY ---")

for a, b in itertools.combinations(PROJECTS, 2):

    score = df_cos.loc[a, b]

    print(
        f"{a} vs {b} | "
        f"Cosine Similarity: {score:.4f}"
    )

# =========================
# 8. JACCARD
# =========================
def structural_jaccard(g1, g2):
    n1, n2 = set(g1.nodes()), set(g2.nodes())
    e1, e2 = set(g1.edges()), set(g2.edges())

    s1 = n1 | set(map(str, e1))
    s2 = n2 | set(map(str, e2))

    union = s1 | s2
    if not union:
        return 0

    return len(s1 & s2) / len(union)

# =========================
# 9. DELTACON
# =========================
# =========================
# 9. DELTACON (REAL IMPLEMENTATION)
# =========================
from scipy.sparse import csc_matrix
from scipy.sparse import identity
from scipy.sparse import diags
from scipy.sparse import dok_matrix
from scipy.sparse.linalg import inv
from numpy import trace
from numpy import square
from math import sqrt
import random

# ---------------------------------
# BUILD ADJACENCY MATRIX
# ---------------------------------
def graph_to_adjmatrix(g, global_nodes):

    idx = {
        node: i
        for i, node in enumerate(global_nodes)
    }

    n = len(global_nodes)

    A = dok_matrix((n, n), dtype=float)

    for u, v in g.edges():

        i = idx[u]
        j = idx[v]

        A[i, j] = 1
        A[j, i] = 1

    return csc_matrix(A)

# ---------------------------------
# RANDOM PARTITIONS
# ---------------------------------
def partition_nodes(num_groups, size):

    nodes = list(range(size))
    nodes = sorted(nodes)

    partitions = {}

    group_size = max(1, size // num_groups)

    for i in range(num_groups):

        start = i * group_size

        if i == num_groups - 1:
            partitions[i] = nodes[start:]
        else:
            partitions[i] = nodes[start:start + group_size]

    return partitions

# ---------------------------------
# PARTITION -> E MATRIX
# ---------------------------------
def partition_to_e(partitions, size):

    E = {}

    for p in partitions:

        vec = np.zeros(size)

        for idx in partitions[p]:
            vec[idx] = 1.0

        E[p] = vec.reshape(-1, 1)

    return E

# ---------------------------------
# FAST BELIEF PROPAGATION
# ---------------------------------
def inverse_matrix(A, E):

    n = A.shape[0]

    I = identity(n)

    D = diags(
        np.array(A.sum(axis=1)).flatten(),
        0
    )

    D_dense = D.toarray()

    c1 = trace(D_dense) + 2
    c2 = trace(square(D_dense)) - 1

    if c2 <= 0:
        c2 = 1e-9

    h = sqrt(
        (-c1 + sqrt(c1 * c1 + 4 * c2))
        / (8 * c2)
    )

    a = (4 * h * h) / (1 - 4 * h * h)
    c = (2 * h) / (1 - 4 * h * h)

    M = c * A - a * D

    results = []

    for p in E:

        inv_vec = E[p].copy()
        mat = E[p].copy()

        power = 1

        while power < 10:

            mat = M.dot(mat)

            inv_vec += mat

            power += 1

        results.append(inv_vec)

    return np.hstack(results)

# ---------------------------------
# SINGLE DELTACON EXECUTION
# ---------------------------------
def deltacon_once(A1, A2, groups=5):

    size = A1.shape[0]

    partitions = partition_nodes(groups, size)

    E = partition_to_e(partitions, size)

    S1 = inverse_matrix(A1, E)
    S2 = inverse_matrix(A2, E)

    d = np.sum(
        (
            np.sqrt(np.abs(S1))
            -
            np.sqrt(np.abs(S2))
        ) ** 2
    )

    d = sqrt(d)

    sim = 1 / (1 + d)

    return sim

# ---------------------------------
# FINAL DELTACON
# ---------------------------------
def deltacon_similarity(g1, g2, groups=5, iterations=10):
    nx.is_isomorphic(g1, g2)
    global_nodes = sorted(list(set(g1.nodes()) | set(g2.nodes())))
    A1 = graph_to_adjmatrix(g1, global_nodes)
    A2 = graph_to_adjmatrix(g2, global_nodes)

    sims = []

    for _ in range(iterations):

        sims.append(
            deltacon_once(
                A1,
                A2,
                groups
            )
        )

    return np.mean(sims)

# =========================
# 10. MATRICES
# =========================
print("\n--- SIMILARITY MATRIX ---")

jaccard_matrix = {}
deltacon_matrix = {}

for a, b in itertools.combinations(PROJECTS, 2):
    j = structural_jaccard(
    semantic_graphs[a],
    semantic_graphs[b]
    )

    d = deltacon_similarity(
        semantic_graphs[a],
        semantic_graphs[b]
    )

    jaccard_matrix[(a, b)] = j
    deltacon_matrix[(a, b)] = d

    print(f"{a} vs {b} | Jaccard: {j:.4f} | DeltaCon: {d:.4f}")

# =========================
# 11. DATAFRAMES + CSV
# =========================
df_j = pd.DataFrame(index=PROJECTS, columns=PROJECTS, dtype=float)
df_d = pd.DataFrame(index=PROJECTS, columns=PROJECTS, dtype=float)

for i in PROJECTS:
    for j in PROJECTS:
        if i == j:
            df_j.loc[i, j] = 1
            df_d.loc[i, j] = 1
        else:
            df_j.loc[i, j] = structural_jaccard(semantic_graphs[i], semantic_graphs[j])
            df_d.loc[i, j] = deltacon_similarity(semantic_graphs[i], semantic_graphs[j])

df_j.to_csv("output/jaccard_matrix.csv")
df_d.to_csv("output/deltacon_matrix.csv")

print("[SAVED] matrices CSV")

# =========================
# 12. HEATMAPS
# =========================
# =========================
# COSINE HEATMAP
# =========================
plt.figure(figsize=(6, 5))

plt.imshow(df_cos.values)

plt.xticks(
    range(len(PROJECTS)),
    PROJECTS,
    rotation=45
)

plt.yticks(
    range(len(PROJECTS)),
    PROJECTS
)

# VALORES NAS CÉLULAS
for i in range(len(PROJECTS)):
    for j in range(len(PROJECTS)):

        value = df_cos.values[i, j]

        plt.text(
            j,
            i,
            f"{value:.2f}",
            ha="center",
            va="center",
            color="white",
            fontsize=12
        )

plt.title("Semantic Cosine Similarity")
plt.colorbar()

plt.savefig(
    "output/cosine_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# =========================
# DELTACON HEATMAP
# =========================
plt.figure(figsize=(6, 5))

plt.imshow(df_d.values)

plt.xticks(
    range(len(PROJECTS)),
    PROJECTS,
    rotation=45
)

plt.yticks(
    range(len(PROJECTS)),
    PROJECTS
)

# VALORES NAS CÉLULAS
for i in range(len(PROJECTS)):
    for j in range(len(PROJECTS)):

        value = df_d.values[i, j]

        plt.text(
            j,
            i,
            f"{value:.2f}",
            ha="center",
            va="center",
            color="white",
            fontsize=12
        )

plt.title("DeltaCon Heatmap")
plt.colorbar()

plt.savefig(
    "output/deltacon_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("[DONE] everything saved in /output")

# =========================
# 13. PRINT ALL GRAPHS
# =========================

print("\n=========================")
print("VISUAL GRAPHS")
print("=========================")

for name, graph in visual_graphs.items():

    print(f"\n--- {name} ---")

    print("Nodes:")
    print(list(graph.nodes()))

    print("\nEdges:")
    for u, v, d in graph.edges(data=True):
        print(f"{u} -- {v} | relation={d.get('relation')}")

print("\n=========================")
print("SEMANTIC GRAPHS")
print("=========================")

for name, graph in semantic_graphs.items():

    print(f"\n--- {name} ---")

    print("Nodes:")
    print(list(graph.nodes()))

    print("\nEdges:")
    for u, v in graph.edges():
        print(f"{u} -- {v}")
