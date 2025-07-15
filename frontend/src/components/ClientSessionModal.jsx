
import { useState } from "react"

export default function ClientSessionModal({ isOpen, onClose, onStartSession }) {
  const [clientNameInput, setClientNameInput] = useState("")

  const handleSubmit = () => {
    if (clientNameInput.trim()) {
      onStartSession(clientNameInput.trim())
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70">
      <div className="relative w-full max-w-md p-6 rounded-lg shadow-lg bg-[#2A2A2A] text-white border border-gray-700">
        <div className="flex justify-between items-center pb-4 border-b border-gray-600 mb-4">
          <h2 className="text-xl font-semibold text-white">Attend the Client</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none" aria-label="Close">
            &times;
          </button>
        </div>
        <p className="text-gray-400 mb-4">Enter the client's name to start a private session.</p>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <label htmlFor="clientName" className="text-right text-gray-300">
              Client Name
            </label>
            <input
              id="clientName"
              type="text"
              value={clientNameInput}
              onChange={(e) => setClientNameInput(e.target.value)}
              className="col-span-3 flex h-10 w-full rounded-md border border-gray-600 bg-[#3A3A3A] px-3 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-[#2A2A2A]"
              placeholder="e.g., Acme Corp"
            />
          </div>
        </div>
        <div className="flex justify-end pt-4 border-t border-gray-600 mt-4">
          <button
            onClick={handleSubmit}
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-[#2A2A2A] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 bg-red-600 hover:bg-red-700 text-white"
          >
            Start Session
          </button>
        </div>
      </div>
    </div>
  )
}
