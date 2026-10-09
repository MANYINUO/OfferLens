# OfferLens Web

Vue 3 + Vite 前端，包含求职工作台总览、投递记录、AI 职位匹配和简历版本管理。

## 启动

```powershell
cd offerlens-web
npm install
npm run dev
```

开发服务器将 `/api/*` 转发到 Java 服务 `http://localhost:8080`，并将 `/ai/*` 改写后转发到 Python 服务 `http://localhost:8000/api/*`。请先分别启动两个后端。

当前页面使用演示用户 `userId = 1`。切换用户前，需先在 `src/api.ts` 调整 `DEMO_USER_ID`。

## 页面

- `/`：投递阶段分布、回复与 Offer 统计、最近投递
- `/applications`：查询、筛选、搜索、创建投递记录并推进状态
- `/match`：提交简历和职位描述进行 AI 分析，可将匹配结果保存为投递记录
- `/resumes`：保存和删除简历文本版本，并在匹配页面载入

匹配分数和证据片段由 AI 服务生成，页面会提示用户回看简历与职位原文。
