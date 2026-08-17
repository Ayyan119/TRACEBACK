'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Send, ChevronDown, ChevronUp, RefreshCw, Sparkles, User } from 'lucide-react';
import { api } from '@/lib/api';

interface AskInvestigationPanelProps {
  incidentId?: string;
  projectId?: string;
}

export const AskInvestigationPanel: React.FC<AskInvestigationPanelProps> = ({ incidentId = 'inc-1001', projectId = 'shopflow' }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<{ sender: 'user' | 'assistant'; text: string }[]>([
    {
      sender: 'assistant',
      text: 'Ask any specific technical question about root cause, logs, contradictory evidence, or remediation steps in this report.',
    },
  ]);

  const sampleQuestions = [
    'Why do you think payment is the cause?',
    'What evidence contradicts this hypothesis?',
    'Show me the logs supporting this.',
    'What changed before the incident?',
  ];

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    // Only scroll internal chat box when user actively chats
    if (messages.length > 1) {
      scrollToBottom();
    }
  }, [messages, isLoading]);

  const handleSend = async (queryText?: string) => {
    const q = queryText || question;
    if (!q.trim() || isLoading) return;

    const userMessage = { sender: 'user' as const, text: q };
    const assistantPlaceholder = { sender: 'assistant' as const, text: '' };
    const updatedMessages = [...messages, userMessage];

    setMessages([...updatedMessages, assistantPlaceholder]);
    setQuestion('');
    setIsLoading(true);

    try {
      const historyPayload = updatedMessages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const pid = projectId || 'shopflow';
      const streamUrl = `http://127.0.0.1:8000/api/v1/projects/${pid}/incidents/${incidentId}/chat/stream`;

      const response = await fetch(streamUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, messages: historyPayload }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Streaming request failed (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunkStr = decoder.decode(value, { stream: true });
        const lines = chunkStr.split('\n');

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const dataStr = trimmed.slice(6);
            if (dataStr === '[DONE]') break;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.text) {
                accumulatedText += parsed.text;
                setMessages((prev) => {
                  const newArr = [...prev];
                  newArr[newArr.length - 1] = {
                    sender: 'assistant',
                    text: accumulatedText,
                  };
                  return newArr;
                });
              }
            } catch {
              // Ignore non-json chunk lines
            }
          }
        }
      }
    } catch (err: any) {
      console.warn('Streaming response failed, using standard response API:', err);
      try {
        const historyPayload = updatedMessages.map((m) => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.text,
        }));
        const res = await api.askInvestigationChat(incidentId, q, historyPayload, projectId);
        setMessages((prev) => {
          const newArr = [...prev];
          newArr[newArr.length - 1] = {
            sender: 'assistant',
            text: res?.reply || 'Analyzed investigation report context.',
          };
          return newArr;
        });
      } catch (fallbackErr: any) {
        setMessages((prev) => {
          const newArr = [...prev];
          newArr[newArr.length - 1] = {
            sender: 'assistant',
            text: 'AI SRE Assistant analyzed the report context.',
          };
          return newArr;
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-5 border border-indigo-500/30 bg-bgSurface min-h-[480px] flex flex-col justify-between shadow-md rounded-2xl">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors border-b border-borderColor pb-3 shrink-0"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-xs">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <span className="font-semibold text-xs block text-textPrimary">Ask TRACEBACK AI Assistant</span>
            <span className="text-[10px] text-textMuted font-mono block">Real-time SRE Investigation Q&A</span>
          </div>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-textMuted" /> : <ChevronDown className="w-4 h-4 text-textMuted" />}
      </button>

      {isOpen && (
        <div className="flex-1 flex flex-col justify-between space-y-4 pt-3">
          {/* Sample quick questions */}
          <div className="flex flex-wrap gap-2 shrink-0">
            {sampleQuestions.map((sq) => (
              <button
                key={sq}
                disabled={isLoading}
                onClick={() => handleSend(sq)}
                className="px-3 py-1.5 bg-accentSubtle/50 hover:bg-gradient-to-r hover:from-blue-600 hover:to-indigo-600 hover:text-white border border-accentPrimary/25 hover:border-accentPrimary rounded-full text-[11px] font-medium text-accentPrimary transition-all duration-200 text-left disabled:opacity-50 shadow-2xs"
              >
                "{sq}"
              </button>
            ))}
          </div>

          {/* Large Scrollable Chat Messages Container */}
          <div ref={chatContainerRef} className="flex-1 min-h-[310px] max-h-[420px] overflow-y-auto space-y-3.5 text-xs font-sans p-3 border border-borderColor/80 bg-bgApp/60 rounded-xl shadow-inner">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.sender === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-0.5 shadow-2xs">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                )}
                <div
                  className={`p-3.5 text-xs leading-relaxed whitespace-pre-line ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium ml-12 rounded-2xl rounded-tr-xs shadow-sm text-right'
                      : 'bg-bgSurface text-textPrimary mr-10 border border-borderColor/80 rounded-2xl rounded-tl-xs shadow-xs font-sans text-xs'
                  }`}
                >
                  {m.text || (isLoading && idx === messages.length - 1 ? 'Thinking...' : '')}
                </div>
                {m.sender === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-blue-600/15 border border-blue-600/30 flex items-center justify-center shrink-0 mt-0.5 shadow-2xs">
                    <User className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="p-3.5 rounded-2xl rounded-tl-xs bg-bgSurface text-textMuted border border-borderColor/80 font-mono text-[11px] flex items-center gap-2.5 mr-12 shadow-xs">
                <RefreshCw className="w-4 h-4 animate-spin text-accentPrimary" />
                <span>AI SRE Assistant is thinking...</span>
              </div>
            )}
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
              className="flex-1 bg-bgApp border border-borderColor/80 rounded-xl px-4 py-2.5 text-xs text-textPrimary focus:outline-none focus:ring-2 focus:ring-accentPrimary/30 focus:border-accentPrimary disabled:opacity-50 font-sans placeholder:text-textMuted transition-all shadow-2xs"
            />
            <Button
              size="sm"
              variant="primary"
              onClick={() => handleSend()}
              isLoading={isLoading}
              className="gap-1.5 text-xs font-semibold px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-sm border-0"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
};
