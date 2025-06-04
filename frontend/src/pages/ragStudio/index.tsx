import { ChatInterface } from './components/ChatInterface';
import RagManagement from './components/RagManagement';

const RagStudio = () => {
  return (
    <div className='bg-gradient flex h-screen w-full gap-5 p-8'>
      <ChatInterface />
      <RagManagement />
    </div>
  );
};

export default RagStudio;
