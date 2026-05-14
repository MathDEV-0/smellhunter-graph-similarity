from rdflib import RDF, Graph, RDFS
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

BAD_NAMESPACES = (
    "http://www.w3.org/1999/02/22-rdf-syntax-ns",
    "http://www.w3.org/2000/01/rdf-schema",
    "http://www.w3.org/2002/07/owl"
)

def is_system_uri(x):

    x = str(x)

    return any(
        x.startswith(ns)
        for ns in BAD_NAMESPACES
    )

def canonicalize_node(node):

    node = str(node)

    if node.startswith("Project"):
        return "PROJECT"

    return node

# =========================
# 0. OUTPUT DIR
# =========================
os.makedirs("output", exist_ok=True)

# =========================
# 1. LOAD RDF
# =========================
g = Graph()
g.parse("urn_webprotege_ontology_fdf018c4-b71a-47b6-a75d-7c9b86689079.ttl", format="turtle")

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

    #Architectural Aspects(1)
    "hasArchitecturalAspects",

        #Modularization (2)
        "Modularization",

        #Persistence(2)
        "Persistence",

        #Resilience(2)
        "Resilience",

        #Security(2)
        "Security",

        # API Integration Pattern(2)
        "hasApiIntegrationPattern",

        # Architectural Observability (2)
        "hasArchitecturalObservability",

        # Architectural Style (2)
        "hasArchitecturalStyle",

        # Deployment and Operation (2)
        "hasDeploymentAndOperation",

        # Design Patterns (2)
        "hasDesignPatterns",
        
        #Governance (2)
        "hasGovernance",

        #Internal Organization (2)
        "hasInternalOrganization",

    # OrganizationalAspects (1)
    "hasOrganizationalAspects",

        #Budget(2)
        "hasBudget",

        #Communication (2)
        "hasCommunicationMode",
            #Communication(3)
            "hasCommunicationModeDescription",
            "hasDocumentationLanguage",
            "hasDocumentationLanguageName",
            "hasPrimaryLanguage",
            "hasPrimaryLanguageName",
            "usesCommunicationTools",
            
        #Location(2)
        "hasLocation",

        #Organizational Structure(2)
        "hasOrganizationalStructure",
            # Work Modality(3)
            "hasWorkModality",

        #Process(2)
        "hasProcess",
            #Agile (3)
            "hasAgileMethod",
                #Agile Culture (4)
                "hasAgileCulture",
            #DevOps (3)
            "hasDevOpsPractice",
                #DevOps culture (4)
                "hasDevOpsCulture",
            #Traditional (3)
            "hasTraditionalMethod",
                #Traditional culture (4)
                "hasTraditionalCulture",
        
        #Product Domain (2)
        "hasProductDomain",

        #Team(2)
        "hasEmployeeTurnover",
        "hasTeamSeniority",
        "hasTeamSize",

        #Temporal Structure (2)
        "hasTemporalStructure",
            #Deadlines (3)
            "hasDeadlines",
            #Frequency (3)
            "hasFrequency",
                #Deployment Frequency (4)
                "hasDeploymentFrequency",
                #Meeting Frequency (4)
                "hasMeetingFrequency",
            #Project Age(3)
            "hasProjectAge",
            #Project Stage(3)
            "hasProjectStage",
            #Sprint Length(3)
            "hasSprintDuration",

    #Quality Aspects (1)
    "hasQualityAspects",

    # Documentation (2)
    "hasDocumentation",
        #Documentation format (3)
        "DocFormats",
        #Documentation type(3)
        "DocTypes",
        # API Documentation (3)
        "hasApiDoc",
        # Diagrams(3)
        "hasDiagrams",
        #Doc Versioning(3)
        "hasDocVersioning",
    
    #Monitoring (2)
    "hasMonitoring",

    #Quality strategies(2)
    "hasQualityStrategies",

    #Reliability (2)
    "hasReliability",

    #Software Security (2)
    "hasSoftwareSecurity",

    # Testing (2)
    "hasTesting",
        #Testing Levels(3)
        "hasTestingLevels",
        #Testing Tools(3)
        "hasTestingTools",

    #Techinical Aspects(1)
    "hasTechnicalAspects",

        #Database(2)
        "hasDatabase",
            #Relational(3)
            "hasRelational",
            #NonRelational(3)
            "hasNonRelational",
        
        #Development Tools(2)
        "hasDevelopmentTools",
            #Build System(3)
            "hasBuildSystem",
            #CI/CD(3)
            "hasCI_CD",
            #Cache(3)
            "hasCache",
            #Code Editor (3)
            "hasCodeEditor",
            #Code Quality Tools(3)
            "hasCodeQuality",
            #IDE(3)
            "hasIDE",
            #Messaging (3)
            "hasMessaging",
            #Version Control(3)
            "hasVersioning",

        #Infrastructure(2)
        "hasInfrastructure",
            #Cloud (3)
            "hasCloud",
            #Containerization(3)
            "hasContainerization",
                #Containerization tools(4)
                "hasContainerizationTools",
                    #Container Orchestration(5)
                    "hasContainerOrchestration",
            #Environment(3)
            "hasEnvironment",
            #IAC(3)
            "hasIAC",
            #Network(3)
            "hasNetwork",
            #Observability(3)
            "hasObservability",
            #Scalability(3)
            "hasScalability",
        
        #Programming Language(2)
        "hasProgrammingLanguage",
            #AI (3)
            "hasAI",
            # Backend (3)
            "hasBackend",
            #Dependency Management(3)
            "hasDependencyManager",
            #Framework(3)
            "hasFramework",
                #AI Framework(4)
                "hasAIFramework",
                #Backend Framework(4)
                "hasBackendFramework",
                #Frontend Framework(4)
                "hasFrontendFramework",
                #Mobile Framework(4)
                "hasMobileFramework",
            #Frontend(3)
            "hasFrontend",
            #Mobile(3)
            "hasMobile",
}

# ==========================================
# HIERARQUIA SEMÂNTICA
# ==========================================

PARENT_MAP = {

    # =========================================================
    # LEVEL 1 ROOTS
    # =========================================================

    "hasArchitecturalAspects": None,
    "hasOrganizationalAspects": None,
    "hasQualityAspects": None,
    "hasTechnicalAspects": None,

    # =========================================================
    # ARCHITECTURAL
    # =========================================================

    "Modularization": "hasArchitecturalAspects",
    "Persistence": "hasArchitecturalAspects",
    "Resilience": "hasArchitecturalAspects",
    "Security": "hasArchitecturalAspects",
    "hasApiIntegrationPattern": "hasArchitecturalAspects",
    "hasArchitecturalObservability": "hasArchitecturalAspects",
    "hasArchitecturalStyle": "hasArchitecturalAspects",
    "hasDeploymentAndOperation": "hasArchitecturalAspects",
    "hasDesignPatterns": "hasArchitecturalAspects",
    "hasGovernance": "hasArchitecturalAspects",
    "hasInternalOrganization": "hasArchitecturalAspects",

    # =========================================================
    # ORGANIZATIONAL
    # =========================================================

    "hasBudget": "hasOrganizationalAspects",

    "hasCommunicationMode": "hasOrganizationalAspects",
    "hasCommunicationModeDescription": "hasCommunicationMode",
    "hasDocumentationLanguage": "hasCommunicationMode",
    "hasDocumentationLanguageName": "hasCommunicationMode",
    "hasPrimaryLanguage": "hasCommunicationMode",
    "hasPrimaryLanguageName": "hasCommunicationMode",
    "usesCommunicationTools": "hasCommunicationMode",

    "hasLocation": "hasOrganizationalAspects",

    "hasOrganizationalStructure": "hasOrganizationalAspects",
    "hasWorkModality": "hasOrganizationalStructure",

    "hasProcess": "hasOrganizationalAspects",

    "hasAgileMethod": "hasProcess",
    "hasAgileCulture": "hasAgileMethod",

    "hasDevOpsPractice": "hasProcess",
    "hasDevOpsCulture": "hasDevOpsPractice",

    "hasTraditionalMethod": "hasProcess",
    "hasTraditionalCulture": "hasTraditionalMethod",

    "hasProductDomain": "hasOrganizationalAspects",

    "hasEmployeeTurnover": "hasOrganizationalAspects",
    "hasTeamSeniority": "hasOrganizationalAspects",
    "hasTeamSize": "hasOrganizationalAspects",

    "hasTemporalStructure": "hasOrganizationalAspects",

    "hasDeadlines": "hasTemporalStructure",

    "hasFrequency": "hasTemporalStructure",
    "hasDeploymentFrequency": "hasFrequency",
    "hasMeetingFrequency": "hasFrequency",

    "hasProjectAge": "hasTemporalStructure",
    "hasProjectStage": "hasTemporalStructure",
    "hasSprintDuration": "hasTemporalStructure",

    # =========================================================
    # QUALITY
    # =========================================================

    "hasDocumentation": "hasQualityAspects",

    "DocFormats": "hasDocumentation",
    "DocTypes": "hasDocumentation",
    "hasApiDoc": "hasDocumentation",
    "hasDiagrams": "hasDocumentation",
    "hasDocVersioning": "hasDocumentation",

    "hasMonitoring": "hasQualityAspects",
    "hasQualityStrategies": "hasQualityAspects",
    "hasReliability": "hasQualityAspects",
    "hasSoftwareSecurity": "hasQualityAspects",

    "hasTesting": "hasQualityAspects",
    "hasTestingLevels": "hasTesting",
    "hasTestingTools": "hasTesting",

    # =========================================================
    # TECHNICAL
    # =========================================================

    "hasDatabase": "hasTechnicalAspects",
    "hasRelational": "hasDatabase",
    "hasNonRelational": "hasDatabase",

    "hasDevelopmentTools": "hasTechnicalAspects",

    "hasBuildSystem": "hasDevelopmentTools",
    "hasCI_CD": "hasDevelopmentTools",
    "hasCache": "hasDevelopmentTools",
    "hasCodeEditor": "hasDevelopmentTools",
    "hasCodeQuality": "hasDevelopmentTools",
    "hasIDE": "hasDevelopmentTools",
    "hasMessaging": "hasDevelopmentTools",
    "hasVersioning": "hasDevelopmentTools",

    "hasInfrastructure": "hasTechnicalAspects",

    "hasCloud": "hasInfrastructure",

    "hasContainerization": "hasInfrastructure",
    "hasContainerizationTools": "hasContainerization",
    "hasContainerOrchestration": "hasContainerizationTools",

    "hasEnvironment": "hasInfrastructure",
    "hasIAC": "hasInfrastructure",
    "hasNetwork": "hasInfrastructure",
    "hasObservability": "hasInfrastructure",
    "hasScalability": "hasInfrastructure",

    "hasProgrammingLanguage": "hasTechnicalAspects",

    "hasAI": "hasProgrammingLanguage",
    "hasBackend": "hasProgrammingLanguage",
    "hasDependencyManager": "hasProgrammingLanguage",

    "hasFramework": "hasProgrammingLanguage",

    "hasAIFramework": "hasFramework",
    "hasBackendFramework": "hasFramework",
    "hasFrontendFramework": "hasFramework",
    "hasMobileFramework": "hasFramework",

    "hasFrontend": "hasProgrammingLanguage",
    "hasMobile": "hasProgrammingLanguage",
}

# =========================
# 4. BUILD GRAPH
# =========================
G = nx.DiGraph()

# -------------------------
# CLASSES
# -------------------------
classes = set()

# -------------------------
# INSTANCE -> CLASS
# -------------------------
instance_of = []

# -------------------------
# SUBCLASS RELATIONS
# -------------------------
subclass_of = []

# -------------------------
# SEMANTIC RELATIONS
# -------------------------
semantic_edges = []

for s, p, o in g:

    p_label = get_label(p)

    # -------------------------
    # rdf:type
    # -------------------------
    if p == RDF.type:

        o_name = get_label(o)
        s_name = get_label(s)

        if o_name == "owl#Class":
            classes.add(s_name)

        else:
            instance_of.append((s_name, o_name))

    # -------------------------
    # subclass hierarchy
    # -------------------------
    elif p == RDFS.subClassOf:

        subclass_of.append(
            (get_label(s), get_label(o))
        )

    # -------------------------
    # semantic relations
    # -------------------------
    else:

        rel = get_label(p)

        if rel in IMPORTANT:
            semantic_edges.append(
                (
                    get_label(s),
                    get_label(o),
                    rel
                )
            )

for child, parent in subclass_of:
    G.add_edge(child, parent, relation="subClassOf")
for inst, cls in instance_of:
    G.add_edge(inst, cls, relation="instanceOf")
for s, o, rel in semantic_edges:
    G.add_edge(s, o, relation=rel)

print("\n--- GRAPH STATS ---")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# =========================
# 5. PROJECTS
# =========================
PROJECTS = sorted([
    inst
    for inst, cls in instance_of
    if cls == "Project"
])

PROJECTS = [p for p in PROJECTS if p in G]

print("\nProjects:", PROJECTS)

# ====================================================
# 5.1 ENTITY TYPES
# ====================================================
from collections import defaultdict

BAD_TYPES = {
    "owl#NamedIndividual",
    "owl#Thing",
    "owl#Class",
    "owl#ObjectProperty",
    "owl#Ontology"
}

ENTITY_TYPES = defaultdict(set)

for s, p, o in g:

    if str(p) == str(RDF.type):

        entity = get_label(s)
        entity_type = get_label(o)

        ENTITY_TYPES[entity].add(entity_type)

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
def clean_feature_type(types):

    if not types:
        return "Unknown"

    filtered = {
        t for t in types
        if not t.startswith("owl#")
    }

    if not filtered:
        return "Unknown"

    return sorted(filtered)[0]


def add_hierarchy_path(H, project, relation, feature):

    current = relation
    chain = []

    # sobe na hierarquia
    while current is not None:
        chain.append(current)
        current = PARENT_MAP.get(current)

    chain = list(reversed(chain))

    prev = project

    # cria cadeia hierárquica
    for node in chain:

        H.add_node(node, kind="hierarchy")

        if not H.has_edge(prev, node):
            H.add_edge(prev, node)

        prev = node

    # feature final
    H.add_node(feature, kind="feature")

    if not H.has_edge(prev, feature):
        H.add_edge(prev, feature)
    
def build_visual_subgraph(project):

    H = nx.Graph()

    H.add_node(project, kind="project")

    for u, v, d in G.edges(data=True):

        rel = d["relation"]

        # -------------------------
        # apenas relações do projeto
        # -------------------------
        if u == project:
            feature = v

        elif v == project:
            feature = u

        else:
            continue

        # -------------------------
        # ignora relações semânticas inválidas
        # -------------------------
        if rel not in PARENT_MAP:
            continue

        feature_types = ENTITY_TYPES.get(feature, set())

        # remove propriedades OWL
        if "owl#ObjectProperty" in feature_types:
            continue

        # remove classes OWL
        if "owl#Class" in feature_types:
            continue

        # -------------------------
        # adiciona caminho hierárquico
        # -------------------------
        add_hierarchy_path(
            H,
            project,
            rel,
            feature
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
        seed=42,
        k=2.5,          # aumenta distância entre nós
        iterations=200  # layout mais estável
    )   

    # ---------------------------------
    # NODE COLORS
    # ---------------------------------
    color_map = []

    for node, data in graph.nodes(data=True):

        kind = data.get("kind")

        if kind == "project":
            color_map.append("#ff6b6b")  # vermelho

        elif kind == "hierarchy":
            color_map.append("#4dabf7")  # azul

        elif kind == "feature":
            color_map.append("#69db7c")  # verde

        else:
            color_map.append("#ced4da")  # cinza fallback

    # ---------------------------------
    # DRAW GRAPH
    # ---------------------------------
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=500,
        node_color=color_map,
        font_size=8,
        edge_color="#adb5bd"
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

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"[SAVED] {path}")

    plt.show()

    plt.close()

for p in PROJECTS:
    draw_graph(
        visual_graphs[p],
        p
    )

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

    #Location
    # Deadlines, prazos (faixas de tempo)
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


TYPE_GROUPS = {
    "Architecture",
    "CodeSmell",
    "Database",
    "DevelopmentPractice",
    "Documentation",
    "Process",
    "ProductDomain",
    "ProgrammingLanguage",
    "Framework",
    "TeamSizeCategory",
    "TestCoverageLevel",
    "Tools"
}

# =========================
# FEATURE GRAPH
# =========================
ROOT_RELATIONS = {
    "hasArchitecturalAspects",
    "hasOrganizationalAspects",
    "hasQualityAspects",
    "hasTechnicalAspects"
}

def build_feature_graph(project):

    H = nx.Graph()

    project = normalize_node(project)

    H.add_node(project, kind="project")

    for u, v, d in G.edges(data=True):

        u = normalize_node(u)
        v = normalize_node(v)

        rel = d["relation"]

        # ---------------------------------
        # detecta feature do projeto
        # ---------------------------------
        if u == project:
            feature = v

        elif v == project:
            feature = u

        else:
            continue

        # ---------------------------------
        # relação precisa existir
        # ---------------------------------
        if rel not in PARENT_MAP:
            continue

        # ---------------------------------
        # tipos da feature
        # ---------------------------------
        feature_types = ENTITY_TYPES.get(feature, set())

        filtered_types = [
            t for t in feature_types
            if t not in BAD_TYPES
        ]

        if not filtered_types:
            continue

        # ---------------------------------
        # ROOT + CATEGORY
        # ---------------------------------
        category_relation = PARENT_MAP.get(rel)

        root_relation = None

        current = rel

        while current is not None:

            parent = PARENT_MAP.get(current)

            if parent in ROOT_RELATIONS:
                root_relation = parent
                break

            current = parent

        # fallback
        if root_relation is None:

            if rel in ROOT_RELATIONS:
                root_relation = rel
            else:
                root_relation = "UNKNOWN_ROOT"

        root_node = f"ROOT::{root_relation}"

        if category_relation is None:
            category_relation = rel

        category_node = f"CATEGORY::{category_relation}"

        subtype_node = f"SUBTYPE::{rel}"

        # ---------------------------------
        # múltiplos tipos
        # ---------------------------------
        for feature_type in filtered_types:

            type_node = f"TYPE::{feature_type}"

            # ---------------------------------
            # adiciona nós
            # ---------------------------------
            H.add_node(root_node, kind="root")

            H.add_node(
                category_node,
                kind="category"
            )

            H.add_node(
                subtype_node,
                kind="subtype"
            )

            H.add_node(
                type_node,
                kind="type"
            )

            H.add_node(
                feature,
                kind="feature"
            )

            # ---------------------------------
            # hierarquia
            # ---------------------------------
            H.add_edge(project, root_node)

            H.add_edge(root_node, category_node)

            H.add_edge(category_node, subtype_node)

            H.add_edge(subtype_node, type_node)

            H.add_edge(type_node, feature)

    return H

RELATION_WEIGHTS = {

    # =========================================================
    # WEIGHTING PHILOSOPHY
    # =========================================================
    #
    # These weights are NOT intended to measure software quality.
    #
    # The goal is to improve cosine similarity between projects
    # that tend to evolve similarly and consequently generate
    # similar emergent code smells over time.
    #
    # Main assumption:
    #
    #   Code smells emerge primarily from:
    #   - project growth
    #   - architectural expansion
    #   - coordination complexity
    #   - scalability pressure
    #   - distributed systems evolution
    #   - organizational entropy
    #   - temporal pressure
    #
    # Therefore:
    #
    # HIGH WEIGHTS (8-10):
    #   Assigned to relations strongly associated with:
    #   - structural growth
    #   - architectural complexity
    #   - long-term maintenance pressure
    #   - scaling challenges
    #   - socio-technical coordination complexity
    #
    # Examples:
    #   - architecture
    #   - scalability
    #   - infrastructure
    #   - modularization
    #   - deployment frequency
    #   - team size
    #   - turnover
    #   - project age
    #
    #
    # MEDIUM WEIGHTS (4-7):
    #   Assigned to technical identity relations.
    #
    # These relations influence implementation style,
    # but alone are usually insufficient to explain
    # emergent smells caused by project evolution.
    #
    # Examples:
    #   - backend
    #   - framework
    #   - databases
    #   - CI/CD
    #   - messaging
    #
    #
    # LOW WEIGHTS (1-3):
    #   Assigned to highly specific or operational details.
    #
    # These relations introduce vector noise in cosine similarity
    # and should not dominate structural similarity.
    #
    # Example:
    #   Two architecturally similar systems should not become
    #   dissimilar merely because one uses VSCode and another IntelliJ.
    #
    # Examples:
    #   - IDE
    #   - code editor
    #   - documentation language
    #   - communication tools
    #
    #
    # HIERARCHICAL RULE:
    #
    # More abstract structural relations receive higher weights
    # than their specialized descendants.
    #
    # Example:
    #
    #   hasInfrastructure            -> high
    #   hasContainerization          -> high
    #   hasContainerizationTools     -> lower
    #
    # Reason:
    #   Distributed/containerized architecture strongly affects
    #   system evolution and smell emergence.
    #
    #   However, the specific tool (Docker/Kubernetes/etc)
    #   should not disproportionately dominate similarity.
    #
    #
    # TEMPORAL AND ORGANIZATIONAL EMPHASIS:
    #
    # Project age, deadlines, deployment frequency,
    # team expansion and turnover receive very high weights
    # because code smells accumulate progressively as systems
    # evolve under continuous delivery and organizational growth.
    #
    #
    # IMPORTANT:
    #
    # These weights are optimized for:
    #   - emergent similarity
    #   - evolutionary similarity
    #   - socio-technical similarity
    #
    # NOT:
    #   - technology stack matching
    #   - code quality scoring
    #   - static architectural evaluation
    #
    # =========================================================


    # =========================================================
    # ARCHITECTURAL ASPECTS
    # =========================================================

    "hasArchitecturalAspects": 9,
    "Modularization": 10,
    "Persistence": 6,
    "Resilience": 8,
    "Security": 7,
    "hasApiIntegrationPattern": 9,
    "hasArchitecturalObservability": 8,
    "hasArchitecturalStyle": 10,
    "hasDeploymentAndOperation": 9,
    "hasDesignPatterns": 7,
    "hasGovernance": 9,
    "hasInternalOrganization": 8,

    # =========================================================
    # ORGANIZATIONAL ASPECTS
    # =========================================================

    "hasOrganizationalAspects": 9,
    "hasBudget": 5,

    "hasCommunicationMode": 6,
    "hasCommunicationModeDescription": 2,
    "hasDocumentationLanguage": 2,
    "hasDocumentationLanguageName": 1,
    "hasPrimaryLanguage": 3,
    "hasPrimaryLanguageName": 1,
    "usesCommunicationTools": 2,

    "hasLocation": 4,

    "hasOrganizationalStructure": 8,
    "hasWorkModality": 5,

    "hasProcess": 9,

    "hasAgileMethod": 7,
    "hasAgileCulture": 8,

    "hasDevOpsPractice": 9,
    "hasDevOpsCulture": 9,

    "hasTraditionalMethod": 5,
    "hasTraditionalCulture": 5,

    "hasProductDomain": 6,

    "hasEmployeeTurnover": 10,
    "hasTeamSeniority": 8,
    "hasTeamSize": 10,

    "hasTemporalStructure": 10,
    "hasDeadlines": 10,

    "hasFrequency": 8,
    "hasDeploymentFrequency": 10,
    "hasMeetingFrequency": 4,

    "hasProjectAge": 10,
    "hasProjectStage": 9,
    "hasSprintDuration": 7,

    # =========================================================
    # QUALITY ASPECTS
    # =========================================================

    "hasQualityAspects": 9,

    "hasDocumentation": 8,
    "DocFormats": 3,
    "DocTypes": 4,
    "hasApiDoc": 6,
    "hasDiagrams": 6,
    "hasDocVersioning": 7,

    "hasMonitoring": 8,
    "hasQualityStrategies": 9,
    "hasReliability": 8,
    "hasSoftwareSecurity": 8,

    "hasTesting": 9,
    "hasTestingLevels": 7,
    "hasTestingTools": 4,

    # =========================================================
    # TECHNICAL ASPECTS
    # =========================================================

    "hasTechnicalAspects": 8,

    "hasDatabase": 7,
    "hasRelational": 4,
    "hasNonRelational": 5,

    "hasDevelopmentTools": 5,
    "hasBuildSystem": 5,
    "hasCI_CD": 8,
    "hasCache": 6,
    "hasCodeEditor": 1,
    "hasCodeQuality": 8,
    "hasIDE": 1,
    "hasMessaging": 7,
    "hasVersioning": 6,

    "hasInfrastructure": 10,
    "hasCloud": 7,

    "hasContainerization": 9,
    "hasContainerizationTools": 4,
    "hasContainerOrchestration": 8,

    "hasEnvironment": 6,
    "hasIAC": 8,
    "hasNetwork": 7,
    "hasObservability": 9,
    "hasScalability": 10,

    "hasProgrammingLanguage": 5,

    "hasAI": 6,
    "hasBackend": 6,

    "hasDependencyManager": 4,

    "hasFramework": 6,
    "hasAIFramework": 4,
    "hasBackendFramework": 5,
    "hasFrontendFramework": 4,
    "hasMobileFramework": 4,

    "hasFrontend": 5,
    "hasMobile": 4,
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
from sklearn.metrics import jaccard_score

def feature_jaccard(project_a, project_b):

    v1 = feature_matrix_binary.loc[project_a].values
    v2 = feature_matrix_binary.loc[project_b].values

    return jaccard_score(v1, v2)

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
from numpy import amax, trace
from numpy import square
from math import sqrt
import random

# ---------------------------------
# BUILD ADJACENCY MATRIX
# ---------------------------------
def graph_to_adjmatrix(g, global_nodes):

    canonical_nodes = [
        canonicalize_node(n)
        for n in global_nodes
    ]

    idx = {
        node: i
        for i, node in enumerate(canonical_nodes)
    }


    n = len(global_nodes)

    A = dok_matrix((n, n), dtype=float)

    for u, v in g.edges():

        i = idx[canonicalize_node(u)]
        j = idx[canonicalize_node(v)]

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

        while amax(M.toarray()) > 10**(-9) and power < 10:

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

    import igraph as ig

    g = ig.Graph.Adjacency(
        (A1.toarray() > 0).tolist()
    )

    partitions = g.community_infomap()

    E = {}

    for i, community in enumerate(partitions):

        vec = np.zeros(size)

        for node in community:
            vec[node] = 1.0

        E[i] = vec.reshape(-1, 1)


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
    # if nx.is_isomorphic(g1, g2):
    #     return 1.0
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
    j = feature_jaccard(a, b)

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
            df_j.loc[i, j] = feature_jaccard(i, j)
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
# 13. PRINT ALL GRAPHS (DEBUG)
# =========================

# print("\n=========================")
# print("VISUAL GRAPHS")
# print("=========================")

# for name, graph in visual_graphs.items():

#     print(f"\n--- {name} ---")

#     print("Nodes:")
#     print(list(graph.nodes()))

#     print("\nEdges:")
#     for u, v, d in graph.edges(data=True):
#         print(f"{u} -- {v} | relation={d.get('relation')}")

print("\n=========================")
print("SEMANTIC GRAPHS")
print("=========================")

for name, graph in semantic_graphs.items():

    print(f"\n--- {name} ---")

    print("Nodes:")
    print("Quantity:", len(graph.nodes()))
    print(list(graph.nodes()))

    print("\nEdges:")
    print("Quantity:", len(graph.edges()))
    for u, v in graph.edges():
        print(f"{u} -- {v}")
