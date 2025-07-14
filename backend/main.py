from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
try:
    from langchain_neo4j import Neo4jGraph
except ImportError:
    from langchain_community.graphs import Neo4jGraph

load_dotenv()  

app = FastAPI(title="Graph Knowledge QA API", version="1.0.0")

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
    
    uvicorn.run(app, host="0.0.0.0", port=8000)