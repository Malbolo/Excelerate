import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Schedule } from '@/types/scheduler';

interface StatusToggleProps {
  schedule: Schedule;
}

const StatusToggle = ({ schedule }: StatusToggleProps) => {
  // 추후에 active라는 필드가 추가되면 그 필드를 사용하도록 변경해야 함
  const isActive = schedule.status !== 'pending';

  // 추후에 active라는 필드가 추가되면 그 필드를 사용하고 실제 API 호출은 여기서 하도록 변경해야 함
  const handleToggle = (checked: boolean) => {
    console.log('toggle', checked);
  };

  return (
    <div className='flex items-center space-x-2'>
      <Switch
        id={`status-toggle-${schedule.scheduleId}`}
        checked={isActive}
        onCheckedChange={handleToggle}
        aria-label={isActive ? 'Deactivate schedule' : 'Activate schedule'}
        onClick={e => e.stopPropagation()}
      />
      <Label
        htmlFor={`status-toggle-${schedule.scheduleId}`}
        className='text-xs'
      >
        {isActive ? 'Active' : 'Paused'}
      </Label>
    </div>
  );
};

export default StatusToggle;
