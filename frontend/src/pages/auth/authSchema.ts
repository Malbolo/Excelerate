import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid email.' }),
  password: z.string().min(1, { message: 'Please enter your password.' }),
});

const signupSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid email.' }),
  password: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long.' }),
  name: z
    .string()
    .min(2, { message: 'name must be at least 2 characters long.' }),
  department: z.string().min(1, { message: 'Please enter your department.' }),
});

export { loginSchema, signupSchema };

export type LoginFormValues = z.infer<typeof loginSchema>;
export type SignupFormValues = z.infer<typeof signupSchema>;

const initialLoginFormValues: LoginFormValues = {
  email: '',
  password: '',
};

const initialSignupFormValues: SignupFormValues = {
  email: '',
  password: '',
  name: '',
  department: '',
};

export { initialLoginFormValues, initialSignupFormValues };
