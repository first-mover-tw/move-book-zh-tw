---

description: "Install the Move Registry (MVR) CLI to publish, discover, and manage reusable Move packages for Sui development."
---

# 安裝 MVR

[Move Registry (MVR)](https://moveregistry.com) 是 Move 的套件管理員。它允許任何人發佈套件，並在以 Move 編寫的新應用程式中使用已發佈的套件。本地二進位檔案允許在註冊表中搜尋套件，並將其作為 Sui CLI 構建過程的一部分進行安裝。

## 透過 suiup 安裝

安裝 MVR 的最佳方式是使用 [`suiup`](https://github.com/MystenLabs/suiup)。Suiup 提供了一種輕鬆更新和管理不同版本二進位檔案的方法。

`suiup` 的安裝說明可以在 [其 GitHub 儲存庫的 README](https://github.com/MystenLabs/suiup) 中找到。

要安裝 Move Registry CLI，請執行以下指令：

```bash
suiup install mvr
```

安裝完成後，Move Registry 將可以透過 `mvr` 指令使用。

## 下載二進位檔案

您可以從 [發佈頁面 (releases page)](https://github.com/MystenLabs/mvr/releases) 下載最新的 MVR 二進位檔案。該二進位檔案適用於 macOS、Linux 和 Windows。與 [Sui](./install-sui.md) 不同，MVR 二進位檔案在不同環境之間不會改變，並且同時支援 `testnet` 和 `mainnet`。

## 使用 Cargo 安裝

您可以使用 Cargo（需要 Rust）在本地安裝並編譯 MVR。

```bash
cargo install --locked --git https://github.com/mystenlabs/mvr --branch release mvr
```

## 故障排除

有關安裝過程中的故障排除，請參閱 [安裝 MVR](https://docs.suins.io/move-registry/tooling/mvr-cli#installation) 指南。
