import { useState } from 'react'
import { useAuthStore } from './../stores/authStore'
import { User, Key, Shield } from 'lucide-react'
import ChangePasswordModal from './../modals/ChangePasswordModal'
import Setup2FAModal from './../modals/Setup2FAModal'
import apiService from './../services/api'

export default function Settings() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [show2FAModal, setShow2FAModal] = useState(false)

  const handleGenerateApiKey = async () => {
    try {
      const result = await apiService.generateApiKey(token)
      alert(`API Key generated: ${result.apiKey}\n\nPlease save this key securely. You won't be able to see it again.`)
    } catch (error) {
      alert('Failed to generate API key: ' + error.message)
    }
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your account and preferences
        </p>
      </div>

      {/* User info */}
      <div className="glass-light dark:glass rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Account Information
          </h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-600 dark:text-gray-400">Username</label>
            <p className="text-lg font-medium text-gray-900 dark:text-white">{user?.username}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600 dark:text-gray-400">Email</label>
            <p className="text-lg font-medium text-gray-900 dark:text-white">{user?.email}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600 dark:text-gray-400">Role</label>
            <span className="inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 text-sm font-medium capitalize">
              {user?.role}
            </span>
          </div>
        </div>
      </div>

      {/* API Key */}
      <div className="glass-light dark:glass rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Key className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            API Key
          </h2>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Use API keys for programmatic access to the analytics platform
        </p>

        <button 
          onClick={handleGenerateApiKey}
          className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all"
        >
          Generate New API Key
        </button>
      </div>

      {/* Security */}
      <div className="glass-light dark:glass rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Security
          </h2>
        </div>

        <div className="space-y-3">
          <button 
            onClick={() => setShowPasswordModal(true)}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <p className="font-medium text-gray-900 dark:text-white">Change Password</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Update your password</p>
          </button>
          
          <button 
            onClick={() => setShow2FAModal(true)}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <p className="font-medium text-gray-900 dark:text-white">Two-Factor Authentication</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Add an extra layer of security</p>
          </button>
        </div>
      </div>

      {/* Modals */}
      {showPasswordModal && (
        <ChangePasswordModal onClose={() => setShowPasswordModal(false)} />
      )}
      {show2FAModal && (
        <Setup2FAModal onClose={() => setShow2FAModal(false)} />
      )}
    </div>
  )
}