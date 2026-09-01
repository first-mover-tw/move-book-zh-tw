---
description: 安裝 Move 註冊中心 (Move Registry) (MVR) 命令列介面 (CLI)，以發佈、探索及管理用於 Sui 開發的可重複使用
  Move 套件 (Move package)。
title: 安裝 MVR
keywords:
- Move
- Sui
- Move tutorial
- install
- mvr
questions:
- What is the Move Registry CLI?
- How do I install MVR?
- How do I manage Move dependencies?
answer: The Move Registry (MVR) CLI resolves and manages Move package dependencies
  from a decentralized registry for easier package sharing and reuse.
goal:
  description: Reader has MVR installed and can manage Move package dependencies
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

# 安裝 MVR (Install MVR) {#install-mvr}

[Move Registry (MVR)](https://moveregistry.com) 是一個 Move 的套件管理器。它允許任何人發布並在新 Move 應用程式中使用已發布的套件。本地二進位檔允許在註冊中心中搜尋套件，並將其安裝為 Sui CLI 建置過程的一部分。

## 透過 suiup 安裝 (Installing via suiup) {#installing-via-suiup}

安裝 MVR 的最佳方式是使用 [`suiup`](https://github.com/MystenLabs/suiup)。Suiup 提供了一種簡單的方式來更新和管理不同版本的二進位檔。

`suiup` 的安裝說明可以在[儲存庫的 README](https://github.com/MystenLabs/suiup) 中找到。

要安裝 Move Registry CLI，請執行以下指令：

```bash
suiup install mvr
```

安裝後，Move Registry 將可作為 `mvr` 使用。

## 下載二進位檔 (Download Binary) {#download-binary}

您可以從 [發布頁面](https://github.com/MystenLabs/mvr/releases) 下載最新的 MVR 二進位檔。此二進位檔適用於 macOS、Linux 和 Windows。與 [Sui](./install-sui.md) 不同，MVR 二進位檔在不同環境之間不會改變，並支援 `testnet` 和 `mainnet`。

## 使用 Cargo 安裝 (Install Using Cargo) {#install-using-cargo}

您可以使用 Cargo 在本地安裝和建置 MVR（需要 Rust）

```bash
cargo install --locked --git https://github.com/mystenlabs/mvr --branch release mvr
```

## 疑難排解 (Troubleshooting) {#troubleshooting}

有關安裝過程的疑難排解，請參閱 [安裝 MVR](https://docs.suins.io/move-registry/tooling/mvr-cli#installation) 指南。

## 使用 MVR (Using MVR) {#using-mvr}

要了解如何在註冊中心中尋找套件並將其作為專案中的依賴項使用，請參閱 [使用 Move Registry](./../guides/using-move-registry) 指南。
