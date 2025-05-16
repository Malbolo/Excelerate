import { useState } from 'react';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';

import { useLoginAPI, useSignupAPI } from '@/apis/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';

import {
  LoginFormValues,
  SignupFormValues,
  initialLoginFormValues,
  initialSignupFormValues,
  loginSchema,
  signupSchema,
} from './authSchema';

export default function AuthPage() {
  const [isLoginMode, setIsLoginMode] = useState(true);

  const login = useLoginAPI();
  const signup = useSignupAPI();

  const form = useForm<LoginFormValues | SignupFormValues>({
    resolver: zodResolver(isLoginMode ? loginSchema : signupSchema),
    defaultValues: isLoginMode ? initialLoginFormValues : initialSignupFormValues,
    mode: 'onChange',
  });

  const toggleMode = () => {
    setIsLoginMode(prevMode => !prevMode);
    form.reset();
  };

  const onSubmit = async (values: LoginFormValues | SignupFormValues) => {
    if (isLoginMode) {
      login(values as LoginFormValues);
    } else {
      signup(values as SignupFormValues);
      setIsLoginMode(true);
      form.reset();
    }
  };

  return (
    <div className='flex h-full w-full items-center justify-center p-4'>
      <Card className='w-full max-w-md'>
        <CardHeader className='text-center'>
          <CardTitle className='text-2xl font-bold'>{isLoginMode ? 'Login' : 'Sign Up'}</CardTitle>
          <CardDescription>
            {isLoginMode
              ? 'Enter your email and password to login.'
              : 'Enter your information to create a new account.'}
          </CardDescription>
        </CardHeader>
        <Form {...form}>
          {form.formState.errors.root?.serverError && (
            <div className='p-4 text-center text-sm text-red-500'>{form.formState.errors.root.serverError.message}</div>
          )}
          <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
            <CardContent className='space-y-4'>
              <FormField
                control={form.control}
                name='email'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder='you@example.com' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name='password'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type='password' placeholder='********' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              {!isLoginMode && (
                <>
                  <FormField
                    control={form.control}
                    name='name'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>name</FormLabel>
                        <FormControl>
                          <Input placeholder='name' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='department'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Department</FormLabel>
                        <FormControl>
                          <Input placeholder='Your Department' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}
            </CardContent>
            <CardFooter className='flex flex-col gap-4'>
              <Button type='submit' className='w-full' disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting ? 'Processing...' : isLoginMode ? 'Login' : 'Sign Up'}
              </Button>
              <Button type='button' variant='link' onClick={toggleMode} className='text-sm'>
                {isLoginMode ? "Don't have an account? Sign Up" : 'Already have an account? Login'}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
