from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
import asyncio
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

try:
    from langchain_neo4j import  Neo4jGraph
except ImportError:
    from langchain_community.graphs import Neo4jGraph

load_dotenv()

app = FastAPI(title="Graph Knowledge QA API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    context_limit: Optional[int] = 5

class QuestionResponse(BaseModel):
    question: str
    answer: str
    cypher_query: Optional[str] = None
    raw_results: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[str] = None

class CompanyAnalysisRequest(BaseModel):
    company_name: str
    pain_points: Optional[List[str]] = None  # Allow user to specify pain points
    additional_context: Optional[str] = None

class ConversationState(str, Enum):
    INITIAL = "initial"
    COMPANY_INFO_GATHERED = "company_info_gathered"
    PAIN_POINTS_NEEDED = "pain_points_needed"
    PAIN_POINTS_IDENTIFIED = "pain_points_identified"
    PROJECTS_RECOMMENDED = "projects_recommended"
    PROJECT_SELECTED = "project_selected"
    INTEGRATION_DISCUSSION = "integration_discussion"

class CompanyAnalysisResponse(BaseModel):
    company_name: str
    company_info: Dict[str, Any]
    identified_pain_points: List[str]
    suggested_pain_points: Optional[List[str]] = None  # AI-suggested pain points
    recommended_projects: List[Dict[str, Any]]
    conversation_state: ConversationState
    next_questions: List[str]
    integration_suggestions: Optional[Dict[str, Any]] = None
    message: Optional[str] = None  # For guiding the user

class ProjectInterestRequest(BaseModel):
    company_name: str
    project_id: str
    user_interest: str
    current_systems: Optional[str] = None

class GraphQASystem:
    def __init__(self, neo4j_url="bolt://localhost:7687", username="neo4j", password="test1234"):
        """Initialize Neo4j connection and OpenAI client"""
        self.graph = Neo4jGraph(
            url=neo4j_url,
            username=username,
            password=password,
            refresh_schema=True
        )
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Graph schema for context
        self.schema_context = self._get_schema_context()
    
    def _get_schema_context(self):
        """Get graph schema information for OpenAI context"""
        return """
        GRAPH SCHEMA:
        Node Types:
        - Project: {id, name, summary, url, deployment_status}
        - PainPoint: {name, popularity}
        - Capability: {name, popularity}
        - Industry: {name, popularity}
        - Technology: {name}
        - Domain: {name}
        - Regulation: {name}
        
        Relationships:
        - (Project)-[:ADDRESSES]->(PainPoint)
        - (Project)-[:HAS_CAPABILITY]->(Capability)
        - (Project)-[:TARGETS]->(Industry)
        - (Project)-[:USES_TECHNOLOGY]->(Technology)
        - (Project)-[:BELONGS_TO]->(Domain)
        - (Project)-[:COMPLIES_WITH]->(Regulation)
        - (Project)-[:SHARES_PAIN_POINTS]-(Project)
        - (Project)-[:SHARES_CAPABILITIES]-(Project)
        - (Project)-[:SHARES_INDUSTRIES]-(Project)
        - (Project)-[:SHARES_TECHNOLOGIES]-(Project)
        - (Project)-[:SHARES_DOMAINS]-(Project)
        """
    
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using SERP API"""
        try:
            # SERP API configuration
            serp_api_key = "31b2d407d3035b81ad59b575e9c82ceca4febe813f1b44ae622208813b42517e"
            if not serp_api_key:
                raise HTTPException(status_code=500, detail="SERP API key not configured")
            
            # Search for company information
            search_url = "https://serpapi.com/search"
            search_params = {
                "q": f"{company_name} pain points",
                "api_key": serp_api_key,
                "engine": "google",
                "num": 5
            }
            
            response = requests.get(search_url, params=search_params)
            search_results = response.json()
            
            # Extract relevant information
            company_info = {
                "name": company_name,
                "search_results": search_results.get("organic_results", [])[:3],
                "knowledge_graph": search_results.get("knowledge_graph", {}),
                "answer_box": search_results.get("answer_box", {})
            }
            
            return company_info
            
        except Exception as e:
            print(f"Error searching company info: {e}")
            return {
                "name": company_name,
                "error": str(e),
                "search_results": []
            }
    
    def suggest_pain_points(self, company_info: Dict[str, Any]) -> List[str]:
        """Use OpenAI to suggest potential pain points from company information"""
        
        # Create context from search results
        context = f"Company: {company_info['name']}\n"
        
        if company_info.get("knowledge_graph"):
            kg = company_info["knowledge_graph"]
            context += f"Industry: {kg.get('type', 'Unknown')}\n"
            context += f"Description: {kg.get('description', '')}\n"
        
        for i, result in enumerate(company_info.get("search_results", [])[:3]):
            context += f"\nSearch Result {i+1}:\n"
            context += f"Title: {result.get('title', '')}\n"
            context += f"Snippet: {result.get('snippet', '')}\n"
        
        prompt = f"""
        Based on the following company information, suggest potential business pain points and challenges that this company might face. Focus on operational, technical, and business process pain points.

        {context}

        Common business pain points to consider:
        - Manual processes that could be automated
        - Data analysis and reporting challenges
        - Customer service and engagement issues
        - Security and compliance concerns
        - Sales and marketing inefficiencies
        - HR and recruitment challenges
        - Contract and legal document management
        - Manufacturing and operational inefficiencies
        - Technology integration challenges
        - Data management and analytics
        - Customer relationship management
        - Process automation needs

        Please suggest 8-10 specific pain points that this company likely faces based on their industry and business model. Be specific and actionable.

        Return only a JSON array of pain point strings, like:
        ["pain point 1", "pain point 2", "pain point 3"]
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        
        try:
            # Parse the JSON response
            pain_points = json.loads(response.choices[0].message.content.strip())
            return pain_points
        except json.JSONDecodeError:
            # Fallback: extract pain points from text
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            pain_points = []
            for line in lines:
                if line.strip().startswith(('-', '•', '*')) or line.strip().startswith(tuple('123456789')):
                    cleaned = line.strip().lstrip('-•*123456789. ')
                    if cleaned:
                        pain_points.append(cleaned)
            return pain_points[:10]
    
    def find_matching_projects(self, pain_points: List[str], company_name: str = None) -> List[Dict[str, Any]]:
        """Find projects that address the identified pain points with fallback logic"""
        
        # Create a comprehensive query to find matching projects
        pain_points_str = "', '".join(pain_points)
        
        # Query for projects that address similar pain points
        similarity_query = f"""
        WITH ['{pain_points_str}'] as target_pain_points
        UNWIND target_pain_points as target_pain
        MATCH (pp:PainPoint) 
        WHERE pp.name CONTAINS target_pain OR target_pain CONTAINS pp.name
        WITH pp, target_pain
        MATCH (pp)<-[:ADDRESSES]-(p:Project)
        RETURN p.id, p.name, p.summary, p.url, p.deployment_status,
               pp.name as matched_pain_point, target_pain,
               pp.popularity as pain_point_popularity
        ORDER BY pp.popularity DESC
        """
        
        try:
            results = self.graph.query(similarity_query)
            
            # Also do a broader search using OpenAI for semantic matching
            projects_query = """
            MATCH (p:Project)-[:ADDRESSES]->(pp:PainPoint)
            RETURN p.id, p.name, p.summary, p.url, p.deployment_status,
                   COLLECT(pp.name) as pain_points,
                   [(p)-[:HAS_CAPABILITY]->(c:Capability) | c.name] as capabilities,
                   [(p)-[:TARGETS]->(i:Industry) | i.name] as industries
            """
            
            all_projects = self.graph.query(projects_query)
            
            # Use OpenAI to find the best matches
            matched_projects = self._semantic_project_matching(pain_points, all_projects, company_name)
            
            # If no matches found, provide at least one generic suggestion
            if not matched_projects:
                matched_projects = self._get_fallback_projects(company_name)
            
            return matched_projects
            
        except Exception as e:
            print(f"Error finding matching projects: {e}")
            # Return fallback projects if there's an error
            return self._get_fallback_projects(company_name)
    
    def _get_fallback_projects(self, company_name: str = None) -> List[Dict[str, Any]]:
        """Provide fallback project suggestions when no matches are found"""
        
        # Get some general projects from the database
        fallback_query = """
        MATCH (p:Project)-[:ADDRESSES]->(pp:PainPoint)
        WITH p, COUNT(pp) as pain_point_count
        ORDER BY pain_point_count DESC
        LIMIT 3
        RETURN p.id, p.name, p.summary, p.url, p.deployment_status,
               [(p)-[:ADDRESSES]->(pp2:PainPoint) | pp2.name] as pain_points
        """
        
        try:
            fallback_results = self.graph.query(fallback_query)
            
            fallback_projects = []
            for project in fallback_results:
                fallback_projects.append({
                    "project_id": project["p.id"],
                    "project_name": project["p.name"],
                    "match_score": 30,  # Lower score to indicate it's a fallback
                    "explanation": f"General recommendation - This project addresses common business challenges that many companies like {company_name or 'yours'} face.",
                    "addresses_pain_points": project["pain_points"][:3],
                    "summary": project["p.summary"],
                    "url": project["p.url"],
                    "deployment_status": project["p.deployment_status"]
                })
            
            return fallback_projects
            
        except Exception as e:
            print(f"Error getting fallback projects: {e}")
            # Last resort: return a generic suggestion
            return [{
                "project_id": "generic-automation",
                "project_name": "Business Process Automation",
                "match_score": 20,
                "explanation": "Generic recommendation for business process improvement and automation",
                "addresses_pain_points": ["Manual processes", "Inefficient workflows"],
                "summary": "Automate repetitive business processes to improve efficiency",
                "url": "#",
                "deployment_status": "Available"
            }]
    
    def _semantic_project_matching(self, pain_points: List[str], all_projects: List[Dict], company_name: str = None) -> List[Dict[str, Any]]:
        """Use OpenAI to semantically match pain points with projects"""
        
        projects_context = []
        for project in all_projects:
            project_info = {
                "id": project["p.id"] if "p.id" in project else project.get("id"),
                "name": project["p.name"] if "p.name" in project else project.get("name"),
                "summary": project["p.summary"] if "p.summary" in project else project.get("summary"),
                "pain_points": project["pain_points"],
                "capabilities": project.get("capabilities", []),
                "industries": project.get("industries", []),
                "url": project["p.url"] if "p.url" in project else project.get("url"),
                "deployment_status": project["p.deployment_status"] if "p.deployment_status" in project else project.get("deployment_status")
            }
            projects_context.append(project_info)
        
        prompt = f"""
        I have identified these pain points for {company_name or 'a company'}:
        {json.dumps(pain_points, indent=2)}

        Here are available projects that might help:
        {json.dumps(projects_context, indent=2)}

        Please analyze and return the top 3-5 projects that best match these pain points. 
        IMPORTANT: Even if the match is not perfect, please provide at least 1 project suggestion.
        If direct matches are not available, find projects that could be adapted or are generally useful.

        For each project, provide:
        1. Match score (0-100)
        2. Explanation of why it matches (or could be adapted)
        3. Which specific pain points it addresses (or could potentially address)

        Return as JSON array with this structure:
        [
            {{
                "project_id": "project-id",
                "project_name": "Project Name",
                "match_score": 85,
                "explanation": "Why this project matches...",
                "addresses_pain_points": ["pain point 1", "pain point 2"],
                "summary": "project summary",
                "url": "project url",
                "deployment_status": "status"
            }}
        ]
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        try:
            matched_projects = json.loads(response.choices[0].message.content.strip())
            return matched_projects
        except json.JSONDecodeError:
            # Fallback: return top projects based on simple matching
            return [
                {
                    "project_id": project["id"],
                    "project_name": project["name"],
                    "match_score": 50,
                    "explanation": "Basic match based on available data",
                    "addresses_pain_points": project["pain_points"][:2],
                    "summary": project["summary"],
                    "url": project["url"],
                    "deployment_status": project["deployment_status"]
                }
                for project in projects_context[:3]
            ]
    
    def generate_integration_suggestions(self, company_info: Dict[str, Any], project_info: Dict[str, Any], 
                                       user_interest: str, current_systems: Optional[str] = None) -> Dict[str, Any]:
        """Generate integration suggestions for a specific project"""
        
        prompt = f"""
        Company: {company_info['name']}
        Project: {project_info['project_name']}
        Project Summary: {project_info['summary']}
        User Interest: {user_interest}
        Current Systems: {current_systems or 'Not specified'}

        Based on the user's interest in this project, provide detailed integration suggestions including:

        1. Implementation approach (how to integrate with their existing systems)
        2. Technical requirements and dependencies
        3. Timeline estimates (phases of implementation)
        4. Expected benefits and ROI
        5. Potential challenges and mitigation strategies
        6. Next steps for evaluation/pilot

        Return as JSON with this structure:
        {{
            "implementation_approach": "detailed approach...",
            "technical_requirements": ["requirement 1", "requirement 2"],
            "timeline": {{
                "phase_1": "1-2 weeks: ...",
                "phase_2": "2-4 weeks: ...",
                "phase_3": "4-6 weeks: ..."
            }},
            "expected_benefits": ["benefit 1", "benefit 2"],
            "potential_challenges": ["challenge 1", "challenge 2"],
            "next_steps": ["step 1", "step 2"],
            "pilot_suggestions": "suggestions for pilot implementation..."
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )
        
        try:
            integration_suggestions = json.loads(response.choices[0].message.content.strip())
            return integration_suggestions
        except json.JSONDecodeError:
            return {
                "implementation_approach": "Custom integration approach needed",
                "technical_requirements": ["API integration", "Authentication setup"],
                "timeline": {"phase_1": "2-3 weeks: Initial setup and testing"},
                "expected_benefits": ["Improved efficiency", "Better user experience"],
                "potential_challenges": ["System integration complexity"],
                "next_steps": ["Schedule demo", "Discuss technical requirements"],
                "pilot_suggestions": "Start with a small pilot group to test functionality"
            }
    
    def generate_cypher_query(self, question: str) -> str:
        """Generate Cypher query from natural language question using OpenAI"""
        
        prompt = f"""
        You are a Cypher query generator for a Neo4j graph database containing project information.
        
        {self.schema_context}
        
        EXAMPLES:
        Question: "What projects use AI technology?"
        Cypher: MATCH (p:Project)-[:USES_TECHNOLOGY]->(t:Technology) WHERE t.name CONTAINS 'AI' RETURN p.name, p.summary, t.name
        
        Question: "Which projects share the most pain points?"
        Cypher: MATCH (p1:Project)-[r:SHARES_PAIN_POINTS]-(p2:Project) RETURN p1.name, p2.name, r.count ORDER BY r.count DESC LIMIT 5
        
        Question: "What are the most common capabilities?"
        Cypher: MATCH (c:Capability)<-[:HAS_CAPABILITY]-(p:Project) RETURN c.name, COUNT(p) as frequency ORDER BY frequency DESC LIMIT 10
        
        Question: "Show me projects in the cybersecurity industry"
        Cypher: MATCH (p:Project)-[:TARGETS]->(i:Industry) WHERE i.name CONTAINS 'Cybersecurity' RETURN p.name, p.summary, p.url
        
        Question: "What technologies are used by HR projects?"
        Cypher: MATCH (p:Project)-[:TARGETS]->(i:Industry), (p)-[:USES_TECHNOLOGY]->(t:Technology) WHERE i.name CONTAINS 'HR' OR i.name CONTAINS 'Human Resources' RETURN p.name, t.name
        
        Question: "Find similar projects to CyberSecure GenAI"
        Cypher: MATCH (p1:Project {{name: 'CyberSecure GenAI'}})-[r:SHARES_PAIN_POINTS|SHARES_CAPABILITIES|SHARES_INDUSTRIES|SHARES_TECHNOLOGIES|SHARES_DOMAINS]-(p2:Project) RETURN p1.name, p2.name, type(r) as similarity_type, r.count ORDER BY r.count DESC
        
        IMPORTANT RULES:
        - Return only the Cypher query, no explanation
        - Use CONTAINS for partial string matching when appropriate
        - Always include LIMIT to prevent overwhelming results (default 10)
        - For similarity queries, use the relationship types shown in examples
        - Use proper Neo4j syntax and escaping
        
        Human Question: "{question}"
        
        Cypher Query:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    def execute_cypher_query(self, cypher_query: str) -> List[Dict[str, Any]]:
        """Execute Cypher query and return results"""
        try:
            results = self.graph.query(cypher_query)
            return results
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")
    
    def generate_natural_language_response(self, question: str, cypher_query: str, 
                                         raw_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate natural language response from query results using OpenAI"""
        
        # Limit results for context
        limited_results = raw_results[:10] if raw_results else []
        
        prompt = f"""
        You are a helpful assistant analyzing project data from a graph database.
        
        Human Question: "{question}"
        
        Cypher Query Used: {cypher_query}
        
        Query Results: {json.dumps(limited_results, indent=2)}
        
        Please provide a clear, informative answer to the human's question based on the results.
        
        GUIDELINES:
        - Be conversational and helpful
        - Summarize key insights from the data
        - If no results found, explain what might be searched for instead
        - Include specific project names, technologies, or metrics when relevant
        - Keep response concise but informative
        - If results show relationships or patterns, highlight them
        
        Response:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        # Determine confidence based on results
        confidence = "High" if raw_results else "Low"
        if raw_results and len(raw_results) > 5:
            confidence = "High"
        elif raw_results and len(raw_results) > 2:
            confidence = "Medium"
        
        return {
            "answer": response.choices[0].message.content.strip(),
            "confidence": confidence
        }
    
    def process_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Process a natural language question and return comprehensive response"""
        
        # Generate Cypher query
        cypher_query = self.generate_cypher_query(question)
        
        # Execute query
        raw_results = self.execute_cypher_query(cypher_query)
        
        # Generate natural language response
        response_data = self.generate_natural_language_response(
            question, cypher_query, raw_results
        )
        
        return {
            "question": question,
            "answer": response_data["answer"],
            "cypher_query": cypher_query,
            "raw_results": raw_results[:context_limit],
            "confidence": response_data["confidence"]
        }

# Initialize the QA system
qa_system = GraphQASystem()

# Store conversation sessions (in production, use Redis or database)
conversation_sessions = {}

@app.post("/analyze-company", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Analyze a company and either ask for pain points or use provided ones.
    
    This endpoint:
    1. Searches for company information using SERP API
    2. If pain_points are not provided, suggests potential pain points for user confirmation
    3. If pain_points are provided, finds matching projects from the knowledge graph
    4. Returns recommendations with next steps
    """
    
    if not request.company_name.strip():
        raise HTTPException(status_code=400, detail="Company name cannot be empty")
    
    try:
        # Step 1: Search for company information
        company_info = qa_system.search_company_info(request.company_name)
        
        # Step 2: Handle pain points
        if not request.pain_points:
            # No pain points provided - suggest some and ask user to confirm
            suggested_pain_points = qa_system.suggest_pain_points(company_info)
            
            return CompanyAnalysisResponse(
                company_name=request.company_name,
                company_info=company_info,
                identified_pain_points=[],
                suggested_pain_points=suggested_pain_points,
                recommended_projects=[],
                conversation_state=ConversationState.PAIN_POINTS_NEEDED,
                next_questions=[
                    "Which of these pain points are most relevant to your company?",
                    "Are there any other pain points you'd like to add?",
                    "Please select 3-5 pain points that are most critical for your business."
                ],
                message="I've analyzed your company and identified potential pain points. Please review the suggested pain points and let me know which ones are most relevant to your business. You can call this endpoint again with the selected pain points in the 'pain_points' field."
            )
        
        else:
            # Pain points provided - find matching projects
            pain_points = request.pain_points
            
            # Step 3: Find matching projects (with fallback logic)
            recommended_projects = qa_system.find_matching_projects(pain_points, request.company_name)
            
            # Step 4: Generate next questions for engagement
            next_questions = [
                f"Which of these projects seems most relevant for {request.company_name}?",
                "Would you like to know more about any specific project?",
                "What's your current approach to handling these challenges?",
                "Do you have any existing systems that need to be integrated?"
            ]
            
            # Store session for follow-up
            session_id = f"{request.company_name}_{len(conversation_sessions)}"
            conversation_sessions[session_id] = {
                "company_info": company_info,
                "pain_points": pain_points,
                "recommended_projects": recommended_projects,
                "state": ConversationState.PROJECTS_RECOMMENDED
            }
            
            return CompanyAnalysisResponse(
                company_name=request.company_name,
                company_info=company_info,
                identified_pain_points=pain_points,
                recommended_projects=recommended_projects,
                conversation_state=ConversationState.PROJECTS_RECOMMENDED,
                next_questions=next_questions,
                message=f"Based on your pain points, I've found {len(recommended_projects)} project recommendations. Use the /project-interest endpoint to express interest in any specific project."
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing company: {str(e)}")

@app.post("/project-interest")
async def express_project_interest(request: ProjectInterestRequest):
    """
    Handle user interest in a specific project and provide integration suggestions.
    
    This endpoint:
    1. Takes user interest in a specific project
    2. Generates detailed integration suggestions
    3. Provides implementation guidance
    4. Offers next steps for evaluation
    """
    
    try:
        # Find the session
        session = None
        for session_id, session_data in conversation_sessions.items():
            if request.company_name.lower() in session_id.lower():
                session = session_data
                break
        
        if not session:
            raise HTTPException(status_code=404, detail="Company analysis session not found. Please run company analysis first.")
        
        # Find the specific project
        project_info = None
        for project in session["recommended_projects"]:
            if project["project_id"] == request.project_id:
                project_info = project
                break
        
        if not project_info:
            raise HTTPException(status_code=404, detail="Project not found in recommendations")
        
        # Generate integration suggestions
        integration_suggestions = qa_system.generate_integration_suggestions(
            session["company_info"],
            project_info,
            request.user_interest,
            request.current_systems
        )
        
        # Update session state
        session["state"] = ConversationState.INTEGRATION_DISCUSSION
        session["selected_project"] = project_info
        session["integration_suggestions"] = integration_suggestions
        
        return {
            "company_name": request.company_name,
            "project": project_info,
            "user_interest": request.user_interest,
            "integration_suggestions": integration_suggestions,
            "next_steps": integration_suggestions.get("next_steps", []),
            "pilot_suggestions": integration_suggestions.get("pilot_suggestions", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing project interest: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a natural language question about the project graph database.
    
    Example questions:
    - "What projects use AI technology?"
    - "Which projects share the most pain points?"
    - "Show me projects in the cybersecurity industry"
    - "What are the most common capabilities?"
    - "Find similar projects to CyberSecure GenAI"
    """
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = qa_system.process_question(request.question, request.context_limit)
        return QuestionResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Graph QA API is running"}

@app.get("/schema")
async def get_schema():
    """Get graph schema information"""
    return {"schema": qa_system.schema_context}

@app.get("/sample-questions")
async def get_sample_questions():
    """Get sample questions to try"""
    return {
        "sample_questions": [
            "What projects use AI technology?",
            "Which projects share the most pain points?",
            "Show me projects in the cybersecurity industry",
            "What are the most common capabilities across all projects?",
            "Find similar projects to CyberSecure GenAI",
            "What technologies are used by HR projects?",
            "Which projects are deployed vs not deployed?",
            "What regulations do most projects comply with?",
            "Show me projects that address SQL injection",
            "What domains have the most projects?",
            "Which industries are most targeted by these projects?",
            "What pain points are shared by multiple projects?"
        ]
    }

# Example usage and testing
if __name__ == "__main__":
    import uvicorn
    
    # Make sure to set your OpenAI API key as an environment variable
    # export OPENAI_API_KEY="your-api-key-here"
    
    print("🚀 Starting Graph QA API...")
    print("📊 Make sure Neo4j is running and the graph is built!")
    print("🔑 Set OPENAI_API_KEY environment variable")
    print("📝 API will be available at: http://localhost:8000")
    print("📚 Interactive docs at: http://localhost:8000/docs")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


