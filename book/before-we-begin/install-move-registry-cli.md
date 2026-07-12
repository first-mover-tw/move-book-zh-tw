---
description:
  安裝 Move 登錄檔 CLI (Move Registry (MVR) CLI) 以發佈、探索並管理可重複使用的 Sui 開發用 Move
  套件。
---

# 安裝 MVR (Install MVR) {#install-mvr}

[Move Registry (MVR)](https://moveregistry.com) 是 Move 的套件管理工具。它讓任何人都能在以 Move 撰寫的新應用程式中發布並使用已發布的套件。本機執行檔可用來搜尋登錄檔中的套件，也可以在 Sui CLI 建構流程中安裝這些套件。

## 透過 suiup 安裝 (Installing via suiup) {#installing-via-suiup}

安裝 MVR 最好的方式是使用 [`suiup`](https://github.com/MystenLabs/suiup)。Suiup 提供簡便的方式來更新與管理不同版本的執行檔。

`suiup` 的安裝說明可以在
[repository README](https://github.com/MystenLabs/suiup) 中找到。

要安裝 Move Registry CLI，請執行以下指令：

```bash
suiup install mvr
```

安裝完成後，Move Registry 會以 `mvr` 的形式提供使用。

## 下載執行檔 (Download Binary) {#download-binary}

你可以從
[releases page](https://github.com/MystenLabs/mvr/releases) 下載最新的 MVR 執行檔。此執行檔支援 macOS、
Linux 與 Windows。與 [Sui](./install-sui.md) 不同，MVR 執行檔在不同環境間不會變動，並同時支援 `testnet` 與 `mainnet`。

## 使用 Cargo 安裝 (Install Using Cargo) {#install-using-cargo}

你可以使用 Cargo 在本機安裝並建構 MVR（需要 Rust）

```bash
cargo install --locked --git https://github.com/mystenlabs/mvr --branch release mvr
```

## 疑難排解 (Troubleshooting) {#troubleshooting}

若要排解安裝過程中的問題，請參閱
[Install MVR](https://docs.suins.io/move-registry/tooling/mvr-cli#installation) 指南。

## 使用 MVR (Using MVR) {#using-mvr}

若要了解如何在登錄檔中尋找套件，並將其作為專案中的相依項使用，請參閱
[Using Move Registry](./../guides/using-move-registry) 指南。
