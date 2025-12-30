# React 前端

基于 [Vite](https://vitejs.dev/)、[React](https://reactjs.org/)、[TypeScript](https://www.typescriptlang.org/)、[TanStack Query](https://tanstack.com/query)、[TanStack Router](https://tanstack.com/router) 和 [Tailwind CSS](https://tailwindcss.com/) 构建。

## 环境要求

- Node.js 20+
- npm / pnpm / yarn

推荐使用 Node 版本管理器：
- [fnm](https://github.com/Schniz/fnm)（推荐，更快）
- [nvm](https://github.com/nvm-sh/nvm)

## 快速开始

### 步骤 1：安装 Node.js

```bash
cd frontend

# 使用 fnm
fnm install
fnm use

# 或使用 nvm
nvm install
nvm use
```

### 步骤 2：安装依赖

```bash
npm install
```

### 步骤 3：启动开发服务器

```bash
npm run dev
```

### 步骤 4：访问应用

打开浏览器访问：http://localhost:5173

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── client/          # 自动生成的 API 客户端
│   ├── components/      # React 组件
│   ├── hooks/           # 自定义 Hooks
│   ├── routes/          # 页面路由
│   ├── utils/           # 工具函数
│   └── main.tsx         # 应用入口
├── public/              # 公共静态文件
└── package.json         # 依赖配置
```

## 开发指南

### 添加新页面

在 `src/routes/` 目录下创建新的路由文件：

```tsx
// src/routes/my-page.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/my-page')({
  component: MyPage,
})

function MyPage() {
  return <div>My Page</div>
}
```

### 添加组件

在 `src/components/` 目录下创建组件：

```tsx
// src/components/MyComponent.tsx
export function MyComponent() {
  return <div>My Component</div>
}
```

### API 调用

使用自动生成的客户端：

```tsx
import { client } from '@/client'
import { useQuery } from '@tanstack/react-query'

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: () => client.GET('/api/v1/items/'),
  })

  if (isLoading) return <div>加载中...</div>
  return <div>{data}</div>
}
```

## 生成 API 客户端

当后端 API 变化时，需要重新生成前端客户端。

### 自动生成（推荐）

```bash
# 确保后端正在运行
./scripts/generate-client.sh
```

### 手动生成

```bash
# 1. 启动后端
docker compose up -d backend

# 2. 下载 OpenAPI JSON
curl http://localhost:8000/api/v1/openapi.json -o frontend/openapi.json

# 3. 生成客户端
cd frontend
npm run generate-client
```

## 使用远程 API

如果需要连接到远程 API，修改 `frontend/.env`：

```env
VITE_API_URL=https://api.my-domain.example.com
```

## 测试

### 端到端测试（E2E）

```bash
# 确保后端正在运行
docker compose up -d --wait backend

# 运行测试
npx playwright test

# UI 模式运行（可以看到浏览器）
npx playwright test --ui
```

## 常用命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check

# 生成 API 客户端
npm run generate-client
```

## 移除前端（API-only 模式）

如果只需要后端 API：

1. 删除 `./frontend` 目录
2. 从 `docker-compose.yml` 中移除 `frontend` 服务
3. 从 `docker-compose.override.yml` 中移除 `frontend` 和 `playwright` 服务

## 技术栈说明

| 技术 | 用途 |
|------|------|
| React | UI 框架 |
| TypeScript | 类型安全 |
| Vite | 构建工具 |
| TanStack Router | 路由管理 |
| TanStack Query | 数据获取和缓存 |
| Tailwind CSS | CSS 框架 |
| shadcn/ui | UI 组件库 |
| Playwright | E2E 测试 |

## 故障排查

### 依赖安装失败

尝试清理缓存：

```bash
rm -rf node_modules package-lock.json
npm install
```

### API 请求失败

1. 确保后端正在运行：http://localhost:8000/docs
2. 检查 `frontend/.env` 中的 `VITE_API_URL`
3. 检查后端 CORS 配置

### 热重载不工作

重启开发服务器：

```bash
# Ctrl+C 停止
npm run dev
```

## 样式开发

项目使用 Tailwind CSS，可以直接在组件中使用类名：

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Hello World
</div>
```

shadcn/ui 组件已预配置，可以按需添加新组件：

```bash
npx shadcn-ui@latest add button
```

## 需要帮助？

- [本地开发指南](../LOCAL_DEV_ZH.md)
- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [TanStack Router 文档](https://tanstack.com/router/latest)
