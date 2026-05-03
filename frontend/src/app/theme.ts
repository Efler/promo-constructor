import { createTheme } from '@mantine/core'

export const theme = createTheme({
  primaryColor: 'brand',
  primaryShade: 6,
  defaultRadius: 'md',
  fontFamily: '"Aptos", "Segoe UI Variable", "Segoe UI", sans-serif',
  black: '#111111',
  headings: {
    fontFamily: '"Aptos Display", "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif',
  },
  colors: {
    brand: [
      '#fdf5fa',
      '#f7e6f0',
      '#efc5dc',
      '#e6a0c6',
      '#d979af',
      '#cb5498',
      '#AE2573',
      '#921c5f',
      '#711549',
      '#531035',
    ],
  },
  shadows: {
    md: '0 16px 40px rgba(174, 37, 115, 0.14)',
  },
})
