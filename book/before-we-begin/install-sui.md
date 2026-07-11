---
description: '安裝 Sui 二進位檔與 Move 編譯器 (Sui binary and Move compiler)


  使用 suiup、Homebrew 或 Chocolatey 安裝 Sui 二進位檔與 Move 編譯器，開始開發 Move 智慧合約。'
---

# 安裝 Sui

Move 是一門編譯型語言，因此您需要安裝編譯器才能編寫和執行 Move 程式。編譯器包含在 Sui 二進位檔案中，您可以透過以下任一方法進行安裝或下載。

## 透過 suiup 安裝

安裝 Sui 的最佳方式是使用 [`suiup`](https://github.com/MystenLabs/suiup)。它提供了安裝二進位檔案的簡便方法，並能為不同環境（例如 `testnet` 和 `mainnet`）管理不同版本的二進位檔案。

`suiup` 的安裝說明可以在 [其 GitHub 儲存庫的 README](https://github.com/MystenLabs/suiup) 中找到。

要安裝 Sui，請執行以下指令：

```bash
suiup install sui
```

## 下載二進位檔案

您可以從 [發佈頁面 (releases page)](https://github.com/MystenLabs/sui/releases) 下載最新的 Sui 二進位檔案。該二進位檔案適用於 macOS、Linux 和 Windows。基於教學和開發目的，我們建議使用 `mainnet` 版本。

## 使用 Homebrew 安裝 (MacOS)

您可以使用 [Homebrew](https://brew.sh/) 套件管理員來安裝 Sui。

```bash
brew install sui
```

## 使用 Chocolatey 安裝 (Windows)

您可以使用 Windows 的 [Chocolatey](https://chocolatey.org/install) 套件管理員來安裝 Sui。

```bash
choco install sui
```

## 使用 Cargo 編譯 (MacOS, Linux)

您可以使用 Cargo 套件管理員（需要 Rust）在本地安裝並編譯 Sui。

```bash
cargo install --git https://github.com/MystenLabs/sui.git sui --branch mainnet
```

如果您鎖定其他環境，請將此處的分支目標更改為 `testnet` 或 `devnet`。

請使用以下指令確保您的系統裝有最新的 Rust 版本。

```bash
rustup update stable
```

## 故障排除

有關安裝過程中的故障排除，請參閱 [安裝 Sui](https://docs.sui.io/guides/developer/getting-started/sui-install) 指南。
