'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { AudioLines, Send, X } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  onVoiceClick: () => void;
  isVoiceMode: boolean;
}

export function ChatInput({ onSendMessage, onVoiceClick, isVoiceMode }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };
  
  if (isVoiceMode) {
    return (
      <div className="p-4 bg-transparent">
        <div className="relative max-w-2xl mx-auto flex justify-center">
          <button
            onClick={onVoiceClick}
            className="flex items-center justify-center h-24 w-12 rounded-full border-2 border-foreground/50 bg-transparent hover:border-foreground transition-colors"
            aria-label="Exit Voice Mode"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 bg-transparent">
      <div className="relative max-w-2xl mx-auto">
        <Textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Message Hue..."
          className="min-h-[52px] w-full resize-none rounded-full border-2 bg-background py-3 pl-4 pr-28 shadow-sm dark:bg-[rgba(0,0,0,0.9)] dark:border-[rgba(81,196,211,0.2)]"
        />
        <div className="absolute inset-y-0 right-0 flex items-center pr-3">
           <Button variant="ghost" size="icon" onClick={handleSend} disabled={!inputValue.trim()}>
            <Send className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={onVoiceClick}>
            <div className="w-6 h-6 rounded-full border-2 border-current flex items-center justify-center">
              <AudioLines className="w-4 h-4" />
            </div>
          </Button>
        </div>
      </div>
      <p className="text-xs text-center text-muted-foreground mt-2">
        Hue can make mistakes. Consider checking important information.
      </p>
    </div>
  );
}
