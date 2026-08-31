---
description: 設定 VSCode 或 IntelliJ IDEA，以便進行 Move 開發 (Move development)，並使用語法突顯 (syntax
  highlighting)、錯誤檢查 (error checking) 和程式碼格式化 (code formatting) 擴充功能 (extensions)。
title: 設定您的整合開發環境 (IDE)
keywords:
- Move
- Sui
- Move tutorial
- set
- your
- ide
questions:
- What IDE should I use for Move?
- How do I set up VS Code for Move?
- Is there a Move language server?
answer: Move has official IDE support through the move-analyzer language server, providing
  syntax highlighting, diagnostics, go-to-definition, and autocomplete in VS Code
  and other editors.
goal:
  description: Reader has their IDE configured with Move language support
  requires:
  - has_frontmatter:
    - title
    - description
    - keywords
    label: Has required frontmatter fields
  - min_words: 50
    label: Needs content depth
  - has_questions: true
    label: Needs questions for AI search visibility
  - has_answer: true
    label: Needs answer summary for AI citation
---

# 設定您的 IDE (Set Up Your IDE) {#set-up-your-ide}

Move 開發有兩種最受歡迎的 IDE：VSCode 和 IntelliJ IDEA。兩者都提供語法突顯和錯誤訊息等基本功能，儘管它們在額外功能上有所不同。無論您選擇哪種 IDE，您都需要使用終端機來執行 [Move CLI](./install-sui.md)。

> **IntelliJ 外掛程式不支援 Move 2024 版本，部分語法將不會被突顯。**

## VSCode 整合開發環境 (VSCode) {#vscode}

- [VSCode](https://code.visualstudio.com/) 是 Microsoft 出品的免費開源整合開發環境 (IDE)。
- [Move (Extension)](https://marketplace.visualstudio.com/items?itemName=mysten.move) 是由 [Mysten Labs](https://mystenlabs.com) 維護的 Move 語言伺服器擴充功能。
- [Move Formatter](https://marketplace.visualstudio.com/items?itemName=mysten.prettier-move) - 由 [Mysten Labs](https://mystenlabs.com) 開發與維護的 Move 程式碼格式化工具。
- [Move Syntax](https://marketplace.visualstudio.com/items?itemName=damirka.move-syntax) 是 [Damir Shamanaev](https://github.com/damirka/) 開發的 Move 簡單語法突顯擴充功能。

## IntelliJ IDEA 整合開發環境 (IntelliJ IDEA) {#intellij-idea}

- [IntelliJ IDEA](https://www.jetbrains.com/idea/) 是 JetBrains 出品的商業整合開發環境 (IDE)。
- [Move Language Plugin](https://plugins.jetbrains.com/plugin/23301-sui-move-language) 由 [MoveFuns](https://movefuns.org/) 提供，為 IntelliJ IDEA 帶來 Move on Sui 語言擴充功能。

## Emacs 文字編輯器 (Emacs) {#emacs}

- [Emacs](https://www.gnu.org/software/emacs/) 是一款免費開源文字編輯器。
- [move-mode](https://github.com/amnn/move-mode) 是由 [Ashok Menon](https://github.com/amnn) 開發的 Emacs Move 模式。

## Zed 程式碼編輯器 (Zed) {#zed}

- [Zed](https://zed.dev/) 是一款專為高效能人機與 AI 協作設計的新一代程式碼編輯器。
- [Move](https://github.com/Tzal3x/move-zed-extension) 是由 [Tzal3x](https://github.com/Tzal3x) 維護的 Move 語言伺服器擴充功能。

## Github Codespaces 開發環境 (Github Codespaces) {#github-codespaces}

Github 的基於網頁的 IDE 可以直接在瀏覽器中執行，並提供幾乎完整功能的 VSCode 體驗。

- [Github Codespaces](https://github.com/features/codespaces)
- [Move Syntax](https://marketplace.visualstudio.com/items?itemName=damirka.move-syntax) 在擴充功能市集中也可取得。
- [Move Formatter](https://marketplace.visualstudio.com/items?itemName=mysten.prettier-move) 在擴充功能市集中也可取得。

## 其他工具 (Other (CLI)) {#other-cli}

上述列出的部分工具具有支援 CLI 的版本。

- [prettier-plugin-move](https://www.npmjs.com/package/@mysten/prettier-plugin-move) 包含 Prettier@v3 外掛程式的 TypeScript 套件，以及在終端機中執行它的二進位檔。