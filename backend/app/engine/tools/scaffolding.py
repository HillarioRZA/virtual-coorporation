"""
Standalone Project Scaffolding Generator.
Menghasilkan berkas konfigurasi build mandiri (package.json, tsconfig, layout, tailwind, database.py)
agar proyek frontend dan backend yang dihasilkan agen dapat langsung dijalankan independen.
"""

from pathlib import Path
from typing import Dict


def scaffold_standalone_frontend(fe_dir: Path, project_id: str) -> None:
    """Menulis berkas konfigurasi Next.js 14 mandiri ke direktori frontend."""
    fe_dir.mkdir(parents=True, exist_ok=True)
    src_app = fe_dir / "src" / "app"
    src_app.mkdir(parents=True, exist_ok=True)

    package_json = f"""{{
  "name": "venture-app-{project_id[:8]}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "^14.2.14",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.447.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.2"
  }},
  "devDependencies": {{
    "typescript": "^5.6.2",
    "@types/node": "^20.16.10",
    "@types/react": "^18.3.10",
    "@types/react-dom": "^18.3.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.13"
  }}
}}"""

    tsconfig = """{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./src/*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}"""

    tailwind_config = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {} },
  plugins: [],
}"""

    postcss_config = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

    next_config = """/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true };
module.exports = nextConfig;"""

    globals_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  color: #ededed;
  background: #0a0a0a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}"""

    layout_tsx = """import "./globals.css";
export const metadata = {
  title: "Venture App Prototype",
  description: "Autonomous Multi-Agent Generated App",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}"""

    readme_md = f"""# Venture App Prototype ({project_id})
Dihasilkan secara otonom oleh **Virtual Tech Startup Multi-Agent System**.

## Cara Menjalankan Frontend Mandiri:
1. `npm install`
2. `npm run dev`
3. Buka `http://localhost:3000` di browser.
"""

    (fe_dir / "package.json").write_text(package_json, encoding="utf-8")
    (fe_dir / "tsconfig.json").write_text(tsconfig, encoding="utf-8")
    (fe_dir / "next.config.js").write_text(next_config, encoding="utf-8")
    (fe_dir / "tailwind.config.js").write_text(tailwind_config, encoding="utf-8")
    (fe_dir / "postcss.config.js").write_text(postcss_config, encoding="utf-8")
    (fe_dir / "README.md").write_text(readme_md, encoding="utf-8")

    # Tulis globals.css & layout.tsx jika belum ada
    if not (src_app / "globals.css").exists():
        (src_app / "globals.css").write_text(globals_css, encoding="utf-8")
    if not (src_app / "layout.tsx").exists():
        (src_app / "layout.tsx").write_text(layout_tsx, encoding="utf-8")


def scaffold_standalone_backend(be_dir: Path, project_id: str) -> None:
    """Menulis berkas pendukung FastAPI mandiri (database.py, schemas.py, README.md)."""
    be_dir.mkdir(parents=True, exist_ok=True)

    database_py = """# database.py - Database Session & Connection Provider
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
"""

    schemas_py = """# schemas.py - Base Pydantic Validation Schemas
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
"""

    readme_md = f"""# Venture Backend Service ({project_id})
Dihasilkan secara otonom oleh **Virtual Tech Startup Multi-Agent System**.

## Cara Menjalankan Backend:
1. `python -m venv venv && source venv/bin/activate` (atau `.\\venv\\Scripts\\activate` di Windows)
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload --port 8000`
"""

    (be_dir / "database.py").write_text(database_py, encoding="utf-8")
    (be_dir / "schemas.py").write_text(schemas_py, encoding="utf-8")
    (be_dir / "README.md").write_text(readme_md, encoding="utf-8")
