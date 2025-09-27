import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  last_login: string | null;
  preferences: {
    theme: string;
    articles_per_page: number;
    default_time_range: number;
  };
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  hideArticle: (articleId: string) => Promise<boolean>;
  unhideArticle: (articleId: string) => Promise<boolean>;
  getHiddenArticles: () => Promise<string[]>;
  updatePreferences: (preferences: any) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Get stored token
  const getToken = () => localStorage.getItem('auth_token');
  
  // Set token
  const setToken = (token: string) => localStorage.setItem('auth_token', token);
  
  // Remove token
  const removeToken = () => localStorage.removeItem('auth_token');

  // API call helper with auth header
  const apiCall = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const token = getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Token expired or invalid
      removeToken();
      setUser(null);
    }

    return response;
  }, [API_BASE_URL]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await apiCall('/api/auth/me');
        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
        } else {
          removeToken();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        removeToken();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [apiCall]);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.session_token);
        setUser(data.user);
        return true;
      } else {
        const error = await response.json();
        console.error('Login failed:', error.error);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.session_token);
        setUser(data.user);
        return true;
      } else {
        const error = await response.json();
        console.error('Registration failed:', error.error);
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await apiCall('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeToken();
      setUser(null);
    }
  };

  const hideArticle = async (articleId: string): Promise<boolean> => {
    try {
      const response = await apiCall(`/api/auth/articles/${articleId}/hide`, {
        method: 'POST',
      });
      return response.ok;
    } catch (error) {
      console.error('Hide article error:', error);
      return false;
    }
  };

  const unhideArticle = async (articleId: string): Promise<boolean> => {
    try {
      const response = await apiCall(`/api/auth/articles/${articleId}/unhide`, {
        method: 'POST',
      });
      return response.ok;
    } catch (error) {
      console.error('Unhide article error:', error);
      return false;
    }
  };

  const getHiddenArticles = async (): Promise<string[]> => {
    try {
      const response = await apiCall('/api/auth/articles/hidden');
      if (response.ok) {
        const data = await response.json();
        return data.hidden_articles;
      }
      return [];
    } catch (error) {
      console.error('Get hidden articles error:', error);
      return [];
    }
  };

  const updatePreferences = async (preferences: any): Promise<boolean> => {
    try {
      const response = await apiCall('/api/auth/preferences', {
        method: 'PUT',
        body: JSON.stringify({ preferences }),
      });
      
      if (response.ok && user) {
        setUser({ ...user, preferences });
        return true;
      }
      return false;
    } catch (error) {
      console.error('Update preferences error:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    hideArticle,
    unhideArticle,
    getHiddenArticles,
    updatePreferences,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};