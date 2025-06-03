import { useEffect, useRef, useState } from 'react';

import { Bot, Clock, FileText, Send, User } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface ChatInterfaceProps {
  documents: any[];
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    title: string;
    content: string;
    similarity: number;
  }>;
}

export function ChatInterface({ documents }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || documents.length === 0) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 실제 구현에서는 여기서 API 호출
      // const response = await fetch('/api/chat', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({ query: input })
      // })
      // const data = await response.json()

      // API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 2000));

      // 응답 생성
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `"${input}"에 대한 답변:\n\n업로드된 문서에서 관련 정보를 찾아 종합적으로 분석한 결과, 다음과 같은 내용을 확인할 수 있습니다.`,
        timestamp: new Date(),
        sources: [
          {
            title: documents[0]?.name || '문서1.pdf',
            content: '관련 내용의 일부분이 여기에 표시됩니다...',
            similarity: 0.89,
          },
          {
            title: documents.length > 1 ? documents[1]?.name : '문서2.txt',
            content: '또 다른 관련 내용이 여기에 표시됩니다...',
            similarity: 0.76,
          },
        ],
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      // 오류 메시지 표시
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '죄송합니다. 응답을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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
          <ScrollArea className='flex-1 p-4' ref={scrollAreaRef}>
            <div className='space-y-4'>
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
                        참조된 문서:
                      </p>
                      {message.sources.map((source, index) => (
                        <Card key={index} className='p-3'>
                          <div className='mb-2 flex items-center justify-between'>
                            <p className='text-sm font-medium'>{source.title}</p>
                            <Badge variant='secondary' className='text-xs'>
                              유사도: {(source.similarity * 100).toFixed(1)}%
                            </Badge>
                          </div>
                          <p className='text-muted-foreground text-sm'>{source.content}</p>
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
          </ScrollArea>

          <Separator />

          {/* 입력 영역 */}
          <div className='p-4'>
            <div className='flex gap-2'>
              <Input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder='Ask a question about the document...'
                disabled={isLoading || documents.length === 0}
                className='flex-1'
              />
              <Button onClick={handleSend} disabled={!input.trim() || isLoading || documents.length === 0} size='icon'>
                <Send className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
