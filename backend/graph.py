import json
from neo4j import GraphDatabase
try:
    from langchain_neo4j import Neo4jGraph
except ImportError:
    from langchain_community.graphs import Neo4jGraph

class ProjectGraphBuilder:
    def __init__(self, neo4j_url="bolt://localhost:7687", username="neo4j", password="test1234"):
        """Initialize Neo4j connection"""
        self.graph = Neo4jGraph(
            url=neo4j_url,
            username=username,
            password=password,
            refresh_schema=True
        )
    
    def clear_database(self):
        """Clear all nodes and relationships from the database"""
        query = "MATCH (n) DETACH DELETE n"
        self.graph.query(query)
        print("Database cleared successfully!")
    
    def create_constraints(self):
        """Create constraints for better performance and data integrity"""
        constraints = [
            "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT pain_point_name IF NOT EXISTS FOR (pp:PainPoint) REQUIRE pp.name IS UNIQUE",
            "CREATE CONSTRAINT capability_name IF NOT EXISTS FOR (c:Capability) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT industry_name IF NOT EXISTS FOR (i:Industry) REQUIRE i.name IS UNIQUE",
            "CREATE CONSTRAINT regulation_name IF NOT EXISTS FOR (r:Regulation) REQUIRE r.name IS UNIQUE",
            "CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                self.graph.query(constraint)
                print(f"✓ Constraint created: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
            except Exception as e:
                print(f"⚠ Constraint may already exist: {e}")
    
    def extract_technologies_from_summary(self, summary):
        """Extract technology keywords from summary"""
        tech_keywords = [
            "AI", "GenAI", "LLM", "Machine Learning", "ML", "Deep Learning",
            "Natural Language Processing", "NLP", "Computer Vision", "CV",
            "Python", "JavaScript", "React", "Node.js", "Azure", "AWS",
            "Docker", "Kubernetes", "API", "REST", "GraphQL", "SQL",
            "NoSQL", "MongoDB", "PostgreSQL", "Redis", "Elasticsearch",
            "Microservices", "Serverless", "Cloud", "IoT", "Blockchain",
            "Chatbot", "Voice AI", "Recommendation Engine", "Analytics",
            "Data Science", "Big Data", "Real-time", "Streaming",
            "Twilio", "GPT", "OpenAI", "Anthropic", "Claude", "Excel",
            "CSV", "Dashboard", "Simulation", "Telemetry", "Forecasting"
        ]
        
        found_techs = []
        summary_lower = summary.lower()
        
        for tech in tech_keywords:
            if tech.lower() in summary_lower:
                found_techs.append(tech)
        
        return found_techs
    
    def categorize_into_domains(self, industries, capabilities, pain_points):
        """Categorize project into broader domains"""
        domains = []
        all_text = " ".join(industries + capabilities + pain_points)
        
        # AI/ML Domain
        ai_keywords = ["AI", "GenAI", "LLM", "Machine Learning", "Natural Language", "Recommendation", "Analytics"]
        if any(keyword in all_text for keyword in ai_keywords):
            domains.append("Artificial Intelligence")
        
        # Security Domain
        security_keywords = ["Security", "Cybersecurity", "Injection", "Firewall", "Compliance", "Privacy"]
        if any(keyword in all_text for keyword in security_keywords):
            domains.append("Security")
        
        # Business Operations Domain
        business_keywords = ["Sales", "HR", "Human Resources", "Customer", "E-commerce", "Retail", "Operations"]
        if any(keyword in all_text for keyword in business_keywords):
            domains.append("Business Operations")
        
        # Data & Analytics Domain
        data_keywords = ["Data", "Analytics", "CSV", "Query", "Database", "Analysis", "Reporting"]
        if any(keyword in all_text for keyword in data_keywords):
            domains.append("Data & Analytics")
        
        # Manufacturing/Industrial Domain
        manufacturing_keywords = ["Manufacturing", "Industrial", "IoT", "Automation", "Factory", "Telemetry"]
        if any(keyword in all_text for keyword in manufacturing_keywords):
            domains.append("Manufacturing & Industrial")
        
        # Legal/Compliance Domain
        legal_keywords = ["Legal", "Compliance", "Contract", "Regulation", "GDPR", "HIPAA"]
        if any(keyword in all_text for keyword in legal_keywords):
            domains.append("Legal & Compliance")
        
        return domains if domains else ["General"]
    
    def build_graph_from_json(self, data):
        """Build comprehensive graph from JSON data"""
        print("Building graph from JSON data...")
        
        for i, project in enumerate(data, 1):
            print(f"Processing project {i}/{len(data)}: {project['name']}")
            
            # Extract technologies from summary
            technologies = self.extract_technologies_from_summary(project['summary'])
            
            # Categorize into domains
            domains = self.categorize_into_domains(
                project['industries'], 
                project['capabilities'], 
                project['pain_points']
            )
            
            # Create Project node
            project_query = """
            MERGE (p:Project {id: $id})
            SET p.name = $name,
                p.summary = $summary,
                p.url = $url,
                p.deployment_status = CASE WHEN $url = "Not Deployed" THEN "Not Deployed" ELSE "Deployed" END
            """
            
            self.graph.query(project_query, {
                'id': project['id'],
                'name': project['name'],
                'summary': project['summary'],
                'url': project['url']
            })
            
            # Create and connect Pain Points
            for pain_point in project['pain_points']:
                pain_point_query = """
                MERGE (pp:PainPoint {name: $pain_point})
                WITH pp
                MATCH (p:Project {id: $project_id})
                MERGE (p)-[:ADDRESSES]->(pp)
                """
                self.graph.query(pain_point_query, {
                    'pain_point': pain_point,
                    'project_id': project['id']
                })
            
            # Create and connect Capabilities
            for capability in project['capabilities']:
                capability_query = """
                MERGE (c:Capability {name: $capability})
                WITH c
                MATCH (p:Project {id: $project_id})
                MERGE (p)-[:HAS_CAPABILITY]->(c)
                """
                self.graph.query(capability_query, {
                    'capability': capability,
                    'project_id': project['id']
                })
            
            # Create and connect Industries
            for industry in project['industries']:
                industry_query = """
                MERGE (i:Industry {name: $industry})
                WITH i
                MATCH (p:Project {id: $project_id})
                MERGE (p)-[:TARGETS]->(i)
                """
                self.graph.query(industry_query, {
                    'industry': industry,
                    'project_id': project['id']
                })
            
            # Create and connect Regulations
            for regulation in project['regulations']:
                if regulation != "Not Applicable":
                    regulation_query = """
                    MERGE (r:Regulation {name: $regulation})
                    WITH r
                    MATCH (p:Project {id: $project_id})
                    MERGE (p)-[:COMPLIES_WITH]->(r)
                    """
                    self.graph.query(regulation_query, {
                        'regulation': regulation,
                        'project_id': project['id']
                    })
            
            # Create and connect Technologies
            for technology in technologies:
                tech_query = """
                MERGE (t:Technology {name: $technology})
                WITH t
                MATCH (p:Project {id: $project_id})
                MERGE (p)-[:USES_TECHNOLOGY]->(t)
                """
                self.graph.query(tech_query, {
                    'technology': technology,
                    'project_id': project['id']
                })
            
            # Create and connect Domains
            for domain in domains:
                domain_query = """
                MERGE (d:Domain {name: $domain})
                WITH d
                MATCH (p:Project {id: $project_id})
                MERGE (p)-[:BELONGS_TO]->(d)
                """
                self.graph.query(domain_query, {
                    'domain': domain,
                    'project_id': project['id']
                })
    
    def create_similarity_relationships(self):
        """Create relationships between projects based on shared attributes"""
        print("Creating similarity relationships...")
        
        # Projects sharing the same pain points
        shared_pain_points_query = """
        MATCH (p1:Project)-[:ADDRESSES]->(pp:PainPoint)<-[:ADDRESSES]-(p2:Project)
        WHERE p1.id < p2.id
        WITH p1, p2, COUNT(pp) as shared_pain_points
        WHERE shared_pain_points > 0
        MERGE (p1)-[r:SHARES_PAIN_POINTS]-(p2)
        SET r.count = shared_pain_points
        """
        self.graph.query(shared_pain_points_query)
        
        # Projects sharing capabilities
        shared_capabilities_query = """
        MATCH (p1:Project)-[:HAS_CAPABILITY]->(c:Capability)<-[:HAS_CAPABILITY]-(p2:Project)
        WHERE p1.id < p2.id
        WITH p1, p2, COUNT(c) as shared_capabilities
        WHERE shared_capabilities > 0
        MERGE (p1)-[r:SHARES_CAPABILITIES]-(p2)
        SET r.count = shared_capabilities
        """
        self.graph.query(shared_capabilities_query)
        
        # Projects targeting same industries
        shared_industries_query = """
        MATCH (p1:Project)-[:TARGETS]->(i:Industry)<-[:TARGETS]-(p2:Project)
        WHERE p1.id < p2.id
        WITH p1, p2, COUNT(i) as shared_industries
        WHERE shared_industries > 0
        MERGE (p1)-[r:SHARES_INDUSTRIES]-(p2)
        SET r.count = shared_industries
        """
        self.graph.query(shared_industries_query)
        
        # Projects using same technologies
        shared_tech_query = """
        MATCH (p1:Project)-[:USES_TECHNOLOGY]->(t:Technology)<-[:USES_TECHNOLOGY]-(p2:Project)
        WHERE p1.id < p2.id
        WITH p1, p2, COUNT(t) as shared_technologies
        WHERE shared_technologies > 0
        MERGE (p1)-[r:SHARES_TECHNOLOGIES]-(p2)
        SET r.count = shared_technologies
        """
        self.graph.query(shared_tech_query)
        
        # Projects in same domain
        shared_domain_query = """
        MATCH (p1:Project)-[:BELONGS_TO]->(d:Domain)<-[:BELONGS_TO]-(p2:Project)
        WHERE p1.id < p2.id
        WITH p1, p2, COUNT(d) as shared_domains
        WHERE shared_domains > 0
        MERGE (p1)-[r:SHARES_DOMAINS]-(p2)
        SET r.count = shared_domains
        """
        self.graph.query(shared_domain_query)
    
    def create_aggregate_relationships(self):
        """Create high-level aggregate relationships"""
        print("Creating aggregate relationships...")
        
        # Most common pain points across all projects
        common_pain_points_query = """
        MATCH (pp:PainPoint)<-[:ADDRESSES]-(p:Project)
        WITH pp, COUNT(p) as project_count
        WHERE project_count > 1
        SET pp.popularity = project_count
        """
        self.graph.query(common_pain_points_query)
        
        # Most common capabilities
        common_capabilities_query = """
        MATCH (c:Capability)<-[:HAS_CAPABILITY]-(p:Project)
        WITH c, COUNT(p) as project_count
        WHERE project_count > 1
        SET c.popularity = project_count
        """
        self.graph.query(common_capabilities_query)
        
        # Most targeted industries
        common_industries_query = """
        MATCH (i:Industry)<-[:TARGETS]-(p:Project)
        WITH i, COUNT(p) as project_count
        SET i.popularity = project_count
        """
        self.graph.query(common_industries_query)
    
    def get_graph_statistics(self):
        """Get basic statistics about the graph"""
        stats_queries = {
            "Total Projects": "MATCH (p:Project) RETURN count(p) as count",
            "Total Pain Points": "MATCH (pp:PainPoint) RETURN count(pp) as count",
            "Total Capabilities": "MATCH (c:Capability) RETURN count(c) as count",
            "Total Industries": "MATCH (i:Industry) RETURN count(i) as count",
            "Total Technologies": "MATCH (t:Technology) RETURN count(t) as count",
            "Total Domains": "MATCH (d:Domain) RETURN count(d) as count",
            "Total Regulations": "MATCH (r:Regulation) RETURN count(r) as count",
            "Shared Pain Points Relationships": "MATCH ()-[r:SHARES_PAIN_POINTS]-() RETURN count(r) as count",
            "Shared Capabilities Relationships": "MATCH ()-[r:SHARES_CAPABILITIES]-() RETURN count(r) as count",
            "Shared Industries Relationships": "MATCH ()-[r:SHARES_INDUSTRIES]-() RETURN count(r) as count",
            "Shared Technologies Relationships": "MATCH ()-[r:SHARES_TECHNOLOGIES]-() RETURN count(r) as count"
        }
        
        print("\n" + "="*50)
        print("📊 GRAPH STATISTICS")
        print("="*50)
        for stat_name, query in stats_queries.items():
            result = self.graph.query(query)
            count = result[0]['count'] if result else 0
            print(f"{stat_name}: {count}")
    
    def show_project_similarities(self):
        """Show project similarities"""
        query = """
        MATCH (p1:Project)-[r:SHARES_PAIN_POINTS|SHARES_CAPABILITIES|SHARES_INDUSTRIES|SHARES_TECHNOLOGIES|SHARES_DOMAINS]-(p2:Project)
        WHERE p1.id < p2.id
        RETURN p1.name as project1, p2.name as project2, type(r) as relationship_type, r.count as similarity_count
        ORDER BY similarity_count DESC
        LIMIT 10
        """
        
        results = self.graph.query(query)
        
        print("\n" + "="*50)
        print("🔗 TOP PROJECT SIMILARITIES")
        print("="*50)
        
        for result in results:
            print(f"{result['project1']} ↔ {result['project2']}")
            print(f"   Relationship: {result['relationship_type']} (Score: {result['similarity_count']})")
            print()
    
    def show_most_common_elements(self):
        """Show most common elements across projects"""
        print("\n" + "="*50)
        print("📈 MOST COMMON ELEMENTS")
        print("="*50)
        
        # Most common pain points
        pain_points_query = """
        MATCH (pp:PainPoint)<-[:ADDRESSES]-(p:Project)
        WITH pp, COUNT(p) as frequency
        WHERE frequency > 1
        RETURN pp.name as name, frequency
        ORDER BY frequency DESC
        LIMIT 5
        """
        
        results = self.graph.query(pain_points_query)
        print("🎯 Most Common Pain Points:")
        for result in results:
            print(f"   • {result['name']} ({result['frequency']} projects)")
        
        # Most common capabilities
        capabilities_query = """
        MATCH (c:Capability)<-[:HAS_CAPABILITY]-(p:Project)
        WITH c, COUNT(p) as frequency
        WHERE frequency > 1
        RETURN c.name as name, frequency
        ORDER BY frequency DESC
        LIMIT 5
        """
        
        results = self.graph.query(capabilities_query)
        print("\n⚡ Most Common Capabilities:")
        for result in results:
            print(f"   • {result['name']} ({result['frequency']} projects)")
        
        # Most targeted industries
        industries_query = """
        MATCH (i:Industry)<-[:TARGETS]-(p:Project)
        WITH i, COUNT(p) as frequency
        RETURN i.name as name, frequency
        ORDER BY frequency DESC
        LIMIT 5
        """
        
        results = self.graph.query(industries_query)
        print("\n🏢 Most Targeted Industries:")
        for result in results:
            print(f"   • {result['name']} ({result['frequency']} projects)")
    
    def build_complete_graph(self, json_data):
        """Build the complete graph from JSON data"""
        print("🚀 Starting Neo4j Graph Knowledge Base construction...")
        
        # Clear existing data
        self.clear_database()
        
        # Create constraints
        self.create_constraints()
        
        # Build graph from JSON
        self.build_graph_from_json(json_data)
        
        # Create similarity relationships
        self.create_similarity_relationships()
        
        # Create aggregate relationships
        self.create_aggregate_relationships()
        
        # Show statistics and insights
        self.get_graph_statistics()
        self.show_project_similarities()
        self.show_most_common_elements()
        
        print("\n" + "="*50)
        print("✅ Graph Knowledge Base built successfully!")
        print("="*50)
        print("You can now:")
        print("• Query the graph using Cypher queries")
        print("• Use the QA interface with OpenAI for natural language queries")
        print("• Explore relationships between projects in Neo4j Browser")
        print("• Access the graph at: http://localhost:7474")


# Your JSON data
projects_data = [
    {
        "id": "cybersecure-genai",
        "name": "CyberSecure GenAI",
        "summary": "A secure GenAI agent layer that prevents malicious prompt injections, SQL injections, and unsafe agent actions by validating user intent before execution.",
        "pain_points": [
            "prompt injection attacks",
            "SQL injection via LLM agents",
            "LLM-based tool misuse"
        ],
        "capabilities": [
            "AI firewall",
            "agent execution guardrails",
            "intent validation",
            "payload inspection"
        ],
        "industries": [
            "Cybersecurity",
            "AI Infrastructure",
            "Enterprise SaaS"
        ],
        "regulations": [
            "OWASP Top 10",
            "SOC 2 Compliance"
        ],
        "url": "https://cyber-securegenai.azurewebsites.net/"
    },
    {
        "id": "eddison-motor",
        "name": "Eddison Motor AI Assistant",
        "summary": "A smart sales chatbot that understands customer needs and recommends the right products while remembering preferences and interactions over time.",
        "pain_points": [
            "inefficient product discovery",
            "low customer retention",
            "generic recommendations"
        ],
        "capabilities": [
            "conversational AI",
            "product recommendation",
            "preference memory",
            "customer intent understanding"
        ],
        "industries": [
            "E-commerce",
            "Retail",
            "Automotive"
        ],
        "regulations": ["Not Applicable"],
        "url": "http://automotive-ai-studio.azurewebsites.net/"
    },
    {
        "id": "talk-to-data",
        "name": "Talk to Data",
        "summary": "An AI platform that lets users upload multiple CSV files and chat with the data. A Python-based engine profiles each column—even if headers are missing—infers types, detects relationships, and stores the structure. At query time, it uses cross-CSV logic and deterministic Python rules to return accurate answers.",
        "pain_points": [
            "slow data analysis",
            "non-technical users unable to query data",
            "messy or unlabeled columns",
            "multiple dataset confusion"
        ],
        "capabilities": [
            "auto column profiling & typing",
            "schema inference for unlabeled data",
            "multi-file CSV reasoning",
            "Python-driven deterministic querying",
            "cross-dataframe QA"
        ],
        "industries": [
            "Finance",
            "Operations",
            "Audit",
            "Data Analytics"
        ],
        "regulations": [
            "Data Quality Standards"
        ],
        "url": "https://app.irame.ai/"
    },
    {
        "id": "axis-ai-sales-caller",
        "name": "AXIS - AI Sales Call Orchestrator",
        "summary": "A tool that lets you define a sales workflow, which is then used by a voice AI assistant (via Twilio) to call clients, follow your flow, and transcribe conversations for further analysis.",
        "pain_points": [
            "manual sales outreach",
            "lack of call analytics",
            "inconsistent customer experience"
        ],
        "capabilities": [
            "AI voice calling",
            "workflow-based conversation",
            "call transcription",
            "post-call analytics"
        ],
        "industries": [
            "Sales",
            "Call Centers",
            "Customer Success"
        ],
        "regulations": [
            "Telemarketing Compliance",
            "Data Privacy in Voice AI"
        ],
        "url": "https://axis-assitant.web.app/"
    },
    {
        "id": "hr-ai-studio",
        "name": "HR AI Studio",
        "summary": "HR AI Studio is an innovative platform designed to revolutionize Human Resources management using advanced artificial intelligence. Enhance your HR efficiency, candidate engagement, and streamline hiring processes effortlessly.",
        "pain_points": [
            "manual resume screening",
            "hiring bias",
            "low candidate engagement",
            "inefficient job description creation",
            "misaligned job-candidate matching"
        ],
        "capabilities": [
            "resume parsing",
            "job description generation",
            "AI-powered interviews",
            "candidate-job matching",
            "automated candidate evaluation"
        ],
        "industries": [
            "Human Resources",
            "Recruitment",
            "HR Tech"
        ],
        "regulations": [
            "EEOC compliance",
            "Diversity and Inclusion Standards"
        ],
        "url": "https://hr-ai-studio.azurewebsites.net/"
    },
    {
        "id": "contracts-ai-studio",
        "name": "Contracts AI Studio",
        "summary": "Contracts AI Studio is a Generative AI-powered web app designed to simplify and modernize contract management. It supports contract summarization, comparison, redaction, generation, clause extraction, and intelligent querying across a contract repository.",
        "pain_points": [
            "manual contract review",
            "version control issues",
            "data redaction risk",
            "slow contract drafting",
            "non-standard clause detection",
            "difficulty querying past contracts"
        ],
        "capabilities": [
            "contract summarization",
            "AI-based contract comparison",
            "PII and sensitive data redaction",
            "contract generation with templates",
            "clause redlining and benchmarking",
            "tag and clause extraction",
            "semantic contract search"
        ],
        "industries": [
            "Legal",
            "Compliance",
            "Procurement",
            "Enterprise Operations"
        ],
        "regulations": [
            "GDPR",
            "HIPAA",
            "Contract Lifecycle Management Standards"
        ],
        "url": "https://contracts-ai-studio-g2gag2gkcka0fegb.canadacentral-01.azurewebsites.net/"
    },
    {
        "id": "digital-twin-assistant",
        "name": "Digital Twin Assistant",
        "summary": "A Digital Twin system for smart manufacturing plants that allows users to simulate, monitor, and understand telemetry data using GPT-4-powered natural language interface and predictive ML models.",
        "pain_points": [
            "manual telemetry analysis",
            "lack of intuitive access to IoT data",
            "difficulty predicting anomalies",
            "non-technical users can't interpret raw sensor data"
        ],
        "capabilities": [
            "natural language querying of industrial data",
            "sensor anomaly detection",
            "real-time Excel telemetry processing",
            "ML-based power/vibration forecasting",
            "simulation of factory behavior",
            "dashboard + chat interface for analysis"
        ],
        "industries": [
            "Manufacturing",
            "Industrial Automation",
            "IoT",
            "Smart Factories"
        ],
        "regulations": [
            "ISO 50001 – Energy Management",
            "Industrial IoT Safety Standards"
        ],
        "url": "Not Deployed"
    }
]

# Usage
if __name__ == "__main__":
    # Initialize the graph builder
    builder = ProjectGraphBuilder()
    
    # Build the complete graph
    builder.build_complete_graph(projects_data)
    
    print("\n💡 Sample Cypher Queries to try:")
    print("• MATCH (p:Project)-[:SHARES_PAIN_POINTS]-(p2:Project) RETURN p.name, p2.name")
    print("• MATCH (p:Project)-[:USES_TECHNOLOGY]->(t:Technology) RETURN p.name, t.name")
    print("• MATCH (p:Project)-[:BELONGS_TO]->(d:Domain) RETURN d.name, count(p) as project_count")