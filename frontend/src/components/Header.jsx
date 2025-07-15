import { Calendar} from "lucide-react"

export default function Header() {
  return (
    <header className="flex items-center justify-between p-4 bg-[#1A1A1A] border-b border-gray-700">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          {/* Placeholder for PwC logo */}
          <span className="text-xl font-bold text-white">pwc</span>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button className="flex items-center text-gray-400 hover:text-white transition-colors cursor-pointer">
          <Calendar className="w-4 h-4 mr-1" />
          <span>Google Calendar Integration</span>
        </button>
        <div className="w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center text-black font-bold">
          GG
        </div>
      </div>
    </header>
  )
}