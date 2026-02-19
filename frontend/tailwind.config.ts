import type { Config } from 'tailwindcss';
import typography from '@tailwindcss/typography';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
      },
      typography: {
        chat: {
          css: {
            '--tw-prose-body': 'inherit',
            '--tw-prose-headings': 'inherit',
            '--tw-prose-links': '#2563eb',
            '--tw-prose-bold': 'inherit',
            '--tw-prose-code': 'inherit',
            '--tw-prose-pre-bg': 'rgba(0, 0, 0, 0.05)',
            '--tw-prose-pre-code': 'inherit',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            p: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            'p:first-child': {
              marginTop: '0',
            },
            'p:last-child': {
              marginBottom: '0',
            },
            ul: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            ol: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            li: {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            h1: {
              fontSize: '1.25em',
              marginTop: '0.75em',
              marginBottom: '0.5em',
            },
            h2: {
              fontSize: '1.125em',
              marginTop: '0.75em',
              marginBottom: '0.5em',
            },
            h3: {
              fontSize: '1em',
              marginTop: '0.5em',
              marginBottom: '0.25em',
            },
            pre: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
              padding: '0.5em',
              borderRadius: '0.375rem',
              overflowX: 'auto',
            },
            code: {
              padding: '0.125em 0.25em',
              borderRadius: '0.25rem',
              backgroundColor: 'rgba(0, 0, 0, 0.05)',
              fontWeight: '400',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            'pre code': {
              padding: '0',
              backgroundColor: 'transparent',
            },
          },
        },
        'chat-invert': {
          css: {
            '--tw-prose-body': '#ffffff',
            '--tw-prose-headings': '#ffffff',
            '--tw-prose-links': '#93c5fd',
            '--tw-prose-bold': '#ffffff',
            '--tw-prose-code': '#ffffff',
            '--tw-prose-pre-bg': 'rgba(255, 255, 255, 0.1)',
            '--tw-prose-pre-code': '#ffffff',
            code: {
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
            },
          },
        },
      },
    },
  },
  plugins: [typography],
};

export default config;
