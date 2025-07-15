export default function SuggestionCard({ title, description, onClick }) {
    return (
      <div
        className="bg-[#2A2A2A] p-4 rounded-lg shadow-md cursor-pointer hover:bg-[#3A3A3A] transition-colors"
        onClick={onClick}
      >
        <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
    )
  }
  