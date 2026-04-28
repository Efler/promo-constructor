import { createTheme } from '@mantine/core'

export const theme = createTheme({
  primaryColor: 'brand',
  defaultRadius: 'md',
  fontFamily: '"Aptos", "Segoe UI Variable", "Segoe UI", sans-serif',
  headings: {
    fontFamily: '"Aptos Display", "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif',
  },
  colors: {
    brand: [
      '#faeef8',
      '#f3d8ec',
      '#ebb6dd',
      '#e18fcf',
      '#d96dc2',
      '#d150b5',
      '#c83fa8',
      '#bc3d96',
      '#983078',
      '#74245b',
    ],
  },
  shadows: {
    md: '0 16px 40px rgba(113, 33, 93, 0.12)',
  },
})
