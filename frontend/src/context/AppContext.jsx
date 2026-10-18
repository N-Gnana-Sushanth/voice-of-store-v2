import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import { USER_PROFILE } from '../data/mockData';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [user, setUser] = useState(USER_PROFILE);
  const [selectedDate, setSelectedDate] = useState('Week of 12 Oct - 18 Oct 2026');
  const [selectedRegion, setSelectedRegion] = useState('All Regions');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  // Authenticate session and check backend health
  const initSession = useCallback(async () => {
    try {
      // 1. Check health
      await api.health.check();
      setIsBackendOnline(true);

      // 2. Auto-login as Sushanth if no token exists
      let token = localStorage.getItem('vos_token');
      if (!token) {
        try {
          const authRes = await api.auth.login('sushanth@voiceofstore.internal', 'analystpassword123');
          token = authRes.access_token;
        } catch {
          // If seed password differed, try admin
          try {
            const adminRes = await api.auth.login('admin@voiceofstore.internal', 'adminpassword123');
            token = adminRes.access_token;
          } catch {
            // Keep demo user
          }
        }
      }

      // 3. Fetch current user if token present
      if (token) {
        try {
          const me = await api.auth.getMe();
          if (me) {
            setUser({
              name: me.full_name || 'Sushanth',
              initials: (me.full_name || 'Sushanth').slice(0, 2).toUpperCase(),
              role: me.role === 'analyst' ? 'HQ Analyst' : me.role === 'admin' ? 'HQ Admin' : 'Store Manager',
              email: me.email,
            });
          }
        } catch {
          // Token expired or invalid, reset
        }
      }

      // 4. Fetch notifications and unread count
      refreshNotifications();
    } catch {
      setIsBackendOnline(false);
    }
  }, []);

  const refreshNotifications = useCallback(async () => {
    try {
      setNotificationsLoading(true);
      const [countRes, listRes] = await Promise.all([
        api.notifications.unreadCount().catch(() => ({ unread_count: 0 })),
        api.notifications.list({ limit: 10 }).catch(() => ({ items: [] })),
      ]);
      setUnreadCount(countRes.unread_count || 0);
      setNotifications(listRes.items || []);
    } catch {
      // Fallback
    } finally {
      setNotificationsLoading(false);
    }
  }, []);

  useEffect(() => {
    initSession();
    const interval = setInterval(refreshNotifications, 30000); // 30s poll
    return () => clearInterval(interval);
  }, [initSession, refreshNotifications]);

  const markNotificationAsRead = async (id) => {
    try {
      await api.notifications.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (err) {
      console.error('Failed to mark notification read:', err);
    }
  };

  const markAllNotificationsAsRead = async () => {
    try {
      await api.notifications.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all notifications read:', err);
    }
  };

  const logout = () => {
    api.auth.logout();
    setUser({
      name: 'Guest',
      initials: 'GU',
      role: 'Logged Out',
      email: '',
    });
    setUnreadCount(0);
    setNotifications([]);
  };

  return (
    <AppContext.Provider
      value={{
        user,
        setUser,
        selectedDate,
        setSelectedDate,
        selectedRegion,
        setSelectedRegion,
        notifications,
        unreadCount,
        isBackendOnline,
        notificationsLoading,
        refreshNotifications,
        markNotificationAsRead,
        markAllNotificationsAsRead,
        logout,
        sidebarOpen,
        setSidebarOpen,
        toggleSidebar,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
