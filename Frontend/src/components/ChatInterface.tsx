import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, Mic, Video, Trash2 } from 'lucide-react';
import { ChatMessage as ChatMessageType, chatService } from '../services/api';
import ChatMessage from './ChatMessage';
import VoiceInput from './VoiceInput';
import AvatarGenerator from './AvatarGenerator';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const [showAvatarGenerator, setShowAvatarGenerator] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load chat history on component mount
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const { history } = await chatService.getChatHistory();
      setMessages(history);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessageType = {
      role: 'user',
      content: message.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(message.trim());
      
      const assistantMessage: ChatMessageType = {
        role: 'assistant',
        content: response.response
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessageType = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your message. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputMessage);
    }
  };

  const handleVoiceResult = (transcript: string) => {
    setInputMessage(transcript);
    setShowVoiceInput(false);
  };

  const clearChatHistory = async () => {
    try {
      await chatService.clearChatHistory();
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear chat history:', error);
    }
  };

  const getLastAssistantMessage = (): string => {
    const lastAssistant = messages
      .filter(msg => msg.role === 'assistant')
      .pop();
    return lastAssistant?.content || '';
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">GenZ Marketing Chatbot</h1>
            <p className="text-purple-100">Your AI-powered marketing assistant</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowVoiceInput(!showVoiceInput)}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              title="Voice Input"
            >
              <Mic size={20} />
            </button>
            <button
              onClick={() => setShowAvatarGenerator(!showAvatarGenerator)}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              title="Generate Avatar Video"
            >
              <Video size={20} />
            </button>
            <button
              onClick={clearChatHistory}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              title="Clear Chat"
            >
              <Trash2 size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Voice Input Panel */}
      {showVoiceInput && (
        <div className="bg-yellow-50 border-b border-yellow-200 p-4">
          <VoiceInput
            onTranscript={handleVoiceResult}
            onClose={() => setShowVoiceInput(false)}
          />
        </div>
      )}

      {/* Avatar Generator Panel */}
      {showAvatarGenerator && (
        <div className="bg-green-50 border-b border-green-200 p-4">
          <AvatarGenerator
            text={getLastAssistantMessage()}
            onClose={() => setShowAvatarGenerator(false)}
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-6xl mb-4">🤖</div>
            <h2 className="text-2xl font-bold mb-2">Welcome to GenZ Marketing Chatbot!</h2>
            <p className="text-center max-w-md">
              I'm here to help you with marketing strategies, content ideas, and business insights. 
              Ask me anything about marketing!
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-3 p-4 bg-gray-50">
                <div className="w-8 h-8 rounded-full bg-gray-500 text-white flex items-center justify-center">
                  <Loader className="animate-spin" size={16} />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm mb-1 text-gray-700">
                    GenZ Marketing Bot
                  </div>
                  <div className="text-gray-600">
                    Thinking...
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your marketing question..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows={1}
            style={{ maxHeight: '120px' }}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage(inputMessage)}
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isLoading ? <Loader className="animate-spin" size={16} /> : <Send size={16} />}
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
