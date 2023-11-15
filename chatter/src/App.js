import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const App = () => {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io('http://localhost:8888');
    setSocket(newSocket);

    // Cleanup on component unmount
    return () => newSocket.close();
  }, []);

  const sendMessage = () => {
    const message = 'Hello, server!';
    socket.emit('message', message);
  };

  return (
    <div>
      <h1>Socket.io React App</h1>
      <button onClick={sendMessage}>Send Message to Server</button>
    </div>
  );
};

export default App;
