---
description: 安裝 Sui 二進位檔 (binary) 和 Move 編譯器 (compiler)，使用 suiup、Homebrew 或 Chocolatey 來開始開發 Move 智慧合約 (smart contract)。
title: 安裝 Sui
keywords:
  - Move
  - Sui
  - Move tutorial
  - install
  - sui
questions:
  - How do I install the Sui CLI?
  - How do I set up Sui for Move development?
answer: Install the Sui CLI using the official installer, then verify with sui --version to begin compiling and testing Move code.
goal:
  description: Reader has the Sui CLI installed and can run sui move commands
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

# 安裝 Sui (Install Sui) {#install-sui}

Move 是一種編譯式語言，因此您需要安裝一個編譯器才能編寫並執行 Move 程式。該編譯器已包含在 Sui 二進位檔中，可透過以下其中一種方法安裝或下載。

## 透過 suiup 安裝 (Installing via suiup) {#installing-via-suiup}

安裝 Sui 的最佳方式是使用 [`suiup`](https://github.com/MystenLabs/suiup)。它提供了一種簡單的方法來安裝二進位檔，並管理不同環境（例如 `testnet` 和 `mainnet`）的不同版本二進位檔。

`suiup` 的安裝說明可以在[儲存庫的 README](https://github.com/MystenLabs/suiup) 中找到。

要安裝 Sui，請執行以下指令：

```bash
suiup install sui
```

## 下載二進位檔 (Download Binary) {#download-binary}

您可以從[發行頁面](https://github.com/MystenLabs/sui/releases)下載最新的 Sui 二進位檔。該二進位檔適用於 macOS、Linux 和 Windows。為了教育目的和開發，我們建議使用 `mainnet` 版本。

## 使用 Homebrew (MacOS) 安裝 (Install Using Homebrew (MacOS)) {#install-using-homebrew-macos}

您可以使用 [Homebrew](https://brew.sh/) 套件管理器安裝 Sui。

```bash
brew install sui
```

## 使用 Chocolatey (Windows) 安裝 (Install Using Chocolatey (Windows)) {#install-using-chocolatey-windows}

您可以使用適用於 Windows 的 [Chocolatey](https://chocolatey.org/install) 套件管理器安裝 Sui。

```bash
choco install sui
```

## 使用 Cargo (MacOS, Linux) 建置 (Build Using Cargo (MacOS, Linux)) {#build-using-cargo-macos-linux}

您可以透過使用 Cargo 套件管理器（需要 Rust）來在本地安裝並建置 Sui。

```bash
cargo install --git https://github.com/MystenLabs/sui.git sui --branch mainnet
```

如果您要針對 `testnet` 或 `devnet`，請將此處的分支目標更改為 `testnet` 或 `devnet`。

請使用以下指令確保您的系統擁有最新的 Rust 版本。

```bash
rustup update stable
```

## 故障排除 (Troubleshooting) {#troubleshooting}

有關安裝過程的故障排除，請參閱 [安裝 Sui](https://docs.sui.io/guides/developer/getting-started/sui-install) 指南。
