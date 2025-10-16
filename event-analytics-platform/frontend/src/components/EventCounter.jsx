function EventCounter({ title, count, icon }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800">
            {count.toLocaleString()}
          </p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )
}

export default EventCounter