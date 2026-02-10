# Move Book (繁體中文版)

這是 [Move Book](https://move-book.com) 和 [Move 語言參考手冊 (Move Language Reference)](https://move-book.com/reference) 的繁體中文原始碼庫。

## 專案結構

- **book**: 包含主要的 Move Book 內容。
- **reference**: 包含 Move 語言參考手冊。
- **packages**: 包含兩本書中所使用的程式碼範例。
- **site**: 包含 [Docusaurus](https://docusaurus.io) 的配置以及自定義插件。

## 在本地運行

### 前置條件

- NodeJS
- `pnpm` (安裝指令：`npm i -g pnpm`)

### 本地伺服器

> 所有指令均可在根目錄下執行。

```bash
pnpm start
```

_您可以在 `http://localhost:3000` 訪問本書。_

### 生產環境建置測試 (Production Build Test)

```bash
pnpm build
pnpm serve
```

## 封存 (Archive)

若需查看舊版內容，請參閱 `archive` 分支。
