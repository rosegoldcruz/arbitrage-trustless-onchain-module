module.exports = {
  apps: [
    {
      name: 'atom-backend',
      script: 'uvicorn',
      args: 'backend.main:app --host 0.0.0.0 --port 8000',
      interpreter: 'python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'atom-adom-bot',
      script: 'python',
      args: 'backend/bots/working/ATOM.py',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M'
    }
  ]
};

