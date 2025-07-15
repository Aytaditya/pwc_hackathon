"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Info, HelpCircle, Settings, Code, Search, Lightbulb, Bot, Brain, Atom } from 'lucide-react'

export default function Chatbot({ clientName }) {
  // Main chat states
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState("")
  const [activeTab, setActiveTab] = useState("planner")
  const [mainView, setMainView] = useState("analysis")
  const [companyAnalysis, setCompanyAnalysis] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedProjects, setSelectedProjects] = useState([]) // Stores selected project objects
  const [quickSuggestions, setQuickSuggestions] = useState([])
  const messagesEndRef = useRef(null)

  // AI Lab chat states
  const [aiLabMessages, setAiLabMessages] = useState([])
  const [aiLabInput, setAiLabInput] = useState("")
  const [aiLabLoading, setAiLabLoading] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, aiLabMessages])

  // Function to handle project interest response
  const handleProjectInterestResponse = (data) => {
    const botMessage = {
      type: "project_interest_response",
      data: data,
      sender: "bot",
      avatar: <Bot className="w-5 h-5 text-white" />,
    }
    setMessages((prevMessages) => [...prevMessages, botMessage])
  }

  const handleProjectSelect = async (projectId) => {
    const project = quickSuggestions.find((p) => p.id === projectId)
    if (project) {
      setSelectedProjects((prev) => [...prev, project])
      setQuickSuggestions((prev) => prev.filter((p) => p.id !== projectId))

      const userMessage = {
        text: `You've selected the project: ${project.name}`,
        sender: "user",
        avatar: (
          <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
            PD
          </div>
        ),
      }
      setMessages((prev) => [...prev, userMessage])

      setIsLoading(true)
      setError(null)
      try {
        const payload = {
          company_name: clientName,
          project_id: project.id,
          user_interest: project.name, // Initial interest is the project name
          current_systems: "", // Placeholder as not provided
        }
        const response = await fetch("http://localhost:8000/project-interest", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        })

        if (!response.ok) {
          throw new Error(`Failed to get project interest: ${response.status}`)
        }

        const data = await response.json()
        handleProjectInterestResponse(data)
      } catch (err) {
        console.error("Error fetching project interest:", err)
        setError(err.message)
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            text: `I couldn't process your interest in ${project.name}. Error: ${err.message}`,
            sender: "bot",
            isError: true,
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
        ])
      } finally {
        setIsLoading(false)
      }
    }
  }

  // Main chat functions
  const fetchAndProcessAnalysis = async (companyName, painPoints = [], additionalContext = null, isInitial = false) => {
    setIsLoading(true)
    setError(null)
    try {
      const payload = {
        company_name: companyName,
        pain_points: painPoints,
        additional_context: additionalContext,
      }
      const response = await fetch("http://localhost:8000/analyze-company", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`Failed to analyze company: ${response.status}`)
      }

      const data = await response.json()
      setCompanyAnalysis(data)

      // Extract project suggestions for quick selection
      if (data.recommended_projects) {
        const suggestions = data.recommended_projects.map((project) => ({
          id: project.project_id,
          name: project.project_name,
          summary: project.summary,
          url: project.url,
        }))
        setQuickSuggestions(suggestions)
      }

      let newBotMessages = []
      if (isInitial) {
        newBotMessages = [
          {
            text: `Hello, ${companyName}! I'm your AI-Powered Network Twin. How can I assist you today?`,
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            text: `I've completed an initial analysis for ${companyName}.`,
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            text: "Here's a summary of the company information I found:",
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            type: "company_info_summary",
            data: data.company_info,
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            text: "Based on this, I've identified some potential pain points:",
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            type: "pain_points_summary",
            data: {
              identified: data.identified_pain_points,
              suggested: data.suggested_pain_points,
            },
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            text: "You can find detailed project recommendations in the 'Projects' tab on the right sidebar. Feel free to ask me anything else!",
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
        ]
      } else {
        newBotMessages = [
          {
            text: "I've updated the analysis based on your input. Here are the refined insights:",
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            type: "company_info_summary",
            data: data.company_info,
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            type: "pain_points_summary",
            data: {
              identified: data.identified_pain_points,
              suggested: data.suggested_pain_points,
            },
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
          {
            text: "Please check the 'Projects' tab for updated recommendations.",
            sender: "bot",
            avatar: <Bot className="w-5 h-5 text-white" />,
          },
        ]
      }
      setMessages((prevMessages) => [...prevMessages, ...newBotMessages])
    } catch (err) {
      console.error("Error fetching company analysis:", err)
      setError(err.message)
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: `I couldn't retrieve the company analysis for ${companyName}. You can still ask me questions directly. Error: ${err.message}`,
          sender: "bot",
          isError: true,
          avatar: <Bot className="w-5 h-5 text-white" />,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    // This effect runs once on initial load if clientName is present.
    // messages.length === 0 ensures it doesn't re-fetch on every message.
    // clientName is the only dependency that should trigger a re-fetch of initial analysis. [^1]
    if (clientName && messages.length === 0) {
      fetchAndProcessAnalysis(clientName, ["marketing", "sales", "operations"], null, true)
    }
  }, [clientName])

  const handleSendMessage = async () => {
    if (inputMessage.trim() === "") return

    const userMessage = {
      text: inputMessage,
      sender: "user",
      avatar: (
        <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
          PD
        </div>
      ),
    }
    setMessages((prevMessages) => [...prevMessages, userMessage])
    setInputMessage("")

    let targetProjectId = null
    let targetProjectName = null

    if (selectedProjects.length > 0) {
      const lastSelected = selectedProjects[selectedProjects.length - 1]
      targetProjectId = lastSelected.id
      targetProjectName = lastSelected.name
    } else if (companyAnalysis?.recommended_projects?.length > 0) {
      // Fallback to the first recommended project if none are explicitly selected
      const firstRecommended = companyAnalysis.recommended_projects[0]
      targetProjectId = firstRecommended.project_id
      targetProjectName = firstRecommended.project_name
    } else {
      // If no project is selected or recommended, we cannot hit /project-interest
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: "Please select a project from the 'Projects' tab or wait for initial analysis to complete before asking project-specific questions.",
          sender: "bot",
          isError: true,
          avatar: <Bot className="w-5 h-5 text-white" />,
        },
      ])
      return // Exit if no project context
    }

    setIsLoading(true)
    setError(null)
    try {
      const payload = {
        company_name: clientName,
        project_id: targetProjectId,
        user_interest: userMessage.text, // User's typed message is the interest
        current_systems: "", // Placeholder
      }
      const response = await fetch("http://localhost:8000/project-interest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`Failed to get project interest: ${response.status}`)
      }

      const data = await response.json()
      handleProjectInterestResponse(data)
    } catch (err) {
      console.error("Error sending message (project interest):", err)
      setError(err.message)
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: `Sorry, I couldn't process your request about ${targetProjectName}. Error: ${err.message}`,
          sender: "bot",
          isError: true,
          avatar: <Bot className="w-5 h-5 text-white" />,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // AI Lab chat functions
  const handleAiLabSendMessage = async () => {
    if (aiLabInput.trim() === "") return

    const userMessage = {
      text: aiLabInput,
      sender: "user",
      avatar: (
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
          AI
        </div>
      ),
    }
    setAiLabMessages((prev) => [...prev, userMessage])
    setAiLabInput("")
    setAiLabLoading(true)

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userMessage.text }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const botMessage = {
        text: data.answer,
        cypher_query: data.cypher_query,
        confidence: data.confidence,
        sender: "bot",
        avatar: <Brain className="w-5 h-5 text-white" />,
      }
      setAiLabMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error("Error sending AI Lab message:", error)
      setAiLabMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I couldn't get a response from the AI Lab. Please try again.",
          sender: "bot",
          isError: true,
          avatar: <Brain className="w-5 h-5 text-white" />,
        },
      ])
    } finally {
      setAiLabLoading(false)
    }
  }

  // Message rendering
  const renderMessageContent = (message) => {
    if (message.type === "company_info_summary") {
      const info = message.data
      return (
        <div className="bg-[#2A2A2A] p-4 rounded-lg space-y-2 text-gray-300 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">Company Information</h3>
          {info.knowledge_graph && Object.keys(info.knowledge_graph).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-300">Knowledge Graph:</h4>
              <p className="text-sm">
                {info.knowledge_graph.description || info.knowledge_graph.title || "No description available."}
              </p>
              {info.knowledge_graph.type && <p className="text-xs text-gray-400">Type: {info.knowledge_graph.type}</p>}
            </div>
          )}
          {info.answer_box && Object.keys(info.answer_box).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-300">Quick Answer:</h4>
              <p className="text-sm">{info.answer_box.snippet}</p>
            </div>
          )}
          {info.search_results && info.search_results.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-300">Top Search Results:</h4>
              <ul className="list-disc list-inside text-sm space-y-1">
                {info.search_results.slice(0, 2).map((result, i) => (
                  <li key={i}>
                    <a
                      href={result.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:underline"
                    >
                      {result.title}
                    </a>
                    <p className="text-xs text-gray-400">{result.snippet}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!info.knowledge_graph && !info.answer_box && (!info.search_results || info.search_results.length === 0) && (
            <p>No detailed company information found.</p>
          )}
        </div>
      )
    } else if (message.type === "pain_points_summary") {
      const { identified, suggested } = message.data
      return (
        <div className="bg-[#2A2A2A] p-4 rounded-lg space-y-2 text-gray-300 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">Identified Pain Points</h3>
          {identified && identified.length > 0 && (
            <div className="mb-3">
              <h4 className="font-medium text-gray-300">From Analysis:</h4>
              <ul className="list-disc list-inside text-sm space-y-1">
                {identified.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          {suggested && suggested.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-300">Suggested:</h4>
              <ul className="list-disc list-inside text-sm space-y-1">
                {suggested.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          {!identified?.length && !suggested?.length && <p>No specific pain points identified yet.</p>}
        </div>
      )
    } else if (message.type === "project_interest_response") {
      const { project, integration_suggestions, next_steps, pilot_suggestions } = message.data
      return (
        <div className="bg-[#2A2A2A] p-4 rounded-lg space-y-4 text-gray-300 border border-gray-700">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-purple-400" /> Project Interest Details: {project.project_name}
          </h3>

          {/* Project Details */}
          <div className="space-y-2">
            <h4 className="font-medium text-gray-300">Project Overview:</h4>
            <p className="text-sm text-gray-400">{project.summary}</p>
            {project.explanation && <p className="text-xs text-gray-500">Explanation: {project.explanation}</p>}
            {project.match_score && <p className="text-xs text-gray-500">Relevance: {project.match_score}/100</p>}
            {project.addresses_pain_points && project.addresses_pain_points.length > 0 && (
              <div>
                <p className="text-xs text-gray-500">Addresses Pain Points:</p>
                <ul className="list-disc list-inside text-xs text-gray-500 ml-2">
                  {project.addresses_pain_points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
            {project.deployment_status && (
              <p className="text-xs text-gray-500">Deployment Status: {project.deployment_status}</p>
            )}
            {project.url && (
              <a
                href={project.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-purple-400 hover:underline block mt-1"
              >
                View Project Details
              </a>
            )}
          </div>

          {/* Integration Suggestions */}
          {integration_suggestions && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-300">Integration Suggestions:</h4>
              {integration_suggestions.implementation_approach && (
                <p className="text-sm text-gray-400">
                  Implementation Approach: {integration_suggestions.implementation_approach}
                </p>
              )}
              {integration_suggestions.technical_requirements &&
                integration_suggestions.technical_requirements.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-400">Technical Requirements:</p>
                    <ul className="list-disc list-inside text-sm text-gray-400 ml-2">
                      {integration_suggestions.technical_requirements.map((req, i) => (
                        <li key={i}>{req}</li>
                      ))}
                    </ul>
                  </div>
                )}
              {integration_suggestions.timeline && (
                <div>
                  <p className="text-sm text-gray-400">Timeline:</p>
                  <ul className="list-disc list-inside text-sm text-gray-400 ml-2">
                    {Object.entries(integration_suggestions.timeline).map(([phase, description]) => (
                      <li key={phase}>
                        <strong>{phase}:</strong> {description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {integration_suggestions.expected_benefits && integration_suggestions.expected_benefits.length > 0 && (
                <div>
                  <p className="text-sm text-gray-400">Expected Benefits:</p>
                  <ul className="list-disc list-inside text-sm text-gray-400 ml-2">
                    {integration_suggestions.expected_benefits.map((benefit, i) => (
                      <li key={i}>{benefit}</li>
                    ))}
                  </ul>
                </div>
              )}
              {integration_suggestions.potential_challenges &&
                integration_suggestions.potential_challenges.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-400">Potential Challenges:</p>
                    <ul className="list-disc list-inside text-sm text-gray-400 ml-2">
                      {integration_suggestions.potential_challenges.map((challenge, i) => (
                        <li key={i}>{challenge}</li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          )}

          {/* Next Steps & Pilot Suggestions */}
          {(next_steps?.length > 0 || pilot_suggestions) && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-300">Next Actions:</h4>
              {next_steps && next_steps.length > 0 && (
                <div>
                  <p className="text-sm text-gray-400">Recommended Next Steps:</p>
                  <ul className="list-disc list-inside text-sm text-gray-400 ml-2">
                    {next_steps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
              {pilot_suggestions && <p className="text-sm text-gray-400">Pilot Suggestions: {pilot_suggestions}</p>}
            </div>
          )}
        </div>
      )
    }
    return message.text
  }

  // Sidebar tab content
  const tabContent = {
    planner: (
      <div className="space-y-6">
        {companyAnalysis &&
          (companyAnalysis.identified_pain_points?.length > 0 || companyAnalysis.suggested_pain_points?.length > 0) && (
            <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Lightbulb className="w-4 h-4 mr-2 text-yellow-400" /> Pain Points for {clientName}
              </h3>
              {companyAnalysis.identified_pain_points?.length > 0 && (
                <div className="mb-3">
                  <h4 className="font-medium text-gray-300">Identified:</h4>
                  <ul className="list-disc list-inside text-gray-400 space-y-1">
                    {companyAnalysis.identified_pain_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
              )}
              {companyAnalysis.suggested_pain_points?.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-300">Suggested:</h4>
                  <ul className="list-disc list-inside text-gray-400 space-y-1">
                    {companyAnalysis.suggested_pain_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        {companyAnalysis && companyAnalysis.next_questions?.length > 0 && (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3">Next Steps / Questions</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              {companyAnalysis.next_questions.map((question, i) => (
                <li key={i}>{question}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    ),
    projects: (
      <div className="space-y-6">
        {/* Selected Projects */}
        {selectedProjects.length > 0 && (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2 text-green-400" /> Selected Projects
            </h3>
            <div className="space-y-3">
              {selectedProjects.map((project) => (
                <div key={project.id} className="bg-[#2A2A2A] p-3 rounded-lg border border-gray-600">
                  <h4 className="font-medium text-purple-400">{project.name}</h4>
                  <p className="text-sm text-gray-400">{project.summary}</p>
                  {project.url && (
                    <a
                      href={project.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-purple-400 hover:underline"
                    >
                      View Project Details
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Recommended Projects */}
        {companyAnalysis && companyAnalysis.recommended_projects?.length > 0 ? (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2 text-yellow-400" /> Recommended Projects for {clientName}
            </h3>
            <div className="space-y-3">
              {companyAnalysis.recommended_projects.map((project) => (
                <div key={project.project_id} className="bg-[#2A2A2A] p-3 rounded-lg border border-gray-600">
                  <h4 className="font-medium text-purple-400">{project.project_name}</h4>
                  <p className="text-sm text-gray-400">{project.summary}</p>
                  {project.match_score && (
                    <span className="text-xs text-gray-500">Relevance: {project.match_score}/100</span>
                  )}
                  {project.url && (
                    <a
                      href={project.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-purple-400 hover:underline ml-2"
                    >
                      Details
                    </a>
                  )}
                  <button
                    onClick={() => handleProjectSelect(project.project_id)}
                    className="mt-2 text-xs bg-purple-900 hover:bg-purple-800 text-white px-2 py-1 rounded"
                  >
                    Select Project
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700 text-gray-400">
            No specific project recommendations available for {clientName} at this time.
          </div>
        )}
      </div>
    ),
    reference: (
      <div className="space-y-6">
        {companyAnalysis && companyAnalysis.company_info ? (
          <>
            <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Info className="w-4 h-4 mr-2 text-blue-400" /> Company Overview
              </h3>
              {companyAnalysis.company_info.knowledge_graph &&
                Object.keys(companyAnalysis.company_info.knowledge_graph).length > 0 && (
                  <div className="mb-3">
                    <h4 className="font-medium text-gray-300">Knowledge Graph:</h4>
                    <p className="text-sm text-gray-400">
                      {companyAnalysis.company_info.knowledge_graph.description || "No description available."}
                    </p>
                    {companyAnalysis.company_info.knowledge_graph.type && (
                      <p className="text-xs text-gray-500">Type: {companyAnalysis.company_info.knowledge_graph.type}</p>
                    )}
                  </div>
                )}
              {companyAnalysis.company_info.answer_box &&
                Object.keys(companyAnalysis.company_info.answer_box).length > 0 && (
                  <div className="mb-3">
                    <h4 className="font-medium text-gray-300">Quick Answer:</h4>
                    <p className="text-sm text-gray-400">{companyAnalysis.company_info.answer_box.snippet}</p>
                  </div>
                )}
              {!companyAnalysis.company_info.knowledge_graph && !companyAnalysis.company_info.answer_box && (
                <p className="text-gray-400">No detailed overview available.</p>
              )}
            </div>
            <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Search className="w-4 h-4 mr-2 text-yellow-400" /> Top Search Results
              </h3>
              {companyAnalysis.company_info.search_results?.length > 0 ? (
                <ul className="list-disc list-inside text-gray-300 space-y-2">
                  {companyAnalysis.company_info.search_results.map((result, i) => (
                    <li key={i}>
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-400 hover:underline"
                      >
                        {result.title}
                      </a>
                      <p className="text-xs text-gray-400">{result.snippet}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">No search results found.</p>
              )}
            </div>
          </>
        ) : (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700 text-gray-400">
            Company analysis not loaded. Please ensure the backend is running and a client session is active.
          </div>
        )}
      </div>
    ),
    coder: (
      <div className="space-y-6">
        {/* Cypher Query Section */}
        {aiLabMessages.length > 0 && aiLabMessages[aiLabMessages.length - 1]?.cypher_query && (
          <div className="bg-[#3A3A3A] p-4 rounded-lg shadow-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
              <Code className="w-4 h-4 mr-2 text-blue-400" /> Latest Cypher Query
            </h3>
            <pre className="bg-[#1A1A1A] p-3 rounded-md text-sm overflow-x-auto text-gray-300">
              <code>{aiLabMessages[aiLabMessages.length - 1].cypher_query}</code>
            </pre>
            {aiLabMessages[aiLabMessages.length - 1]?.confidence && (
              <div className="mt-2 text-xs text-gray-400">
                Confidence:{" "}
                <span
                  className={
                    aiLabMessages[aiLabMessages.length - 1].confidence === "High"
                      ? "text-green-400"
                      : aiLabMessages[aiLabMessages.length - 1].confidence === "Medium"
                        ? "text-yellow-400"
                        : "text-red-400"
                  }
                >
                  {aiLabMessages[aiLabMessages.length - 1].confidence}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    ),
  }

  // AI Lab Content with Chat
  const aiLabContent = (
    <div className="flex flex-col h-full bg-[#1A1A1A]">
      {/* AI Lab Header */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Atom className="w-6 h-6 mr-3 text-blue-400" /> Gen AI Lab Chat
        </h2>
        <p className="text-sm text-gray-400 mt-1">Ask questions about our AI models, tools, and capabilities</p>
      </div>
      {/* AI Lab Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Loading state */}
        {aiLabLoading && (
          <div className="flex justify-center">
            <div className="animate-pulse text-gray-400">Thinking...</div>
          </div>
        )}
        {/* Messages */}
        {aiLabMessages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} items-start gap-3`}
          >
            {msg.sender === "bot" && (
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                {msg.avatar}
              </div>
            )}
            <div
              className={`p-3 rounded-lg shadow-md ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white max-w-[70%]"
                  : msg.isError
                    ? "bg-red-900 text-white max-w-[80%]"
                    : "bg-[#2A2A2A] text-gray-300 max-w-full w-full border border-gray-700"
              }`}
            >
              {msg.text}
              {/* Add Cypher query display if available */}
              {msg.cypher_query && (
                <div className="mt-3">
                  <div className="text-xs text-gray-400 mb-1">Cypher Query:</div>
                  <pre className="bg-[#1A1A1A] p-3 rounded-md text-sm overflow-x-auto text-gray-300">
                    <code>{msg.cypher_query}</code>
                  </pre>
                </div>
              )}
              {/* Add confidence level if available */}
              {msg.confidence && (
                <div className="mt-2 text-xs text-gray-400">
                  Confidence:{" "}
                  <span
                    className={
                      msg.confidence === "High"
                        ? "text-green-400"
                        : msg.confidence === "Medium"
                          ? "text-yellow-400"
                          : "text-red-400"
                    }
                  >
                    {msg.confidence}
                  </span>
                </div>
              )}
            </div>
            {msg.sender === "user" && (
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                AI
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      {/* AI Lab Input Area */}
      <div className="sticky bottom-0 w-full p-4 bg-[#1A1A1A] border-t border-gray-800">
        <div className="relative max-w-3xl mx-auto">
          <textarea
            placeholder="Ask about AI models, tools, or capabilities..."
            value={aiLabInput}
            onChange={(e) => setAiLabInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleAiLabSendMessage()
              }
            }}
            rows={1}
            className="min-h-[48px] rounded-xl resize-none p-4 border border-gray-700 shadow-inner pr-16 bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#1A1A1A] w-full placeholder-gray-500"
          ></textarea>
          <button
            type="submit"
            className="absolute w-10 h-10 top-2 right-2 bg-blue-600 hover:bg-blue-700 rounded-full flex items-center justify-center shadow-md"
            onClick={handleAiLabSendMessage}
            disabled={aiLabInput.trim() === ""}
            aria-label="Send AI Lab message"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-[#1A1A1A] text-white">
      {/* Left Section: Main Content Area */}
      <div className="flex-1 flex flex-col bg-[#1A1A1A] border-r border-gray-800 relative overflow-hidden">
        {/* Background Circles */}
        <div className="absolute top-1/4 left-1/4 w-24 h-24 rounded-full border-2 border-red-500 opacity-10 animate-pulse"></div>
        <div className="absolute top-1/2 right-1/4 w-32 h-32 rounded-full border-2 border-orange-400 opacity-10 animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 left-1/3 w-20 h-20 rounded-full border-2 border-gray-500 opacity-10 animate-pulse-fast"></div>
        <div className="absolute top-1/3 left-1/2 w-40 h-40 rounded-full border-2 border-red-500 opacity-10 animate-pulse"></div>
        <div className="absolute bottom-1/2 right-1/3 w-28 h-28 rounded-full border-2 border-orange-400 opacity-10 animate-pulse-slow"></div>
        <div className="absolute top-1/4 right-1/4 w-24 h-24 rounded-full border-2 border-gray-500 opacity-10 animate-pulse-fast"></div>
        <div className="absolute bottom-1/4 right-1/2 w-36 h-36 rounded-full border-2 border-red-500 opacity-10 animate-pulse"></div>
        {/* Main Content Header */}
        <div className="flex items-center p-4 bg-[#1A1A1A] border-b border-gray-800 z-10">
          <div className="flex items-center bg-[#6B46C1] rounded-full px-3 py-1 text-sm font-medium text-white">
            <Settings className="w-4 h-4 mr-2" />
            <span>OPS Ex v4</span>
            <span className="w-2 h-2 ml-2 bg-green-500 rounded-full"></span>
          </div>
          <div className="ml-4 text-sm text-gray-400">
            Analyzing: <span className="text-purple-400">{clientName}</span>
          </div>
          {/* Header Tabs */}
          <div className="flex ml-auto space-x-2">
            <button
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                mainView === "analysis"
                  ? "bg-purple-700 text-white"
                  : "bg-[#2A2A2A] text-gray-400 hover:bg-gray-700 hover:text-white"
              }`}
              onClick={() => setMainView("analysis")}
            >
              Company Painpoint Analysis
            </button>
            <button
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                mainView === "aiLab"
                  ? "bg-purple-700 text-white"
                  : "bg-[#2A2A2A] text-gray-400 hover:bg-gray-700 hover:text-white"
              }`}
              onClick={() => setMainView("aiLab")}
            >
              Gen AI Lab Assets
            </button>
          </div>
        </div>
        {/* Conditional Main Content */}
        {mainView === "analysis" ? (
          <>
            {/* Chat Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 z-10">
              {/* Loading state */}
              {isLoading && (
                <div className="flex justify-center">
                  <div className="animate-pulse text-gray-400">Analyzing {clientName}...</div>
                </div>
              )}
              {/* Error state */}
              {error && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] p-4 rounded-lg bg-red-900 text-white shadow-md">
                    <div className="flex items-center">
                      <Info className="w-5 h-5 mr-2" />
                      <span>Error analyzing company: {error}</span>
                    </div>
                  </div>
                </div>
              )}
              {/* Dynamic Chat Messages */}
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} items-start gap-3`}
                >
                  {msg.sender === "bot" && (
                    <div className="w-10 h-10 rounded-full bg-red-600 flex items-center justify-center flex-shrink-0">
                      {msg.avatar}
                    </div>
                  )}
                  <div
                    className={`p-3 rounded-lg shadow-md ${
                      msg.sender === "user"
                        ? "bg-[#6B46C1] text-white max-w-[70%]"
                        : msg.isError
                          ? "bg-red-900 text-white max-w-[80%]"
                          : "bg-[#2A2A2A] text-gray-300 max-w-full w-full border border-gray-700"
                    }`}
                  >
                    {renderMessageContent(msg)}
                  </div>
                  {msg.sender === "user" && (
                    <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      PD
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            {/* Chat Input Area */}
            <div className="sticky bottom-0 w-full p-4 bg-[#1A1A1A] border-t border-gray-800 z-20">
              {/* Quick suggestions */}
              {quickSuggestions.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                  {quickSuggestions.map((project) => (
                    <button
                      key={project.id}
                      onClick={() => handleProjectSelect(project.id)}
                      className="text-xs bg-purple-900 hover:bg-purple-800 text-white px-3 py-1 rounded-full flex items-center"
                      title={project.summary}
                    >
                      {project.name}
                      <Send className="w-3 h-3 ml-1" />
                    </button>
                  ))}
                </div>
              )}
              <div className="relative max-w-3xl mx-auto">
                <textarea
                  placeholder="Enter a prompt, or press '/' for multiple prompts..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                  rows={1}
                  className="min-h-[48px] rounded-xl resize-none p-4 border border-gray-700 shadow-inner pr-16 bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-[#1A1A1A] w-full placeholder-gray-500"
                ></textarea>
                <button
                  type="submit"
                  className="absolute w-10 h-10 top-2 right-2 bg-[#6B46C1] hover:bg-purple-700 rounded-full flex items-center justify-center shadow-md"
                  onClick={handleSendMessage}
                  disabled={inputMessage.trim() === ""}
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5 text-white" />
                </button>
              </div>
              <p className="text-xs text-gray-500 text-center mt-2">
                Iframe.ai may display inaccurate info, including about people, so double-check its responses.
              </p>
            </div>
          </>
        ) : (
          // AI Lab Assets View
          aiLabContent
        )}
      </div>
      {/* Right Section: Workspace Sidebar */}
      <div className="w-96 flex-shrink-0 bg-[#2A2A2A] border-l border-gray-800 flex flex-col">
        <div className="flex justify-between items-center p-4 border-b border-gray-800">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Code className="w-5 h-5 mr-2 text-purple-400" /> {clientName}'s Workspace
          </h2>
          <button className="text-gray-400 hover:text-white text-2xl leading-none" aria-label="Close workspace">
            &times;
          </button>
        </div>
        {/* Tabs */}
        <div className="flex border-b border-gray-800">
          <button
            className={`flex-1 py-3 text-center font-semibold transition-colors ${
              activeTab === "planner"
                ? "text-purple-400 border-b-2 border-purple-400"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => setActiveTab("planner")}
          >
            Planner
          </button>
          <button
            className={`flex-1 py-3 text-center font-semibold transition-colors ${
              activeTab === "projects"
                ? "text-purple-400 border-b-2 border-purple-400"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => setActiveTab("projects")}
          >
            Projects
          </button>
          <button
            className={`flex-1 py-3 text-center font-semibold transition-colors ${
              activeTab === "reference"
                ? "text-purple-400 border-b-2 border-purple-400"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => setActiveTab("reference")}
          >
            Reference
          </button>
          <button
            className={`flex-1 py-3 text-center font-semibold transition-colors ${
              activeTab === "coder" ? "text-purple-400 border-b-2 border-purple-400" : "text-gray-400 hover:text-white"
            }`}
            onClick={() => setActiveTab("coder")}
          >
            Coder
          </button>
        </div>
        {/* Dynamic Content based on activeTab */}
        <div className="flex-1 overflow-y-auto p-6">{tabContent[activeTab]}</div>
        {/* Help Button */}
        <div className="p-4 border-t border-gray-800 flex justify-end">
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full flex items-center shadow-lg">
            <HelpCircle className="w-5 h-5 mr-2" /> Help
          </button>
        </div>
      </div>
    </div>
  )
}
