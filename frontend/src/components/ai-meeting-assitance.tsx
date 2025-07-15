"use client"

import { useState, useEffect } from "react"
import {
  Video,
  MessageSquare,
  CheckCircle2,
  XCircle,
  Loader2,
  Users,
  Clock,
  ChevronRight,
  ChevronDown,
  Calendar,
  Mic,
  MicOff,
  ScreenShare,
  MoreVertical,
  PhoneOff
} from "lucide-react"

export default function AiMeetingAssistant() {
  const [phase, setPhase] = useState<
    | "connecting"
    | "ms_teams_calendar_view"
    | "processing_info"
    | "notifying"
    | "permission_granted"
    | "permission_denied"
  >("connecting")
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    let timer: NodeJS.Timeout

    const resetToConnecting = () => {
      timer = setTimeout(() => {
        setPhase("connecting")
      }, 5000) // Wait 5 seconds after permission status before resetting
    }

    if (phase === "connecting") {
      timer = setTimeout(() => {
        setPhase("ms_teams_calendar_view")
      }, 2500) // Simulate connection time
    } else if (phase === "ms_teams_calendar_view") {
      timer = setTimeout(() => {
        setPhase("processing_info")
      }, 5000) // Simulate reading calendar time
    } else if (phase === "processing_info") {
      timer = setTimeout(() => {
        setPhase("notifying")
      }, 3500) // Simulate processing time
    } else if (phase === "permission_granted" || phase === "permission_denied") {
      resetToConnecting() // Trigger reset after permission is handled
    }

    return () => clearTimeout(timer)
  }, [phase])

  const handlePermission = (granted: boolean) => {
    setPhase(granted ? "permission_granted" : "permission_denied")
  }

  const toggleExpand = () => {
    setIsExpanded(!isExpanded)
  }

  return (
    <div className="relative w-full max-w-xl mx-auto bg-white rounded-xl shadow-2xl overflow-hidden border border-gray-200 transition-all duration-300">
      {/* Video Call Header */}
      <div className="flex items-center justify-between bg-gradient-to-r bg-yellow-400 p-4 text-white">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Video className="h-6 w-6" />
            <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-blue-900"></span>
          </div>
          <div>
            <h2 className="text-lg font-bold">AI Meeting Assistant</h2>
            <p className="text-xs opacity-80 flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${phase === "connecting" ? "bg-yellow-400" : "bg-green-400"}`}></span>
              {phase === "connecting" ? "Connecting..." : "Active"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1 rounded-full hover:bg-blue-800 transition-colors">
            <Mic className="h-4 w-4" />
          </button>
          <button className="p-1 rounded-full hover:bg-blue-800 transition-colors">
            <ScreenShare className="h-4 w-4" />
          </button>
          <button className="p-1 rounded-full hover:bg-blue-800 transition-colors">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* AI Agent "Video" Area */}
      <div className="relative bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-6 min-h-[220px]">
        {/* AI Avatar with pulse animation */}
        <div className="relative group">
          <div className="absolute inset-0 rounded-full bg-blue-500/20 blur-md animate-pulse-slow -z-10"></div>
          <div className="relative h-32 w-32 rounded-full border-4 border-blue-400 ring-4 ring-blue-500/30 flex items-center justify-center overflow-hidden transition-transform duration-300 group-hover:scale-105">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/30 to-purple-600/20 rounded-full"></div>
            <div className="text-5xl font-bold text-white drop-shadow-lg">AI</div>
          </div>
        </div>
        
        {/* Status indicator */}
        <div className="absolute bottom-4 right-4 bg-green-500 text-white text-xs px-3 py-1 rounded-full flex items-center gap-1 shadow-md">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
          </span>
          <span className="font-medium">Live</span>
        </div>
        
        {/* Expand/collapse button */}
        <button 
          onClick={toggleExpand}
          className={`absolute top-4 right-4 text-gray-300 hover:text-white transition-transform ${isExpanded ? "rotate-180" : ""}`}
        >
          <ChevronDown className="h-5 w-5" />
        </button>
      </div>

      {/* Expanded details panel */}
      {isExpanded && (
        <div className="bg-gray-50 border-t border-gray-200 p-4">
          <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <Clock className="h-3 w-3 text-blue-600" />
              <span>Connection time: 2.4s</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-3 w-3 text-blue-600" />
              <span>Client detected: 1</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-3 w-3 text-blue-600" />
              <span>Upcoming meetings: 3</span>
            </div>
            <div className="flex items-center gap-2">
              <Loader2 className="h-3 w-3 text-blue-600 animate-spin" />
              <span>Processing speed: 1.2x</span>
            </div>
          </div>
        </div>
      )}

      {/* Conversation Content / MS Teams View */}
      <div className="transition-all duration-300">
        {phase === "ms_teams_calendar_view" ? (
          <div className="p-6 bg-gray-800 text-white min-h-[300px] flex flex-col items-center text-center space-y-6">
            <div className="flex items-center gap-3 text-blue-400 animate-fade-in">
              <div className="bg-blue-900/30 p-2 rounded-lg">
                <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.5 6.5C2.5 4.019 4.519 2 7 2h10c2.481 0 4.5 2.019 4.5 4.5v10c0 2.481-2.019 4.5-4.5 4.5H7c-2.481 0-4.5-2.019-4.5-4.5v-10zM7 3.5c-1.654 0-3 1.346-3 3v10c0 1.654 1.346 3 3 3h10c1.654 0 3-1.346 3-3v-10c0-1.654-1.346-3-3-3H7z"/>
                  <path d="M5.5 7C5.5 6.724 5.724 6.5 6 6.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5H6c-.276 0-.5-.224-.5-.5V7zM6 7.5v2h2.5v-2H6zM5.5 14c0-.276.224-.5.5-.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5H6c-.276 0-.5-.224-.5-.5v-3zM6 14.5v2h2.5v-2H6zM12 6.5c-.276 0-.5.224-.5.5v3c0 .276.224.5.5.5h3c.276 0 .5-.224.5-.5V7c0-.276-.224-.5-.5-.5h-3zM12 7.5h2.5v2H12v-2zM11.5 14c0-.276.224-.5.5-.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5h-3c-.276 0-.5-.224-.5-.5v-3zM12 14.5h2.5v2H12v-2z"/>
                </svg>
              </div>
              <p className="text-xl font-semibold">
                Accessing Microsoft Teams Calendar...
              </p>
            </div>

            <div className="w-full max-w-md bg-gray-900 rounded-xl shadow-lg overflow-hidden border border-gray-700 transform transition-all duration-300 hover:scale-[1.01]">
              {/* Calendar Header */}
              <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-700/50">
                <span className="text-sm font-medium text-gray-300">Today, July 15</span>
                <span className="text-sm font-medium text-gray-300">Thursday, July 17</span>
              </div>
              
              {/* Calendar Grid */}
              <div className="grid grid-cols-[60px_1fr] text-left text-sm">
                {/* Time Column */}
                <div className="flex flex-col border-r border-gray-700">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      className="h-12 flex items-center justify-end pr-2 text-gray-400 border-b border-gray-700 last:border-b-0"
                    >
                      {`${9 + i}:00`}
                    </div>
                  ))}
                </div>
                
                {/* Events Column */}
                <div className="relative p-2">
                  {/* Dummy events */}
                  <div className="absolute top-[20px] left-2 right-2 h-8 bg-blue-600/80 rounded-md p-1 text-xs font-medium flex items-center justify-between">
                    <span>Team Sync</span>
                    <ChevronRight className="h-3 w-3" />
                  </div>
                  <div className="absolute top-[70px] left-2 right-2 h-10 bg-green-600/80 rounded-md p-1 text-xs font-medium flex items-center justify-between">
                    <span>Project Review</span>
                    <ChevronRight className="h-3 w-3" />
                  </div>

                  {/* Highlighted Meeting */}
                  <div className="absolute top-[140px] left-2 right-2 h-[60px] bg-gradient-to-r from-purple-600 to-purple-700 rounded-md p-2 text-sm font-bold flex flex-col justify-center shadow-lg border-2 border-purple-400/50">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      <span>Client X Meeting</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-normal text-purple-200 mt-1">
                      <Clock className="h-3 w-3" />
                      <span>10:00 AM - 11:00 AM</span>
                    </div>
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex">
                      {[...Array(3)].map((_, i) => (
                        <div 
                          key={i}
                          className="w-1 h-1 bg-purple-300 rounded-full mx-[1px] animate-bounce"
                          style={{ animationDelay: `${i * 0.1}s` }}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="absolute bottom-[20px] left-2 right-2 h-8 bg-yellow-600/80 rounded-md p-1 text-xs font-medium flex items-center justify-between">
                    <span>1:1 with Manager</span>
                    <ChevronRight className="h-3 w-3" />
                  </div>
                </div>
              </div>
            </div>
            
            <p className="text-sm text-gray-400 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Extracting relevant meeting details...
            </p>
          </div>
        ) : (
          <div className="p-6 bg-white space-y-6">
            {phase === "connecting" && (
              <div className="flex items-start gap-4 animate-fade-in">
                <div className="relative">
                  <Loader2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-1 animate-spin" />
                  <div className="absolute inset-0 rounded-full bg-blue-100 animate-ping opacity-30"></div>
                </div>
                <div>
                  <p className="text-base text-gray-800 leading-relaxed font-medium">
                    Establishing secure connection with your AI assistant...
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Authenticating with your Microsoft 365 account
                  </p>
                </div>
              </div>
            )}

            {phase === "processing_info" && (
              <div className="flex items-start gap-4 animate-fade-in">
                <div className="relative">
                  <Loader2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-1 animate-spin" />
                  <div className="absolute inset-0 rounded-full bg-blue-100 animate-ping opacity-30"></div>
                </div>
                <div>
                  <p className="text-base text-gray-800 leading-relaxed font-medium">
                    Analyzing meeting details and client information...
                  </p>
                  <div className="mt-2 w-full bg-gray-100 rounded-full h-1.5">
                    <div 
                      className="bg-blue-600 h-1.5 rounded-full animate-progress" 
                      style={{ width: '70%' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {phase === "notifying" && (
              <div className="space-y-6 animate-fade-in">
                <div className="flex items-start gap-4">
                  <div className="bg-blue-100 p-2 rounded-full">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-base text-gray-800 leading-relaxed font-medium">
                      Greetings! I've reviewed your schedule and found:
                    </p>
                    <div className="mt-3 bg-blue-50 p-3 rounded-lg border border-blue-100">
                      <div className="flex items-center gap-2 text-blue-800">
                        <Calendar className="h-4 w-4" />
                        <span className="font-semibold">Client X Meeting</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-blue-700 mt-1">
                        <Clock className="h-3 w-3" />
                        <span>Thursday, July 17 • 10:00 AM - 11:00 AM</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-blue-700 mt-1">
                        <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M2.5 6.5C2.5 4.019 4.519 2 7 2h10c2.481 0 4.5 2.019 4.5 4.5v10c0 2.481-2.019 4.5-4.5 4.5H7c-2.481 0-4.5-2.019-4.5-4.5v-10zM7 3.5c-1.654 0-3 1.346-3 3v10c0 1.654 1.346 3 3 3h10c1.654 0 3-1.346 3-3v-10c0-1.654-1.346-3-3-3H7z"/>
                          <path d="M5.5 7C5.5 6.724 5.724 6.5 6 6.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5H6c-.276 0-.5-.224-.5-.5V7zM6 7.5v2h2.5v-2H6zM5.5 14c0-.276.224-.5.5-.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5H6c-.276 0-.5-.224-.5-.5v-3zM6 14.5v2h2.5v-2H6zM12 6.5c-.276 0-.5.224-.5.5v3c0 .276.224.5.5.5h3c.276 0 .5-.224.5-.5V7c0-.276-.224-.5-.5-.5h-3zM12 7.5h2.5v2H12v-2zM11.5 14c0-.276.224-.5.5-.5h3c.276 0 .5.224.5.5v3c0 .276-.224.5-.5.5h-3c-.276 0-.5-.224-.5-.5v-3zM12 14.5h2.5v2H12v-2z"/>
                        </svg>
                        <span>Microsoft Teams</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <div className="bg-blue-100 p-2 rounded-full">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-base text-gray-800 leading-relaxed">
                      As your AI Assistant, I can proactively reach out to the Client POC to gather insights on their expectations and key agenda points.
                    </p>
                    <p className="text-base text-gray-800 leading-relaxed font-medium mt-2">
                      Would you like me to proceed with this?
                    </p>
                    
                    <div className="flex gap-3 justify-end mt-4">
                      <button
                        onClick={() => handlePermission(false)}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-gray-300 bg-white hover:bg-gray-50 h-10 px-5 py-2 text-base font-semibold text-gray-700"
                      >
                        <XCircle className="h-5 w-5 mr-2 text-red-500" />
                        No, thanks
                      </button>
                      <button
                        onClick={() => handlePermission(true)}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 h-10 px-5 py-2 text-base font-semibold shadow-md"
                      >
                        <CheckCircle2 className="h-5 w-5 mr-2 text-white" />
                        Yes, proceed
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {phase === "permission_granted" && (
              <div className="text-base text-green-700 flex items-start gap-4 p-4 bg-green-50 rounded-lg border border-green-200 animate-fade-in">
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-medium">
                    Understood. I will now initiate contact with the Client POC.
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    Estimated response time: 2-4 hours
                  </p>
                </div>
              </div>
            )}

            {phase === "permission_denied" && (
              <div className="text-base text-gray-700 flex items-start gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200 animate-fade-in">
                <XCircle className="h-6 w-6 text-gray-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-medium">
                    Acknowledged. I won't contact the Client POC.
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    You can ask me to do this later if you change your mind.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Meeting controls footer */}
      <div className="bg-gray-50 border-t border-gray-200 p-3 flex justify-between items-center">
        <button className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-200 transition-colors">
          <Mic className="h-5 w-5" />
        </button>
        <button className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-200 transition-colors">
          <ScreenShare className="h-5 w-5" />
        </button>
        <button className="bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors shadow-md">
          <PhoneOff className="h-5 w-5" />
        </button>
        <button className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-200 transition-colors">
          <MoreVertical className="h-5 w-5" />
        </button>
      </div>

      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
          }
          50% {
            transform: translateY(-10px) translateX(5px);
          }
        }
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.6;
          }
          50% {
            opacity: 0.9;
          }
        }
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes progress {
          from {
            width: 0%;
          }
          to {
            width: 70%;
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 3s infinite ease-in-out;
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out forwards;
        }
        .animate-progress {
          animation: progress 1.5s ease-out forwards;
        }
      `}</style>
    </div>
  )
}