import React, { useState, useEffect, useRef } from 'react'
import { MessageCircle, Briefcase, Brain, Settings, Send, User, Bot, CreditCard } from 'lucide-react'

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:5000'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState(null)
  const [activeSection, setActiveSection] = useState('chat')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleLogin = async () => {
    try {
      // Simulate Google OAuth login
      const mockUser = {
        email: 'user@example.com',
        name: 'Demo User',
        google_id: 'demo_user_123'
      }

      const response = await fetch(`${API_BASE}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockUser)
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
        setIsLoggedIn(true)
        localStorage.setItem('jarvis_token', data.token)
      }
    } catch (error) {
      console.error('Login error:', error)
      // Fallback for demo
      setUser({
        id: 'demo_user',
        email: 'user@example.com',
        name: 'Demo User',
        credits: 500
      })
      setIsLoggedIn(true)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    
    const messageToSend = inputMessage
    setInputMessage('')

    try {
      const token = localStorage.getItem('jarvis_token')
      const response = await fetch(`${API_BASE}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: conversationId
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const jarvisMessage = {
          id: Date.now() + 1,
          content: data.response,
          sender: 'jarvis',
          timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, jarvisMessage])
        setConversationId(data.conversation_id)
        
        // Update user credits
        if (user) {
          setUser(prev => ({ ...prev, credits: data.remaining_credits }))
        }
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Fallback response for demo
      const jarvisMessage = {
        id: Date.now() + 1,
        content: "Natuurlijk meneer, ik voer dit direct uit ondanks mijn twijfels over de methode. (Demo mode - API niet beschikbaar)",
        sender: 'jarvis',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, jarvisMessage])
      
      if (user) {
        setUser(prev => ({ ...prev, credits: Math.max(0, prev.credits - 2) }))
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full mx-4 border border-white/20">
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mx-auto mb-6">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Jarvis</h1>
            <p className="text-blue-200 mb-8">Google Workspace AI Assistant</p>
            <button
              onClick={handleLogin}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              Login with Google
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Jarvis</h1>
              <p className="text-sm text-gray-500">AI Assistant</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-2">
            <button
              onClick={() => setActiveSection('chat')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeSection === 'chat' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <MessageCircle className="w-5 h-5" />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setActiveSection('workspace')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeSection === 'workspace' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Briefcase className="w-5 h-5" />
              <span>Workspace</span>
            </button>
            <button
              onClick={() => setActiveSection('ai-tools')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeSection === 'ai-tools' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Brain className="w-5 h-5" />
              <span>AI Tools</span>
            </button>
          </div>
        </nav>

        {/* User Info */}
        <div className="p-4 border-t">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-gray-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-800">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <CreditCard className="w-4 h-4 text-green-500" />
            <span className="text-gray-600">Credits: {user?.credits || 0}</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {activeSection === 'chat' && (
          <>
            <div className="bg-white border-b px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800">Chat with Jarvis</h2>
              <p className="text-sm text-gray-500">Your AI assistant with personality</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">Start a conversation</h3>
                  <p className="text-gray-400">Ask Jarvis anything about your Google Workspace</p>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.sender === 'jarvis' && (
                        <Bot className="w-4 h-4 mt-1 text-blue-500" />
                      )}
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 text-blue-500" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="bg-white border-t p-4">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
              </div>
            </div>
          </>
        )}

        {activeSection === 'workspace' && (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Google Workspace</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Gmail</h3>
                <p className="text-gray-600 mb-4">Manage your emails with AI assistance</p>
                <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  Open Gmail
                </button>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Calendar</h3>
                <p className="text-gray-600 mb-4">Schedule and manage appointments</p>
                <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                  Open Calendar
                </button>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Drive</h3>
                <p className="text-gray-600 mb-4">Access and organize your files</p>
                <button className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">
                  Open Drive
                </button>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'ai-tools' && (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">AI Tools</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Smart Compose</h3>
                <p className="text-gray-600 mb-4">AI-powered writing assistance</p>
                <button className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                  Start Composing
                </button>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Summarize</h3>
                <p className="text-gray-600 mb-4">Summarize long documents</p>
                <button className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600">
                  Summarize Text
                </button>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Workspace Analysis</h3>
                <p className="text-gray-600 mb-4">Analyze your productivity</p>
                <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                  Analyze Now
                </button>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-2">Translate</h3>
                <p className="text-gray-600 mb-4">Translate text with Jarvis humor</p>
                <button className="bg-teal-500 text-white px-4 py-2 rounded hover:bg-teal-600">
                  Translate
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

