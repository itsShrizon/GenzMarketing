import React from 'react';
import { User, Bot } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../services/api';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-3 p-4 ${isUser ? 'bg-blue-50' : 'bg-gray-50'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-blue-500 text-white' : 'bg-gray-500 text-white'
      }`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>
      <div className="flex-1">
        <div className={`font-medium text-sm mb-1 ${
          isUser ? 'text-blue-700' : 'text-gray-700'
        }`}>
          {isUser ? 'You' : 'GenZ Marketing Bot'}
        </div>
        <div className="text-gray-800 whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
