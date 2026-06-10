# 📈 每日财经透视

每天 7:30 自动更新，聚合全球财经新闻 + AI 产业链分析的个人财经早报。

## 功能

- 🌏 **宏观风向** — 中美欧最新财经政策、经济数据
- 🏭 **产业链透视** — AI 将新闻串联，分析上下游影响（报告核心）
- 📊 **机构研报摘要** — 高盛、摩根、中金等机构观点
- 💡 **前沿科技** — 科技领域头条
- 🗣 **自媒体声音** — X/YouTube 财经大V观点
- 🔗 **原文速览** — 所有原文链接汇总
- 📋 **简报版** / 🔍 **深度版** 一键切换

## 技术栈

- **采集**：Python (RSS + NewsAPI)
- **分析**：DeepSeek API
- **展示**：纯静态 HTML (Tailwind CSS)
- **调度**：GitHub Actions
- **托管**：GitHub Pages（免费）

## 部署步骤

### 前置条件

- ✅ 一个 GitHub 账号（https://github.com）
- ✅ DeepSeek API Key（https://platform.deepseek.com 注册获取）
- ✅ NewsAPI Key（https://newsapi.org 注册获取）

### 第1步：上传代码到 GitHub

打开 https://github.com/historycloudfly-art ，创建一个新仓库叫 `daily-financial-report`，然后执行：

```bash
cd /c/Users/37126/Desktop/daily-financial-report
git init
git add .
git commit -m "初始化项目"
git remote add origin https://github.com/historycloudfly-art/daily-financial-report.git
git branch -M main
git push -u origin main
```

### 第2步：在 GitHub 仓库设置 Secrets

1. 打开你的 GitHub 仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"，添加以下 2 个：

| Secret 名称 | 值 |
|------------|-----|
| `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key |
| `NEWSAPI_KEY` | 你的 NewsAPI Key |

### 第3步：启用 GitHub Pages

1. 打开你的 GitHub 仓库 → **Settings** → **Pages**
2. **Source** 选 **"Deploy from a branch"**
3. **Branch** 选 **`gh-pages`** → 文件夹选 **`/ (root)`**
4. 点击 **"Save"**

### 第4步：手动触发一次

1. 打开 GitHub 仓库 → **Actions** 标签
2. 左侧点击 **"每日财经报告"**
3. 右侧点击 **"Run workflow"** → 绿色按钮
4. 等待几分钟，运行成功后 GitHub Pages 会自动更新

### 第5步：访问你的财经早报 🎉

部署完成后，访问：
```
https://historycloudfly-art.github.io/daily-financial-report/
```

以后每天 7:30，你的专属财经早报会自动更新。

## 本地测试

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API Key
export DEEPSEEK_API_KEY=sk-你的key
export NEWSAPI_KEY=你的newsapi密钥

# 3. 采集新闻
python scripts/collector.py

# 4. AI 分析
python scripts/analyzer.py

# 5. 构建网页
python scripts/builder.py

# 6. 打开网页
start site/index.html
```

## 免责声明

本工具仅供学习参考，所有内容由 AI 自动生成，不构成投资建议。新闻内容版权归原作者所有。
