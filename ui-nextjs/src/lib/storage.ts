import type { Conversation, Message } from './data';

const STORAGE_KEY_CONVERSATIONS = 'hue_conversations';
const STORAGE_KEY_MESSAGES = 'hue_messages';
const MAX_CONVERSATIONS = 10;

/**
 * Load conversations from localStorage
 */
export function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY_CONVERSATIONS);
    if (!stored) return [];
    
    const conversations = JSON.parse(stored) as Conversation[];
    // Keep only last 10
    return conversations.slice(0, MAX_CONVERSATIONS);
  } catch (error) {
    console.error('Error loading conversations:', error);
    return [];
  }
}

/**
 * Save conversations to localStorage (keeps only last 10)
 */
export function saveConversations(conversations: Conversation[]): void {
  if (typeof window === 'undefined') return;
  
  try {
    // Keep only last 10 conversations
    const toSave = conversations.slice(0, MAX_CONVERSATIONS);
    localStorage.setItem(STORAGE_KEY_CONVERSATIONS, JSON.stringify(toSave));
  } catch (error) {
    console.error('Error saving conversations:', error);
  }
}

/**
 * Load messages from localStorage
 */
export function loadMessages(): Record<string, Message[]> {
  if (typeof window === 'undefined') return {};
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY_MESSAGES);
    if (!stored) return {};
    
    return JSON.parse(stored) as Record<string, Message[]>;
  } catch (error) {
    console.error('Error loading messages:', error);
    return {};
  }
}

/**
 * Save messages to localStorage
 */
export function saveMessages(messages: Record<string, Message[]>): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages));
  } catch (error) {
    console.error('Error saving messages:', error);
  }
}

/**
 * Generate conversation title from first message
 */
export function generateConversationTitle(firstMessage: string): string {
  // Take first 30 characters and add ellipsis if longer
  const title = firstMessage.trim().slice(0, 30);
  return title.length < firstMessage.trim().length ? `${title}...` : title;
}

/**
 * Clear all stored conversations and messages
 */
export function clearStorage(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(STORAGE_KEY_CONVERSATIONS);
  localStorage.removeItem(STORAGE_KEY_MESSAGES);
}


