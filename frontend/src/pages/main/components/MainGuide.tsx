import { motion } from 'framer-motion';
import { CloudUpload, CommandIcon, Save } from 'lucide-react';

import { cn } from '@/lib/utils';

interface MainGuideProps {
  currentStep?: number;
}

const MainGuide = ({ currentStep }: MainGuideProps) => {
  const steps = [
    {
      icon: CloudUpload,
      title: 'Step 1',
      description: [
        'Please load the source data to be processed.',
        'This action will commence the job.',
        'e.g. "수원 공장에서 4월 불량률 데이터 불러와."',
      ],
    },
    {
      icon: CommandIcon,
      title: 'Step 2',
      description: [
        'Manipulate data with simple commands.',
        'Filter, sort, or modify data as needed.',
        'e.g. "불량률 1 이상만 필터링해."',
      ],
    },
    {
      icon: Save,
      title: 'Step 3',
      description: [
        'Save the task!',
        'You can edit or delete this task later, and schedule it to run automatically at regular intervals.',
      ],
    },
  ];

  return (
    <div className='flex h-full items-center justify-center gap-6 pt-2'>
      {steps.map((step, index) => (
        <motion.div
          key={step.title}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: -12 }}
          transition={{ duration: 0.4, delay: index * 0.1 }}
          className={cn(
            'group card-gradient relative z-20 flex h-full flex-1 flex-col items-center justify-center gap-3 overflow-visible rounded-xl border p-5 transition-all duration-300',
            index + 1 === currentStep && 'border-primary/70 box-shadow',
            'hidden @xl/main-container:flex',
          )}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 + 0.2 }}
            className='relative z-30 mt-5 mb-4 flex flex-col items-center justify-center gap-2'
          >
            <div className='bg-secondary rounded-full p-2'>
              <step.icon className='text-accent-foreground h-4 w-4 transition-transform duration-300 group-hover:scale-110' />
            </div>
            <p className='text-accent-foreground text-md font-bold tracking-tight'>{step.title}</p>
          </motion.div>

          <div className='relative z-30 flex flex-1 flex-col items-center gap-1.5'>
            {step.description.map((line, lineIndex) => (
              <motion.p
                key={lineIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 + 0.3 + lineIndex * 0.1 }}
                className='text-muted-foreground/80 text-center text-sm leading-relaxed'
              >
                {line}
              </motion.p>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default MainGuide;
