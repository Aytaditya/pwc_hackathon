#!/usr/bin/env python3

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
from enum import Enum
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

# MCP imports - CORRECTED
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graph-qa-mcp")

class ConversationState(str, Enum):
    INITIAL = "initial"
    COMPANY_SEARCHED = "company_searched"
    PAIN_POINTS_SUGGESTED = "pain_points_suggested"
    PAIN_POINTS_CONFIRMED = "pain_points_confirmed"
    PROJECTS_RECOMMENDED = "projects_recommended"
    PROJECT_SELECTED = "project_selected"
    INTEGRATION_DISCUSSED = "integration_discussed"

@dataclass
class CompanySession:
    company_name: str
    company_info: Dict[str, Any]
    state: ConversationState
    suggested_pain_points: List[str] = None
    confirmed_pain_points: List[str] = None
    recommended_projects: List[Dict[str, Any]] = None
    selected_project: Dict[str, Any] = None
    integration_suggestions: Dict[str, Any] = None
    context: Dict[str, Any] = None

class GraphQASystem:
    """Simplified GraphQA system for MCP integration"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.serp_api_key = os.getenv("SERP_API_KEY", "31b2d407d3035b81ad59b575e9c82ceca4febe813f1b44ae622208813b42517e")
        
        # Neo4j connection would go here
        self.neo4j_url = os.getenv("NEO4J_URL", "bolt://localhost:7687")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "test1234")
        
        # Mock graph schema for demonstration
        self.schema_context = """
        GRAPH SCHEMA:
        Node Types: Project, PainPoint, Capability, Industry, Technology, Domain, Regulation
        Relationships: ADDRESSES, HAS_CAPABILITY, TARGETS, USES_TECHNOLOGY, BELONGS_TO, COMPLIES_WITH
        """
        
        logger.info("GraphQA System initialized")
    
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using SERP API"""
        try:
            search_url = "https://serpapi.com/search"
            search_params = {
                "q": f"{company_name} company business model services products",
                "api_key": self.serp_api_key,
                "engine": "google",
                "num": 3
            }
            
            response = requests.get(search_url, params=search_params)
            if response.status_code == 200:
                search_results = response.json()
                return {
                    "name": company_name,
                    "search_results": search_results.get("organic_results", [])[:3],
                    "knowledge_graph": search_results.get("knowledge_graph", {}),
                    "answer_box": search_results.get("answer_box", {})
                }
            else:
                logger.warning(f"SERP API request failed: {response.status_code}")
                return {"name": company_name, "error": "Search failed", "search_results": []}
        
        except Exception as e:
            logger.error(f"Error searching company info: {e}")
            return {"name": company_name, "error": str(e), "search_results": []}
    
    def suggest_pain_points(self, company_info: Dict[str, Any]) -> List[str]:
        """Generate pain point suggestions using OpenAI"""
        context = f"Company: {company_info['name']}\n"
        
        if company_info.get("knowledge_graph"):
            kg = company_info["knowledge_graph"]
            context += f"Industry: {kg.get('type', 'Unknown')}\n"
            context += f"Description: {kg.get('description', '')}\n"
        
        for i, result in enumerate(company_info.get("search_results", [])[:2]):
            context += f"\nResult {i+1}: {result.get('title', '')} - {result.get('snippet', '')}\n"
        
        prompt = f"""
        Based on this company information, suggest 6-8 specific business pain points:
        
        {context}
        
        Focus on common business challenges like:
        - Manual process automation needs
        - Data analysis and reporting gaps
        - Customer service inefficiencies
        - Security and compliance issues
        - Sales and marketing challenges
        - HR and recruitment difficulties
        - Technology integration problems
        
        Return only a JSON array of pain point strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error generating pain points: {e}")
            return [
                "Manual data entry processes",
                "Inefficient customer support",
                "Cybersecurity vulnerabilities",
                "Poor data analytics capabilities",
                "Compliance management challenges",
                "Sales process inefficiencies"
            ]
    
    def find_matching_projects(self, pain_points: List[str], company_name: str) -> List[Dict[str, Any]]:
        """Find projects that match the identified pain points"""
        # This would normally query the Neo4j database
        # For demo purposes, we'll simulate with OpenAI recommendations
        
        prompt = f"""
        Company: {company_name}
        Pain Points: {json.dumps(pain_points)}
        
        Based on these pain points, recommend 3-5 relevant AI/automation projects that could help.
        
        Return JSON array with this structure:
        [
            {{
                "project_id": "unique-id",
                "project_name": "Project Name",
                "match_score": 85,
                "explanation": "Why this project matches the pain points",
                "addresses_pain_points": ["specific pain point 1", "specific pain point 2"],
                "summary": "Brief project description",
                "deployment_status": "Available",
                "technologies": ["AI", "Python", "FastAPI"],
                "estimated_timeline": "4-6 weeks"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"Error finding projects: {e}")
            return [
                {
                    "project_id": "automation-suite",
                    "project_name": "Business Process Automation Suite",
                    "match_score": 75,
                    "explanation": "Addresses multiple manual process pain points",
                    "addresses_pain_points": pain_points[:2],
                    "summary": "Comprehensive automation solution for common business processes",
                    "deployment_status": "Available",
                    "technologies": ["Python", "FastAPI", "RPA"],
                    "estimated_timeline": "6-8 weeks"
                }
            ]
    
    def generate_integration_plan(self, company_info: Dict[str, Any], project_info: Dict[str, Any], 
                                current_systems: str = None) -> Dict[str, Any]:
        """Generate integration plan for selected project"""
        
        prompt = f"""
        Company: {company_info['name']}
        Project: {project_info['project_name']}
        Current Systems: {current_systems or 'Not specified'}
        
        Generate a detailed integration plan including:
        1. Technical requirements
        2. Implementation phases
        3. Timeline estimates
        4. Resource needs
        5. Risk mitigation
        6. Success metrics
        
        Return as JSON:
        {{
            "technical_requirements": ["req1", "req2"],
            "implementation_phases": {{
                "phase_1": "Discovery and Planning (1-2 weeks)",
                "phase_2": "Development and Testing (3-4 weeks)",
                "phase_3": "Deployment and Training (1-2 weeks)"
            }},
            "resource_needs": ["2 developers", "1 project manager"],
            "risks_and_mitigation": ["Risk 1: Mitigation strategy"],
            "success_metrics": ["metric1", "metric2"],
            "next_steps": ["Schedule technical review", "Prepare pilot environment"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"Error generating integration plan: {e}")
            return {
                "technical_requirements": ["API access", "Database connectivity"],
                "implementation_phases": {
                    "phase_1": "Planning and setup (2 weeks)",
                    "phase_2": "Implementation (4 weeks)",
                    "phase_3": "Testing and deployment (2 weeks)"
                },
                "resource_needs": ["Technical team", "Project coordination"],
                "risks_and_mitigation": ["Integration complexity: Phased approach"],
                "success_metrics": ["Reduced processing time", "Improved accuracy"],
                "next_steps": ["Schedule technical discussion", "Review requirements"]
            }
    
    def answer_general_question(self, question: str) -> str:
        """Answer general questions about the graph database"""
        prompt = f"""
        You are a knowledgeable assistant for a graph database containing project information.
        
        Database contains: Projects, Technologies, Industries, Pain Points, Capabilities, etc.
        
        Question: {question}
        
        Provide a helpful response. If you need to access specific data, explain what kind of query would be needed.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I apologize, but I'm having trouble processing your question right now. Please try again."

# Initialize the system
qa_system = GraphQASystem()

# Session storage (in production, use Redis or database)
sessions: Dict[str, CompanySession] = {}

# Create MCP server
mcp = FastMCP("Graph Knowledge QA")

@mcp.tool()
def start_company_analysis(company_name: str) -> str:
    """
    Start analyzing a company to identify pain points and recommend projects.
    
    Args:
        company_name: The name of the company to analyze
    
    Returns:
        Initial analysis with company information and next steps
    """
    
    if not company_name.strip():
        return "Please provide a valid company name."
    
    try:
        # Search for company information
        company_info = qa_system.search_company_info(company_name)
        
        # Create new session
        session = CompanySession(
            company_name=company_name,
            company_info=company_info,
            state=ConversationState.COMPANY_SEARCHED
        )
        
        sessions[company_name.lower()] = session
        
        # Format response
        response = f"🏢 **Company Analysis Started: {company_name}**\n\n"
        
        if company_info.get("knowledge_graph"):
            kg = company_info["knowledge_graph"]
            response += f"**Industry:** {kg.get('type', 'Unknown')}\n"
            response += f"**Description:** {kg.get('description', 'No description available')}\n\n"
        
        response += "**What I found:**\n"
        for i, result in enumerate(company_info.get("search_results", [])[:2]):
            response += f"{i+1}. {result.get('title', 'No title')}\n"
            response += f"   {result.get('snippet', 'No snippet')}\n\n"
        
        response += "✨ **Next Step:** I'll analyze this information to suggest potential pain points.\n"
        response += f"Use `suggest_pain_points('{company_name}')` to continue!"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in start_company_analysis: {e}")
        return f"❌ Error analyzing company: {str(e)}"

@mcp.tool()
def suggest_pain_points(company_name: str) -> str:
    """
    Generate pain point suggestions for a company based on their business profile.
    
    Args:
        company_name: The company name (must have been analyzed first)
    
    Returns:
        List of suggested pain points for user confirmation
    """
    
    session = sessions.get(company_name.lower())
    if not session:
        return f"❌ No session found for {company_name}. Please run `start_company_analysis('{company_name}')` first."
    
    try:
        # Generate pain point suggestions
        pain_points = qa_system.suggest_pain_points(session.company_info)
        
        # Update session
        session.suggested_pain_points = pain_points
        session.state = ConversationState.PAIN_POINTS_SUGGESTED
        
        response = f"🎯 **Suggested Pain Points for {company_name}:**\n\n"
        
        for i, pain_point in enumerate(pain_points, 1):
            response += f"{i}. {pain_point}\n"
        
        response += f"\n💡 **Next Steps:**\n"
        response += f"- Review these pain points and select the most relevant ones\n"
        response += f"- Use `confirm_pain_points('{company_name}', [1,2,3])` to select by numbers\n"
        response += f"- Or use `confirm_pain_points('{company_name}', ['custom pain point'])` to specify your own\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in suggest_pain_points: {e}")
        return f"❌ Error generating pain points: {str(e)}"

@mcp.tool()
def confirm_pain_points(company_name: str, selected_pain_points: List[Any]) -> str:
    """
    Confirm selected pain points and get project recommendations.
    
    Args:
        company_name: The company name
        selected_pain_points: List of pain point numbers (1-based) or custom pain point strings
    
    Returns:
        Project recommendations based on confirmed pain points
    """
    
    session = sessions.get(company_name.lower())
    if not session:
        return f"❌ No session found for {company_name}. Please start company analysis first."
    
    try:
        # Process selected pain points
        confirmed_pain_points = []
        
        for item in selected_pain_points:
            if isinstance(item, int):
                # User selected by number
                if 1 <= item <= len(session.suggested_pain_points or []):
                    confirmed_pain_points.append(session.suggested_pain_points[item - 1])
            elif isinstance(item, str):
                # User provided custom pain point
                confirmed_pain_points.append(item)
        
        if not confirmed_pain_points:
            return "❌ No valid pain points selected. Please try again."
        
        # Update session
        session.confirmed_pain_points = confirmed_pain_points
        session.state = ConversationState.PAIN_POINTS_CONFIRMED
        
        # Find matching projects
        projects = qa_system.find_matching_projects(confirmed_pain_points, company_name)
        session.recommended_projects = projects
        session.state = ConversationState.PROJECTS_RECOMMENDED
        
        # Format response
        response = f"✅ **Confirmed Pain Points for {company_name}:**\n"
        for i, pain_point in enumerate(confirmed_pain_points, 1):
            response += f"{i}. {pain_point}\n"
        
        response += f"\n🚀 **Recommended Projects:**\n\n"
        
        for i, project in enumerate(projects, 1):
            response += f"**{i}. {project['project_name']}** (Match: {project['match_score']}%)\n"
            response += f"   📋 {project['summary']}\n"
            response += f"   🎯 Addresses: {', '.join(project['addresses_pain_points'])}\n"
            response += f"   ⏱️ Timeline: {project.get('estimated_timeline', 'TBD')}\n"
            response += f"   🔧 Technologies: {', '.join(project.get('technologies', []))}\n\n"
        
        response += f"💡 **Next Step:** Choose a project to explore integration details.\n"
        response += f"Use `select_project('{company_name}', 1)` to select project by number."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in confirm_pain_points: {e}")
        return f"❌ Error confirming pain points: {str(e)}"

@mcp.tool()
def select_project(company_name: str, project_number: int, current_systems: str = None) -> str:
    """
    Select a project and get detailed integration plan.
    
    Args:
        company_name: The company name
        project_number: Project number from the recommendations (1-based)
        current_systems: Optional description of current systems/tech stack
    
    Returns:
        Detailed integration plan for the selected project
    """
    
    session = sessions.get(company_name.lower())
    if not session or not session.recommended_projects:
        return f"❌ No project recommendations found for {company_name}. Please complete the analysis first."
    
    try:
        # Validate project selection
        if not (1 <= project_number <= len(session.recommended_projects)):
            return f"❌ Invalid project number. Please select between 1 and {len(session.recommended_projects)}."
        
        # Get selected project
        selected_project = session.recommended_projects[project_number - 1]
        session.selected_project = selected_project
        session.state = ConversationState.PROJECT_SELECTED
        
        # Generate integration plan
        integration_plan = qa_system.generate_integration_plan(
            session.company_info, 
            selected_project, 
            current_systems
        )
        session.integration_suggestions = integration_plan
        session.state = ConversationState.INTEGRATION_DISCUSSED
        
        # Format response
        response = f"🎯 **Selected Project: {selected_project['project_name']}**\n\n"
        response += f"**Summary:** {selected_project['summary']}\n\n"
        
        response += f"📋 **Integration Plan:**\n\n"
        
        response += f"**Technical Requirements:**\n"
        for req in integration_plan.get('technical_requirements', []):
            response += f"• {req}\n"
        
        response += f"\n**Implementation Phases:**\n"
        for phase, description in integration_plan.get('implementation_phases', {}).items():
            response += f"• **{phase.title()}:** {description}\n"
        
        response += f"\n**Resource Needs:**\n"
        for resource in integration_plan.get('resource_needs', []):
            response += f"• {resource}\n"
        
        response += f"\n**Success Metrics:**\n"
        for metric in integration_plan.get('success_metrics', []):
            response += f"• {metric}\n"
        
        response += f"\n**Next Steps:**\n"
        for step in integration_plan.get('next_steps', []):
            response += f"• {step}\n"
        
        response += f"\n💡 You can now ask specific questions about implementation, or use `get_session_summary('{company_name}')` for a complete overview."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in select_project: {e}")
        return f"❌ Error selecting project: {str(e)}"

@mcp.tool()
def get_session_summary(company_name: str) -> str:
    """
    Get a complete summary of the analysis session.
    
    Args:
        company_name: The company name
    
    Returns:
        Complete session summary with all decisions and recommendations
    """
    
    session = sessions.get(company_name.lower())
    if not session:
        return f"❌ No session found for {company_name}."
    
    try:
        response = f"📊 **Complete Analysis Summary for {company_name}**\n\n"
        
        # Company info
        response += f"**Company Information:**\n"
        if session.company_info.get("knowledge_graph"):
            kg = session.company_info["knowledge_graph"]
            response += f"• Industry: {kg.get('type', 'Unknown')}\n"
            response += f"• Description: {kg.get('description', 'N/A')}\n"
        
        # Pain points
        if session.confirmed_pain_points:
            response += f"\n**Confirmed Pain Points:**\n"
            for i, pain_point in enumerate(session.confirmed_pain_points, 1):
                response += f"{i}. {pain_point}\n"
        
        # Selected project
        if session.selected_project:
            project = session.selected_project
            response += f"\n**Selected Project:**\n"
            response += f"• **Name:** {project['project_name']}\n"
            response += f"• **Match Score:** {project['match_score']}%\n"
            response += f"• **Summary:** {project['summary']}\n"
            response += f"• **Technologies:** {', '.join(project.get('technologies', []))}\n"
            response += f"• **Timeline:** {project.get('estimated_timeline', 'TBD')}\n"
        
        # Integration plan
        if session.integration_suggestions:
            response += f"\n**Integration Status:** Planning phase complete\n"
            response += f"• Technical requirements identified\n"
            response += f"• Implementation phases defined\n"
            response += f"• Next steps outlined\n"
        
        response += f"\n**Session State:** {session.state.value}\n"
        response += f"\n💡 **Available Actions:**\n"
        response += f"• Ask questions about the analysis\n"
        response += f"• Request more details about implementation\n"
        response += f"• Explore alternative projects\n"
        response += f"• Start analysis for another company\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_session_summary: {e}")
        return f"❌ Error generating summary: {str(e)}"

@mcp.tool()
def ask_question(question: str) -> str:
    """
    Ask a general question about the graph database or current analysis.
    
    Args:
        question: Your question about projects, technologies, or analysis
    
    Returns:
        Answer to your question
    """
    
    try:
        # Check if question is about a specific session
        for company_name, session in sessions.items():
            if company_name in question.lower():
                # Context-aware response
                context = f"Current analysis for {session.company_name}: "
                context += f"State: {session.state.value}, "
                if session.confirmed_pain_points:
                    context += f"Pain points: {', '.join(session.confirmed_pain_points)}, "
                if session.selected_project:
                    context += f"Selected project: {session.selected_project['project_name']}"
                
                response = qa_system.answer_general_question(f"{context}\n\nQuestion: {question}")
                return f"🤔 **Question:** {question}\n\n**Answer:** {response}"
        
        # General question
        response = qa_system.answer_general_question(question)
        return f"🤔 **Question:** {question}\n\n**Answer:** {response}"
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        return f"❌ Error answering question: {str(e)}"

@mcp.tool()
def list_active_sessions() -> str:
    """
    List all active company analysis sessions.
    
    Returns:
        List of active sessions with their current state
    """
    
    if not sessions:
        return "📭 No active sessions. Use `start_company_analysis('Company Name')` to begin."
    
    response = "📋 **Active Sessions:**\n\n"
    
    for company_name, session in sessions.items():
        response += f"**{session.company_name}**\n"
        response += f"• State: {session.state.value}\n"
        
        if session.confirmed_pain_points:
            response += f"• Pain points: {len(session.confirmed_pain_points)} confirmed\n"
        
        if session.recommended_projects:
            response += f"• Projects: {len(session.recommended_projects)} recommended\n"
        
        if session.selected_project:
            response += f"• Selected: {session.selected_project['project_name']}\n"
        
        response += "\n"
    
    response += "💡 Use `get_session_summary('Company Name')` for detailed information about any session."
    
    return response

@mcp.tool()
def get_help() -> str:
    """
    Get help information about available commands and workflow.
    
    Returns:
        Help information and example usage
    """
    
    return """
🚀 **Graph Knowledge QA System - Help Guide**

**📋 Complete Workflow:**

1. **Start Analysis**
   `start_company_analysis('Company Name')`
   - Searches for company information
   - Prepares for pain point analysis

2. **Get Pain Point Suggestions**
   `suggest_pain_points('Company Name')`
   - AI-generated pain point suggestions
   - Based on company profile and industry

3. **Confirm Pain Points**
   `confirm_pain_points('Company Name', [1,2,3])`
   - Select by numbers: [1,2,3] 
   - Or custom: ['Custom pain point']
   - Triggers project recommendations

4. **Select Project**
   `select_project('Company Name', 1)`
   - Choose project by number
   - Optional: add current systems info
   - Gets detailed integration plan

5. **Get Summary**
   `get_session_summary('Company Name')`
   - Complete analysis overview
   - All decisions and recommendations

**🔧 Other Commands:**
- `ask_question('your question')` - Ask anything
- `list_active_sessions()` - See all sessions
- `get_help()` - This help message

**💡 Example Complete Flow:**
```
start_company_analysis('TechCorp Inc')
suggest_pain_points('TechCorp Inc')
confirm_pain_points('TechCorp Inc', [1,3,5])
select_project('TechCorp Inc', 2)
get_session_summary('TechCorp Inc')
```

**🎯 Tips:**
- Each company gets its own session
- You can work with multiple companies simultaneously
- Ask questions anytime during the process
- Sessions persist throughout the conversation
"""

# Add resource for system status
@mcp.resource("system://status")
def get_system_status() -> str:
    """Get current system status and active sessions"""
    status = {
        "system": "Graph Knowledge QA MCP Server",
        "status": "Running",
        "active_sessions": len(sessions),
        "available_tools": [
            "start_company_analysis",
            "suggest_pain_points", 
            "confirm_pain_points",
            "select_project",
            "get_session_summary",
            "ask_question",
            "list_active_sessions",
            "get_help"
        ]
    }
    return json.dumps(status, indent=2)

if __name__ == "__main__":
    # Configure environment
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not found in environment variables")
    
    logger.info("🚀 Starting Graph Knowledge QA MCP Server...")
    logger.info("💡 Use get_help() to see available commands")
    logger.info("🏢 Start with: start_company_analysis('Company Name')")
    
    # Run the MCP server
    mcp.run()