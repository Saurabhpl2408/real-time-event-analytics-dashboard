import { useState } from 'react'
import { X, Loader2, Shield } from 'lucide-react'
import { useAuthStore } from './../stores/authStore'
import apiService from './../services/api'

export default function Setup2FAModal({ onClose }) {
  const token = useAuthStore((state) => state.token)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [step, setStep] = useState('info') // 'info', 'qr', 'verify'
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [error, setError] = useState('')

  const handleSetup = async () => {
    setIsSubmitting(true)
    setError('')

    try {
      const result = await apiService.setup2FA(token)
      setQrCode(result.qrCode)
      setSecret(result.secret)
      setStep('qr')
    } catch (error) {
      setError(error.message || 'Failed to setup 2FA')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      await apiService.verify2FA({ code: verificationCode }, token)
      alert('Two-factor authentication enabled successfully')
      onClose()
    } catch (error) {
      setError('Invalid verification code. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-light dark:glass rounded-xl shadow-2xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Two-Factor Authentication
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Info Step */}
        {step === 'info' && (
          <div className="space-y-4">
            <div className="flex items-center justify-center mb-4">
              <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                <Shield className="w-12 h-12 text-blue-600 dark:text-blue-400" />
              </div>
            </div>

            <p className="text-gray-600 dark:text-gray-400 text-center">
              Two-factor authentication adds an extra layer of security to your account. You'll need an authenticator app to continue.
            </p>

            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Recommended Apps:</h3>
              <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <li>• Google Authenticator</li>
                <li>• Microsoft Authenticator</li>
                <li>• Authy</li>
              </ul>
            </div>

            <button
              onClick={handleSetup}
              disabled={isSubmitting}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Setting up...</span>
                </>
              ) : (
                <span>Continue Setup</span>
              )}
            </button>
          </div>
        )}

        {/* QR Code Step */}
        {step === 'qr' && (
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400 text-center text-sm">
              Scan this QR code with your authenticator app:
            </p>

            <div className="bg-white p-4 rounded-lg flex items-center justify-center">
              {qrCode ? (
                <img src={qrCode} alt="2FA QR Code" className="w-48 h-48" />
              ) : (
                <div className="w-48 h-48 bg-gray-200 dark:bg-gray-700 animate-pulse rounded-lg" />
              )}
            </div>

            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
              <p className="text-xs text-gray-600 dark:text-gray-400 text-center mb-2">
                Or enter this code manually:
              </p>
              <p className="text-center font-mono text-sm text-gray-900 dark:text-white break-all">
                {secret}
              </p>
            </div>

            <button
              onClick={() => setStep('verify')}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all"
            >
              Continue to Verification
            </button>
          </div>
        )}

        {/* Verify Step */}
        {step === 'verify' && (
          <form onSubmit={handleVerify} className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400 text-center text-sm">
              Enter the 6-digit code from your authenticator app:
            </p>

            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              required
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white text-center text-2xl font-mono tracking-widest"
            />

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => setStep('qr')}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={isSubmitting || verificationCode.length !== 6}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  <span>Verify & Enable</span>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}