module.exports = {
  apps: [
    {
      name: 'shift-maker-backend',
      script: 'python',
      args: '-m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000',
      cwd: '/home/user/webapp',
      env: {
        NODE_ENV: 'development'
      }
    },
    {
      name: 'shift-maker-frontend',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 5173',
      cwd: '/home/user/webapp/frontend',
      env: {
        NODE_ENV: 'development'
      }
    }
  ]
};