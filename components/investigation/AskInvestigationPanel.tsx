'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Send, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';

interface AskInvestigationPanelProps {
  incidentId?: string;
  projectId?: string;
}

export const AskInvestigationPanel: React.FC<AskInvestigationPanelProps> = ({ incidentId = 'inc-1001', projectId = 'shopflow' }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<{ sender: 'user' | 'assistant'; text: string }[]>([
    {
      sender: 'assistant',
      text: 'Ask any specific technical question about evidence correlation, logs, or contradictory hypotheses in this report.',
    },
  ]);

  const sampleQuestions = [
    'Why do you think payment is the cause?',
    'What evidence contradicts this hypothesis?',
    'Show me the logs supporting this.',
    'What changed before the incident?',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isLoading, isOpen]);

  const handleSend = async (queryText?: string) => {
    const q = queryText || question;
    if (!q.trim() || isLoading) return;

    const userMessage = { sender: 'user' as const, text: q };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setQuestion('');
    setIsLoading(true);

    try {
      // Short-term in-memory history for LLM prompt
      const historyPayload = updatedMessages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await api.askInvestigationChat(incidentId, q, historyPayload, projectId);
      const replyText = res?.reply || 'Based on the final investigation report, no additional details were found for this query.';
      setMessages((prev) => [...prev, { sender: 'assistant', text: replyText }]);
    } catch (err: any) {
      console.error('Failed to get answer from AI Chat:', err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `AI Assistant response: ${err?.message || 'Checked final report dictionary.'}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-5 space-y-3 border-accentPrimary/40 bg-bgSurface min-h-[460px] flex flex-col justify-between">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors border-b border-borderColor pb-2 shrink-0"
      >
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-accentPrimary" />
          <span className="font-mono text-xs">Ask about this investigation (SRE AI Chat)</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-textMuted" /> : <ChevronDown className="w-4 h-4 text-textMuted" />}
      </button>

      {isOpen && (
        <div className="flex-1 flex flex-col justify-between space-y-4 pt-1">
          {/* Sample quick questions */}
          <div className="flex flex-wrap gap-1.5 shrink-0">
            {sampleQuestions.map((sq) => (
              <button
                key={sq}
                disabled={isLoading}
                onClick={() => handleSend(sq)}
                className="px-2.5 py-1 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded text-[11px] font-mono text-accentPrimary transition-colors text-left disabled:opacity-50"
              >
                "{sq}"
              </button>
            ))}
          </div>

          {/* Large Scrollable Chat Messages Container */}
          <div className="flex-1 min-h-[300px] max-h-[400px] overflow-y-auto space-y-3 text-xs font-sans p-2 border border-borderColor/60 bg-bgApp/50 rounded-lg">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg text-xs leading-relaxed whitespace-pre-line shadow-xs ${
                  m.sender === 'user'
                    ? 'bg-accentSubtle text-accentPrimary font-semibold ml-12 border border-accentPrimary/30 text-right'
                    : 'bg-bgSurface text-textPrimary mr-12 border border-borderColor font-mono text-[11px]'
                }`}
              >
                {m.text}
              </div>
            ))}
            {isLoading && (
              <div className="p-3 rounded-lg bg-bgSurface text-textMuted border border-borderColor font-mono text-[11px] flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-accentPrimary" />
                <span>Invoking LLM with investigation report dictionary...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div className="flex gap-2.5 shrink-0 pt-1">
            <input
              type="text"
              placeholder="Ask a question about this report (e.g., 'what is my issue', 'how to fix this')..."
              value={question}
              disabled={isLoading}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 bg-bgApp border border-borderColor rounded-lg px-3 py-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary disabled:opacity-50 font-mono placeholder:text-textMuted"
            />
            <Button size="sm" variant="primary" onClick={() => handleSend()} isLoading={isLoading} className="gap-1.5 text-xs font-mono px-4 py-2">
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
};
