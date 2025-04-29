import NavigationBar from './NavigationBar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className='flex h-screen min-h-screen w-screen max-w-screen overflow-x-hidden bg-gray-50'>
      <NavigationBar />
      <main className='grow overflow-y-auto'>{children}</main>
    </div>
  );
}
