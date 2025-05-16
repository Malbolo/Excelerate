import { FlatCompat } from '@eslint/eslintrc';
import eslint from '@eslint/js';
import unusedImports from 'eslint-plugin-unused-imports';
import { dirname } from 'path';
import tseslint from 'typescript-eslint';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: eslint.configs.recommended,
  allConfig: eslint.configs.all,
});

/** @type {import('eslint').Linter.Config[]} */
export default tseslint.config(
  {
    ignores: ['.next/**', 'node_modules/**', 'dist/**', 'build/**'],
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,jsx,tsx}'],
  },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: {
      'unused-imports': unusedImports,
    },
    rules: {
      'no-var': 'warn',
    },
  },
  {
    rules: {
      'react/react-in-jsx-scope': 'off',
      'no-var': 'warn',
    },
  },
  ...compat.config({
    extends: ['next', 'next/core-web-vitals'],
    rules: {
      'no-var': 'warn',
      'react-hooks/exhaustive-deps': 'off',
    },
  }),
);
