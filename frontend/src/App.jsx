import { useState } from "react"
import Header from "./components/Header"
import ClientSessionModal from "./components/ClientSessionModal"
import Chatbot from "./components/Chatbot"
import { Bot, Sparkles, Users, PhoneOutgoing, CalendarCheck } from "lucide-react"
import AiMeetingAssistant from "./components/ai-meeting-assitance"

export default function Page() {
  const [isClientSessionActive, setIsClientSessionActive] = useState(false)
  const [showClientModal, setShowClientModal] = useState(false)
  const [clientName, setClientName] = useState("")
  const [hoveredCard, setHoveredCard] = useState(null)

  const handleStartClientSession = (name) => {
    setClientName(name)
    setIsClientSessionActive(true)
    setShowClientModal(false)
    console.log(`Starting session for client: ${name}`)
  }

  if (isClientSessionActive) {
    return <Chatbot clientName={clientName} />
  }

  return (
    <div className="min-h-screen bg-[#1A1A1A] text-white flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col items-center p-4 relative overflow-hidden">
        {/* Animated background elements */}
        <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
          {[...Array(12)].map((_, i) => (
            <div 
              key={i}
              className="absolute rounded-full border border-[#eb8c00]/10"
              style={{
                width: `${Math.random() * 300 + 100}px`,
                height: `${Math.random() * 300 + 100}px`,
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                animation: `float ${Math.random() * 20 + 10}s infinite ease-in-out`,
                opacity: Math.random() * 0.3 + 0.1,
                borderWidth: Math.random() > 0.5 ? '1px' : '2px',
                borderColor: Math.random() > 0.5 ? `rgba(235, 140, 0, ${Math.random() * 0.3})` : `rgba(224, 48, 30, ${Math.random() * 0.3})`
              }}
            />
          ))}
        </div>

        <div className="relative z-10 w-full max-w-7xl mx-auto px-4 flex flex-col lg:flex-row gap-12">
          {/* Left Section - Heading and Cards */}
          <div className="lg:w-1/2">
            {/* Hero section */}
            <div className="text-left mb-16 mt-8">
              <div className="inline-flex items-center bg-yellow-400/10 px-4 py-2 rounded-full mb-6 border border-yellow-400/30">
                <Sparkles className="w-5 h-5 text-yellow-400 mr-2" />
                <span className="text-yellow-400 font-medium">PwC Internal Tool</span>
              </div>
              <h1 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-yellow-400">
                Gen AI <span className="text-yellow-400">Experience Lab</span>
              </h1>
              <p className="text-xl text-gray-400">
                Transform client engagements with AI-powered insights and personalized experiences.
              </p>
            </div>

            {/* Feature cards */}
            <div className="grid grid-cols-1 gap-6 w-full">
              {/* Card 1: Attend the Client */}
              <div
                className={`bg-gradient-to-br from-[#2A2A2A] to-[#1E1E1E] p-8 rounded-2xl shadow-lg cursor-pointer transition-all duration-300 ease-in-out transform hover:-translate-y-2 flex flex-col items-start text-left border border-gray-800 hover:border-yellow-400/30 relative overflow-hidden ${hoveredCard === 1 ? 'ring-2 ring-yellow-400/50' : ''}`}
                onClick={() => setShowClientModal(true)}
                onMouseEnter={() => setHoveredCard(1)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-yellow-400/5 to-red-600/5 opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                <div className="w-14 h-14 rounded-xl bg-red-600/20 flex items-center justify-center mb-6 border border-red-600/30">
                  <Users className="w-6 h-6 text-red-400" />
                </div>
                <h2 className="text-2xl font-bold mb-3 text-white">Attend the Client</h2>
                <p className="text-gray-400 mb-4">
                  Initiate a personalized AI session tailored to a specific client's needs and data.
                </p>
                <div className="mt-auto pt-4 text-yellow-400 font-medium flex items-center">
                  Start session
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
              </div>

              {/* Card 2: Initiate AI Agent */}
              <div
                className={`bg-gradient-to-br from-[#2A2A2A] to-[#1E1E1E] p-8 rounded-2xl shadow-lg cursor-pointer transition-all duration-300 ease-in-out transform hover:-translate-y-2 flex flex-col items-start text-left border border-gray-800 hover:border-yellow-400/30 relative overflow-hidden ${hoveredCard === 2 ? 'ring-2 ring-yellow-400/50' : ''}`}
                onMouseEnter={() => setHoveredCard(2)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-yellow-400/5 to-red-600/5 opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                <div className="w-14 h-14 rounded-xl bg-orange-500/20 flex items-center justify-center mb-6 border border-orange-500/30">
                  <PhoneOutgoing className="w-6 h-6 text-orange-400" />
                </div>
                <h2 className="text-2xl font-bold mb-3 text-white">Initiate AI Agent</h2>
                <p className="text-gray-400 mb-4">
                  AI Agent will contact client POC and gather insights on their expectations ahead of meeting.
                </p>
                <div className="mt-auto pt-4 text-yellow-400 font-medium flex items-center">
                  Configure agent
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Right Section - Demo Video */}
          <div className="lg:w-1/2 flex flex-col justify-center">
            <div className="sticky top-24">
              <div className="inline-flex items-center bg-gradient-to-r from-yellow-400/10 to-red-600/10 px-6 py-3 rounded-full mb-6 border border-gray-700 backdrop-blur-sm">
                <CalendarCheck className="w-5 h-5 text-yellow-400 mr-2" />
                <h3 className="text-xl font-semibold text-white">
                  Watch a demo of agent in action with a component
                </h3>
              </div>
              
              <div className="w-full overflow-hidden shadow-2xl rounded-xl">
                <AiMeetingAssistant />
              </div>
            </div>
          </div>
        </div>
      </main>

      {showClientModal && (
        <ClientSessionModal
          isOpen={showClientModal}
          onClose={() => setShowClientModal(false)}
          onStartSession={handleStartClientSession}
        />
      )}

      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
          }
          50% {
            transform: translateY(-20px) translateX(10px);
          }
        }
        .floating-circle {
          animation: float 15s infinite ease-in-out;
        }
        .floating-circle-2 {
          animation: float 20s infinite ease-in-out;
        }
        .floating-circle-3 {
          animation: float 25s infinite ease-in-out;
        }
      `}</style>
    </div>
  )
}