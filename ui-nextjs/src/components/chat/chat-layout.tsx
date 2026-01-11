'use client';

import * as React from 'react';
import type { Conversation, Message } from '@/lib/data';
import { AiPersona } from './ai-persona';
import { ChatMessages } from './chat-messages';
import { ChatInput } from './chat-input';
import { SidebarTrigger } from '../ui/sidebar';

interface ChatLayoutProps {
  conversation: Conversation | null;
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  isVoiceMode: boolean;
  toggleVoiceMode: () => void;
  createOrSelectConversation?: (firstMessage: string) => Promise<Conversation | null>;
  onConversationCreated?: (conversationId: string, title: string) => void;
  onMessagesLoaded?: (conversationId: string) => Promise<void>;
}

export function ChatLayout({ 
  conversation, 
  messages, 
  setMessages, 
  isVoiceMode, 
  toggleVoiceMode, 
  createOrSelectConversation,
  onConversationCreated,
  onMessagesLoaded
}: ChatLayoutProps) {
  const [isResponding, setIsResponding] = React.useState(false);
  
  const handleSendMessage = async (content: string) => {
    setIsResponding(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: content,
          conversation_id: conversation?.id || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Handle conversation creation if this is the first message
      if (!conversation && data.conversation_id && onConversationCreated) {
        const title = content.slice(0, 30) + (content.length > 30 ? '...' : '');
        onConversationCreated(data.conversation_id, title);
        // Reload messages for the new conversation
        if (onMessagesLoaded) {
          await onMessagesLoaded(data.conversation_id);
        }
      } else if (data.conversation_id && onMessagesLoaded) {
        // Reload messages to get from database (includes both user and assistant messages)
        await onMessagesLoaded(data.conversation_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsResponding(false);
    }
  };
  
  const showPersona = isVoiceMode || !conversation;

  return (
    <div className="relative flex flex-col h-full">
      <div className="absolute top-4 left-4 z-10">
        <SidebarTrigger />
      </div>
      {showPersona ? (
        <div className="flex flex-col items-center justify-center h-full gap-8">
          <AiPersona isSpeaking={isResponding} />
        </div>
      ) : (
        <ChatMessages messages={messages} />
      )}

      <div className="mt-auto">
        <ChatInput onSendMessage={handleSendMessage} onVoiceClick={toggleVoiceMode} isVoiceMode={isVoiceMode}/>
      </div>
    </div>
  );
}
