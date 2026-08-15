'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Send, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';

export const AskInvestigationPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState('');
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

  const handleSend = (queryText?: string) => {
    const q = queryText || question;
    if (!q.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: q }]);
    setQuestion('');

    setTimeout(() => {
      let reply = 'Evidence shows payment latency spiked from 500ms to 3.5s at 13:55 UTC before order latency degraded.';
      if (q.includes('contradicts')) {
        reply = 'Database latency remained completely normal (4.6ms avg), refuting PostgreSQL pool exhaustion.';
      } else if (q.includes('logs')) {
        reply = 'order-service-production.log line 14:03:12Z emitted HTTP POST timeout after 3000ms.';
      } else if (q.includes('changed')) {
        reply = 'Release v2.4.1 (commit d8f3a9e) was deployed to ShopFlow production at 13:30 UTC.';
      }
      setMessages((prev) => [...prev, { sender: 'assistant', text: reply }]);
    }, 400);
  };

  return (
    <Card className="p-4 space-y-2 border-accentPrimary/40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors"
      >
        <div className="flex items-center gap-2">
          <MessageSquare className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Ask about this investigation</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="pt-3 mt-2 border-t border-borderColor space-y-3">
          {/* Sample quick questions */}
          <div className="flex flex-wrap gap-1.5">
            {sampleQuestions.map((sq) => (
              <button
                key={sq}
                onClick={() => handleSend(sq)}
                className="px-2 py-1 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded text-[11px] font-mono text-accentPrimary transition-colors text-left"
              >
                "{sq}"
              </button>
            ))}
          </div>

          {/* Chat Messages Log */}
          <div className="max-h-48 overflow-y-auto space-y-2 text-xs font-sans">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded text-xs leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-accentSubtle text-accentPrimary font-semibold ml-6 border border-accentPrimary/30'
                    : 'bg-bgApp text-textPrimary mr-6 border border-borderColor font-mono text-[11px]'
                }`}
              >
                {m.text}
              </div>
            ))}
          </div>

          {/* Input Box */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask a question about this report..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary"
            />
            <Button size="sm" variant="primary" onClick={() => handleSend()} className="gap-1 text-xs">
              <Send className="w-3 h-3" />
              <span>Send</span>
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
};
