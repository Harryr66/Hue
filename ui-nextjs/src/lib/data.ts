export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export interface Conversation {
  id: string;
  title: string;
}

export const conversations: Conversation[] = [
  { id: 'conv-1', title: 'Exploring Next.js 14' },
  { id: 'conv-2', title: 'The Future of AI' },
  { id: 'conv-3', title: 'Creative Writing Ideas' },
];

export const messages: Record<string, Message[]> = {
  'conv-1': [
    {
      id: 'msg-1',
      role: 'user',
      content: 'What are the key features of Next.js 14?',
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content:
        'Next.js 14 focuses on improving performance with Turbopack, enhancing developer experience with better error messages, and stabilizing Server Actions. It aims to make building complex, high-performance web applications faster and more intuitive.',
    },
  ],
  'conv-2': [
    {
      id: 'msg-3',
      role: 'user',
      content: 'Where do you see AI heading in the next 5 years?',
    },
    {
      id: 'msg-4',
      role: 'assistant',
      content: 'In the next five years, I anticipate AI will become more integrated into our daily lives through personalized assistants, advancements in autonomous systems, and significant breakthroughs in creative fields and scientific research. We can also expect more powerful and efficient models that are accessible to a wider range of developers and businesses.',
    },
     {
      id: 'msg-5',
      role: 'user',
      content: 'That sounds exciting! What about the ethical considerations?',
    },
     {
      id: 'msg-6',
      role: 'assistant',
      content: 'That\'s a crucial point. The rapid advancement of AI necessitates a strong focus on ethical guidelines. Key areas of concern include data privacy, algorithmic bias, and the societal impact of automation. Developing transparent, fair, and accountable AI systems will be paramount to ensuring technology serves humanity beneficially and equitably.',
    },
  ],
  'conv-3': [],
};
