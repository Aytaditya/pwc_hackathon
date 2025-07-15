bash -c 'npm create vite@latest frontend -- --template react && \
cd frontend && \
npm install && \
npm install -D tailwindcss postcss autoprefixer && \
npx tailwindcss init -p && \
sed -i.bak "s/content: \\[\\]/content: [\".\\/index.html\", \"./src/**/*.{js,ts,jsx,tsx}\"]/" tailwind.config.js && \
printf "\n@tailwind base;\n@tailwind components;\n@tailwind utilities;\n" >> src/index.css'
