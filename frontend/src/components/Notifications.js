import React, { useState, useEffect } from 'react';
import { Toast, ToastContainer, Badge } from 'react-bootstrap';
import { getNotifications, markNotificationAsRead } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [showToasts, setShowToasts] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotifications();
    
    // Set up polling for notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await getNotifications();
      setNotifications(response.data);
      
      // Initialize toast visibility state
      const initialShowState = {};
      response.data.forEach(notification => {
        initialShowState[notification.id] = !notification.read;
      });
      setShowToasts(initialShowState);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const handleClose = async (id) => {
    try {
      await markNotificationAsRead(id);
      setShowToasts(prev => ({ ...prev, [id]: false }));
      
      // Update local state to mark as read
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleClick = (notification) => {
    // Navigate based on notification type
    if (notification.notification_type === 'job_match') {
      navigate(`/jobs/${notification.related_id}`);
    } else if (notification.notification_type === 'application_update') {
      navigate(`/applications`);
    } else {
      navigate('/dashboard');
    }
    
    // Mark as read
    handleClose(notification.id);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <>
      {unreadCount > 0 && (
        <Badge 
          bg="danger" 
          pill 
          className="position-absolute top-0 start-100 translate-middle"
          style={{ fontSize: '0.6rem' }}
        >
          {unreadCount}
        </Badge>
      )}
      
      <ToastContainer position="top-end" className="p-3" style={{ zIndex: 1060 }}>
        {notifications.map(notification => (
          <Toast 
            key={notification.id}
            show={showToasts[notification.id] || false} 
            onClose={() => handleClose(notification.id)}
            delay={5000}
            autohide
            className="cursor-pointer"
            onClick={() => handleClick(notification)}
          >
            <Toast.Header>
              <strong className="me-auto">
                {notification.notification_type === 'job_match' && 'New Job Match'}
                {notification.notification_type === 'application_update' && 'Application Update'}
                {notification.notification_type === 'system' && 'System Notification'}
              </strong>
              <small>{new Date(notification.created_at).toLocaleTimeString()}</small>
            </Toast.Header>
            <Toast.Body>{notification.message}</Toast.Body>
          </Toast>
        ))}
      </ToastContainer>
    </>
  );
};

export default Notifications;