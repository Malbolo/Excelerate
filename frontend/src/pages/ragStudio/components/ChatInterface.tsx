import { useEffect, useRef, useState } from 'react';

import { Bot, Clock, FileText, Send, User } from 'lucide-react';

import { RagSource, useRagSearch } from '@/apis/ragStudio';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<RagSource>;
}

// 검색할 최대 문서 수
const K = 3;

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const ragSearchMutate = useRagSearch();

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    const request = {
      query: input,
      k: K,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // API 호출
    const response = await ragSearchMutate(request);

    // 응답 생성
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: response.answer,
      timestamp: new Date(),
      sources: response.sources,
    };

    setMessages(prev => [...prev, assistantMessage]);

    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className='l:w-2/3 h-full w-3/5 grow space-y-4'>
      {/* 채팅 영역 */}
      <Card className='flex h-full flex-col'>
        <CardContent className='flex h-full flex-col p-0'>
          <section className='flex-1 overflow-y-auto p-4' ref={scrollAreaRef}>
            <div className='min-h-0 space-y-4'>
              {messages.length === 0 && (
                <div className='text-muted-foreground py-8 text-center'>
                  <Bot className='mx-auto mb-4 h-5 w-5' />
                  <p className='text-xs'>Hello! Feel free to ask any questions about the uploaded document.</p>
                </div>
              )}

              {messages.map(message => (
                <div key={message.id} className='space-y-2'>
                  <div className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`flex max-w-[80%] gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      <div
                        className={`flex h-8 w-8 items-center justify-center rounded-full ${
                          message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}
                      >
                        {message.type === 'user' ? <User className='h-4 w-4' /> : <Bot className='h-4 w-4' />}
                      </div>
                      <div
                        className={`rounded-lg p-3 ${
                          message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}
                      >
                        <p className='whitespace-pre-wrap'>{message.content}</p>
                        <div className='mt-2 flex items-center gap-1 opacity-70'>
                          <Clock className='h-3 w-3' />
                          <span className='text-xs'>{message.timestamp.toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 소스 정보 표시 */}
                  {message.sources && (
                    <div className='ml-11 space-y-2'>
                      <p className='text-muted-foreground flex items-center gap-1 text-sm font-medium'>
                        <FileText className='h-3 w-3' />
                        Referenced Documents:
                      </p>
                      {message.sources.map((source, index) => (
                        <Card key={index} className='p-3'>
                          <div className='flex items-center justify-between'>
                            <Badge variant='secondary' className='text-xs'>
                              Similarity: {source.similarity.toFixed(1)}%
                            </Badge>
                          </div>
                          <p className='text-muted-foreground text-sm'>{source.file_name}</p>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className='flex gap-3'>
                  <div className='bg-muted flex h-8 w-8 items-center justify-center rounded-full'>
                    <Bot className='h-4 w-4' />
                  </div>
                  <div className='bg-muted rounded-lg p-3'>
                    <div className='flex items-center gap-2'>
                      <div className='border-primary h-4 w-4 animate-spin rounded-full border-b-2'></div>
                      <span className='text-sm'>Generating your response...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>

          <Separator />

          {/* 입력 영역 */}
          <div className='p-4'>
            <div className='flex gap-2'>
              <Input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder='Ask a question about the document...'
                disabled={isLoading}
                className='flex-1'
              />
              <Button onClick={handleSend} disabled={!input.trim() || isLoading} size='icon'>
                <Send className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
