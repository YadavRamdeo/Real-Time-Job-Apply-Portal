import API_CONFIG from '../config/api.config';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.callbacks = {};
  }

  connect() {
    if (this.socket) {
      this.socket.close();
    }

    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No authentication token found');
      return;
    }

    // Connect to WebSocket with authentication token
    this.socket = new WebSocket(`${API_CONFIG.WEBSOCKET_URL}?token=${token}`);

    this.socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Trigger callbacks based on message type
        if (data.type && this.callbacks[data.type]) {
          this.callbacks[data.type].forEach(callback => callback(data));
        }
        
        // Also trigger general message callbacks
        if (this.callbacks['message']) {
          this.callbacks['message'].forEach(callback => callback(data));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(type, callback) {
    if (!this.callbacks[type]) {
      this.callbacks[type] = [];
    }
    this.callbacks[type].push(callback);
  }

  off(type, callback) {
    if (this.callbacks[type]) {
      this.callbacks[type] = this.callbacks[type].filter(cb => cb !== callback);
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;