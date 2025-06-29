import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Alert, AlertDescription } from '@/components/ui/alert.jsx';
import { Bot, Loader2, AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

export const GoogleAuth = ({ onAuthSuccess, onAuthError }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [authUrl, setAuthUrl] = useState(null);

  // Initialize Google OAuth flow
  const initiateGoogleLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.authorization_url) {
        // In a real app, redirect to Google OAuth
        // For demo purposes, we'll simulate success
        setAuthUrl(data.authorization_url);
        
        // Simulate OAuth callback after 2 seconds
        setTimeout(() => {
          simulateOAuthCallback();
        }, 2000);
      } else {
        throw new Error('No authorization URL received');
      }
    } catch (err) {
      console.error('OAuth initialization failed:', err);
      setError('Failed to initialize Google login. Please try again.');
      setIsLoading(false);
    }
  };

  // Simulate OAuth callback (in real app, this would be handled by redirect)
  const simulateOAuthCallback = async () => {
    try {
      // Simulate successful OAuth with mock data
      const mockAuthData = {
        access_token: 'mock_access_token_' + Date.now(),
        refresh_token: 'mock_refresh_token_' + Date.now(),
        expires_in: 3600,
        scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar',
        google_id: 'mock_google_id_' + Date.now(),
        email: 'user@example.com',
        name: 'Demo User'
      };

      const response = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockAuthData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.user) {
        onAuthSuccess({
          user: result.user,
          sessionId: result.session_id,
          isNewUser: result.is_new_user
        });
      } else {
        throw new Error('Authentication failed');
      }
    } catch (err) {
      console.error('OAuth callback failed:', err);
      setError('Authentication failed. Please try again.');
      onAuthError(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Check existing authentication status
  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': localStorage.getItem('jarvis_user_id') || '',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authenticated && data.user) {
          onAuthSuccess({
            user: data.user,
            sessionId: data.user.id,
            isNewUser: false
          });
        }
      }
    } catch (err) {
      console.error('Auth status check failed:', err);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

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
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <p className="text-sm text-center text-muted-foreground">
            Log in met uw Google account om toegang te krijgen tot alle functies van Jarvis.
          </p>
          
          {authUrl && (
            <Alert>
              <AlertDescription>
                Redirecting to Google OAuth... In een echte app zou u nu doorgestuurd worden naar Google.
              </AlertDescription>
            </Alert>
          )}
          
          <Button 
            onClick={initiateGoogleLogin} 
            className="w-full bg-blue-600 hover:bg-blue-700"
            size="lg"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Inloggen...
              </>
            ) : (
              <>
                <Bot className="w-4 h-4 mr-2" />
                Inloggen met Google
              </>
            )}
          </Button>
          
          <div className="text-xs text-center text-muted-foreground space-y-1">
            <p>Demo versie - gebruikt mock authenticatie</p>
            <p>In productie: echte Google OAuth flow</p>
          </div>
          
          <div className="text-xs text-muted-foreground">
            <p className="font-semibold mb-1">Vereiste Google Workspace toegang:</p>
            <ul className="space-y-1 text-xs">
              <li>• Gmail - E-mails lezen en versturen</li>
              <li>• Drive - Bestanden beheren</li>
              <li>• Calendar - Afspraken plannen</li>
              <li>• Docs/Sheets - Documenten bewerken</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GoogleAuth;

