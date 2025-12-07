/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        profit: '#10b981', // 盈利绿色
        loss: '#ef4444' // 亏损红色
      }
    }
  },
  plugins: []
}
