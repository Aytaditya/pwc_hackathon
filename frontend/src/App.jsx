import { useState } from "react"
import Header from "./components/Header"
import ClientSessionModal from "./components/ClientSessionModal"
import Chatbot from "./components/Chatbot"
import { Bot } from "lucide-react"

export default function Page() {
  const [isClientSessionActive, setIsClientSessionActive] = useState(false)
  const [showClientModal, setShowClientModal] = useState(false)
  const [clientName, setClientName] = useState("")

  const handleStartClientSession = (name) => {
    setClientName(name)
    setIsClientSessionActive(true)
    setShowClientModal(false)
    // In a real app, you'd call your backend /analyze-company here
    console.log(`Starting session for client: ${name}`)
  }

  if (isClientSessionActive) {
    return <Chatbot clientName={clientName} />
  }

  return (
    <div className="min-h-screen bg-[#1A1A1A] text-white flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col items-center justify-center p-4 relative overflow-hidden">
        {/* Background Circles - Enhanced for visual appeal */}
        <div className="absolute top-1/4 left-1/4 w-24 h-24 rounded-full border-2 border-red-500 opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 right-1/4 w-32 h-32 rounded-full border-2 border-orange-400 opacity-20 animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 left-1/3 w-20 h-20 rounded-full border-2 border-gray-500 opacity-20 animate-pulse-fast"></div>
        <div className="absolute top-1/3 left-1/2 w-40 h-40 rounded-full border-2 border-red-500 opacity-20 animate-pulse"></div>
        <div className="absolute bottom-1/2 right-1/3 w-28 h-28 rounded-full border-2 border-orange-400 opacity-20 animate-pulse-slow"></div>
        <div className="absolute top-1/4 right-1/4 w-24 h-24 rounded-full border-2 border-gray-500 opacity-20 animate-pulse-fast"></div>
        <div className="absolute bottom-1/4 right-1/2 w-36 h-36 rounded-full border-2 border-red-500 opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 w-56 h-56 rounded-full border-2 border-orange-400 opacity-10 animate-pulse-slow transform -translate-x-1/2 -translate-y-1/2"></div>

        <h1 className="text-5xl font-extrabold mb-16 text-center z-10 tracking-tight">
          PwC <span className="text-yellow-400">Gen AI Experience Lab</span> Internal Tool
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-4xl w-full z-10">
          {/* Card 1: Attend the Client */}
          <div
            className="bg-[#2A2A2A] p-8 rounded-xl shadow-2xl cursor-pointer hover:bg-[#3A3A3A] transition-all duration-300 ease-in-out transform hover:-translate-y-2 flex flex-col items-center text-center border border-gray-700"
            onClick={() => setShowClientModal(true)}
          >
            <div className="w-20 h-20 rounded-full bg-red-600 flex items-center justify-center mb-6 shadow-lg">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold mb-3 text-white">Attend the Client</h2>
            <p className="text-gray-400 text-lg">
              Initiate a personalized AI session tailored to a specific client's needs and data.
            </p>
          </div>

          {/* Card 2: Start a New Session */}
          <div className="bg-[#2A2A2A] p-8 rounded-xl shadow-2xl flex flex-col items-center text-center border border-gray-700">
            <div className="w-20 h-20 rounded-full bg-orange-500 flex items-center justify-center mb-6 shadow-lg">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold mb-3 text-white">Start a New Session</h2>
            <p className="text-gray-400 text-lg">
              Begin a general AI exploration without specific client details for broader queries.
            </p>
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
    </div>
  )
}
