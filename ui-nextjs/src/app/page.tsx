'use client';

import * as React from 'react';
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarInset,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';
import { Icons } from '@/components/icons';
import { ChatLayout } from '@/components/chat/chat-layout';
import type { Conversation, Message } from '@/lib/data';

export default function Home() {
  const [conversations, setConversations] = React.useState<Conversation[]>([]);
  const [messages, setMessages] = React.useState<Record<string, Message[]>>({});
  const [selectedConversation, setSelectedConversation] = React.useState<Conversation | null>(null);
  const [isVoiceMode, setIsVoiceMode] = React.useState(true);
  const [isLoading, setIsLoading] = React.useState(true);
  
  // Load conversations from database on mount
  React.useEffect(() => {
    loadConversationsFromAPI();
  }, []);
  
  // Load messages when conversation is selected
  React.useEffect(() => {
    if (selectedConversation) {
      loadMessagesFromAPI(selectedConversation.id);
    }
  }, [selectedConversation]);
  
  const loadConversationsFromAPI = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/conversations`);
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const loadMessagesFromAPI = async (conversationId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/conversations/${conversationId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => ({ ...prev, [conversationId]: data }));
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };
  
  const handleNewChat = () => {
    // Just reset to voice mode - conversation will be created on first message
    setSelectedConversation(null);
    setIsVoiceMode(true);
  };

  const currentMessages = selectedConversation ? messages[selectedConversation.id] || [] : [];
  
  const setConversationMessages = (newMessages: Message[]) => {
    if (selectedConversation) {
      setMessages(prev => ({
        ...prev,
        [selectedConversation.id]: newMessages,
      }));
    }
  };

  const toggleVoiceMode = () => {
    setIsVoiceMode(prev => !prev);
    if (!selectedConversation && conversations.length > 0) {
      setSelectedConversation(conversations[0]);
    }
  };
  
  // Handle conversation created from API response
  const handleConversationCreated = React.useCallback((conversationId: string, title: string) => {
    const newConversation: Conversation = {
      id: conversationId,
      title: title,
    };
    
    // Refresh conversations list from database
    loadConversationsFromAPI();
    setSelectedConversation(newConversation);
    setIsVoiceMode(false);
  }, []);
  
  // Create or select conversation - handled by API
  const createOrSelectConversation = React.useCallback(async (firstMessage: string): Promise<Conversation | null> => {
    if (selectedConversation) {
      return selectedConversation;
    }
    // Conversation will be created by API, we'll get it back from chat response
    return null;
  }, [selectedConversation]);

  return (
    <main className="min-h-screen bg-background">
      <SidebarProvider defaultOpen={true}>
        <Sidebar>
          <SidebarHeader className="p-2">
            <div className="flex items-center justify-between">
              <Button variant="ghost" className="gap-2 text-lg font-semibold">
                <Icons.logo className="w-6 h-6" />
                <span className="group-data-[state=collapsed]:hidden">Hue</span>
              </Button>
              <div className="flex items-center">
                <ThemeToggle />
                <Button variant="ghost" size="icon" onClick={handleNewChat}>
                  <Plus className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </SidebarHeader>
          <SidebarContent className="p-2">
            <SidebarMenu>
              {conversations.map((conversation) => (
                <SidebarMenuItem key={conversation.id}>
                  <SidebarMenuButton
                    onClick={() => {
                      setSelectedConversation(conversation);
                      setIsVoiceMode(false);
                    }}
                    isActive={selectedConversation?.id === conversation.id}
                    tooltip={conversation.title}
                  >
                    <MessageSquare />
                    <span>{conversation.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter className="p-2 flex items-center justify-center">
          </SidebarFooter>
        </Sidebar>
        <SidebarInset>
          <ChatLayout
            conversation={selectedConversation}
            messages={currentMessages}
            setMessages={setConversationMessages}
            isVoiceMode={isVoiceMode}
            toggleVoiceMode={toggleVoiceMode}
            createOrSelectConversation={createOrSelectConversation}
            onConversationCreated={handleConversationCreated}
            onMessagesLoaded={loadMessagesFromAPI}
          />
        </SidebarInset>
      </SidebarProvider>
    </main>
  );
}
