import ChatInterface from './components/ChatInterface';
import AuthGate from './components/AuthGate';
import APIKeyRequest from './components/APIKeyRequest';

function App() {
  return (
    <div className="h-screen">
      <AuthGate>
        <ChatInterface />
      </AuthGate>
    </div>
  );
}

export default App;