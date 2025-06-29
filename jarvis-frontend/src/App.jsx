import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { ScrollArea } from '@/components/ui/scroll-area.jsx';
import { Separator } from '@/components/ui/separator.jsx';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Settings, 
  CreditCard, 
  FileText, 
  Mail, 
  Calendar, 
  FolderOpen,
  Loader2,
  Zap,
  Brain,
  Sparkles
} from 'lucide-react';
import './App.css';

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [credits, setCredits] = useState(500);
  const [currentView, setCurrentView] = useState('chat');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: 'Goedemorgen meneer, ik ben Jarvis, uw AI-assistent voor Google Workspace. Hoe kan ik u van dienst zijn vandaag?',
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Mock authentication (in real app, this would use Google OAuth)
  const handleLogin = () => {
    setIsAuthenticated(true);
    setUser({
      name: 'Test User',
      email: 'test@example.com',
      avatar: null
    });
    setCredits(500);
  };

  // Send message to Jarvis
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // In a real app, this would call the actual API
      // For demo purposes, we'll simulate Jarvis responses
      const response = await simulateJarvisResponse(inputMessage);
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setCredits(prev => Math.max(0, prev - response.creditsUsed));
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Meneer, ik ondervind technische moeilijkheden. Wellicht kunt u het later opnieuw proberen.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate Jarvis responses (in real app, this calls the backend API)
  const simulateJarvisResponse = async (message) => {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    const responses = [
      "Meneer, ik heb uw verzoek verwerkt, hoewel ik me afvraag of dit de meest efficiënte aanpak is.",
      "Natuurlijk meneer, ik voer dit direct uit ondanks mijn twijfels over de methode.",
      "Meneer, zoals u wenst, hoewel een meer conventionele benadering wellicht beter zou zijn.",
      "Uiteraard meneer, ik zal dit regelen ondanks dat dit niet mijn eerste keuze zou zijn.",
      "Meneer, ik heb de taak voltooid, hoewel ik persoonlijk een andere route zou suggereren."
    ];
    
    // Special responses for specific inputs
    if (message.toLowerCase().includes('dokter') || message.toLowerCase().includes('mevrouw') || message.toLowerCase().includes('hendrik')) {
      if (message.toLowerCase().includes('dokter')) {
        return { content: "Meneer, ik zal u dokter gebruiken, meneer.", creditsUsed: 1 };
      } else if (message.toLowerCase().includes('mevrouw')) {
        return { content: "Meneer, ik zal u mevrouw gebruiken, meneer.", creditsUsed: 1 };
      } else if (message.toLowerCase().includes('hendrik')) {
        return { content: "Meneer, ik zal u hendrik van aalsmeer tot zwolle gebruiken, meneer.", creditsUsed: 1 };
      }
    }
    
    return {
      content: responses[Math.floor(Math.random() * responses.length)],
      creditsUsed: Math.floor(Math.random() * 3) + 1
    };
  };

  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Render login screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">Jarvis</CardTitle>
            <p className="text-muted-foreground">Google Workspace AI Assistant</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-center text-muted-foreground">
              Log in met uw Google account om toegang te krijgen tot alle functies van Jarvis.
            </p>
            <Button 
              onClick={handleLogin} 
              className="w-full bg-blue-600 hover:bg-blue-700"
              size="lg"
            >
              <Bot className="w-4 h-4 mr-2" />
              Inloggen met Google
            </Button>
            <div className="text-xs text-center text-muted-foreground">
              Demo versie - klik om door te gaan
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <div className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Jarvis</h1>
              <p className="text-xs text-muted-foreground">AI Assistant</p>
            </div>
          </div>
        </div>

        <div className="flex-1 p-4">
          <div className="space-y-2">
            <Button
              variant={currentView === 'chat' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentView('chat')}
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button
              variant={currentView === 'workspace' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentView('workspace')}
            >
              <FolderOpen className="w-4 h-4 mr-2" />
              Workspace
            </Button>
            <Button
              variant={currentView === 'ai-tools' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentView('ai-tools')}
            >
              <Brain className="w-4 h-4 mr-2" />
              AI Tools
            </Button>
          </div>
        </div>

        <div className="p-4 border-t border-border space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Credits</span>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              <Zap className="w-3 h-3 mr-1" />
              {credits}
            </Badge>
          </div>
          <Button variant="outline" size="sm" className="w-full">
            <CreditCard className="w-4 h-4 mr-2" />
            Upgrade
          </Button>
          <div className="text-xs text-muted-foreground">
            {user?.name} • {user?.email}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {currentView === 'chat' && (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-border bg-card">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-lg">Chat met Jarvis</h2>
                  <p className="text-sm text-muted-foreground">
                    Uw persoonlijke AI-assistent voor Google Workspace
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-green-600 border-green-200">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Online
                  </Badge>
                </div>
              </div>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4 max-w-4xl mx-auto">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex max-w-[80%] ${
                        message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user' 
                            ? 'bg-blue-600 ml-3' 
                            : 'bg-slate-700 mr-3'
                        }`}
                      >
                        {message.role === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div
                        className={`rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-card border border-border'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-blue-100' : 'text-muted-foreground'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex">
                      <div className="w-8 h-8 rounded-full bg-slate-700 mr-3 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-card border border-border rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span className="text-sm text-muted-foreground">Jarvis denkt na...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t border-border bg-card">
              <div className="max-w-4xl mx-auto">
                <div className="flex space-x-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Typ uw bericht aan Jarvis..."
                    className="flex-1"
                    disabled={isLoading}
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  Jarvis gebruikt AI om u te helpen met Google Workspace taken
                </p>
              </div>
            </div>
          </>
        )}

        {currentView === 'workspace' && (
          <div className="flex-1 p-6">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Google Workspace</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Mail className="w-5 h-5 mr-2 text-blue-600" />
                      Gmail
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Beheer uw e-mails met AI-ondersteuning
                    </p>
                    <Button variant="outline" className="w-full">
                      E-mails bekijken
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Calendar className="w-5 h-5 mr-2 text-green-600" />
                      Agenda
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Plan afspraken en beheer uw agenda
                    </p>
                    <Button variant="outline" className="w-full">
                      Agenda openen
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FolderOpen className="w-5 h-5 mr-2 text-yellow-600" />
                      Drive
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Toegang tot uw bestanden en documenten
                    </p>
                    <Button variant="outline" className="w-full">
                      Bestanden bekijken
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {currentView === 'ai-tools' && (
          <div className="flex-1 p-6">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">AI Tools</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                      Smart Compose
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Laat Jarvis e-mails en documenten voor u schrijven
                    </p>
                    <Button variant="outline" className="w-full">
                      Tekst genereren
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-blue-600" />
                      Samenvatten
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Krijg snelle samenvattingen van lange documenten
                    </p>
                    <Button variant="outline" className="w-full">
                      Document samenvatten
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Brain className="w-5 h-5 mr-2 text-green-600" />
                      Workspace Analyse
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Krijg inzichten in uw productiviteit en werkpatronen
                    </p>
                    <Button variant="outline" className="w-full">
                      Analyse starten
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Settings className="w-5 h-5 mr-2 text-gray-600" />
                      Vertalen
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Vertaal teksten met behoud van context en toon
                    </p>
                    <Button variant="outline" className="w-full">
                      Tekst vertalen
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

