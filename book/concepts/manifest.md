---
description: Move.toml 套件 (package) 資訊清單 (manifest)：套件 (package) 中繼資料 (metadata)、依賴
  (dependencies)、具名 (named) 地址 (addresses) 與依賴 (dependency) 覆寫 (overrides) 說明。
title: 套件 (Package) 清單 (Manifest)
keywords:
- Move
- Sui
- Move tutorial
- package
- manifest
questions:
- What is Package Manifest in Move?
- How do I use Package Manifest in Move?
- What is Sections in Move?
- What is TOML Styles in Move?
answer: 'The Move.toml package manifest: package metadata, dependencies, named addresses,
  and dependency overrides explained.'
goal:
  description: 'Reader understands the Move.toml package manifest: package metadata,
    dependencies, named addresses, and dependency overrides explained'
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

# 套件 Manifest (Package Manifest) {#package-manifest}

`Move.toml` 是描述[套件 (package)](./packages) 及其依賴項的 manifest 檔案。它以 [TOML](https://toml.io/en/) 格式撰寫，包含多個章節，其中最重要的是 `[package]`、`[dependencies]` 和 `[addresses]`。

```toml
[package]
name = "my_project"
edition = "2024"

[dependencies]
example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }
```

## 章節 (Sections) {#sections}

### 套件 (Package) {#package}

`[package]` 章節用於描述套件。此章節中的任何欄位皆不會發佈至鏈上，但會用於工具和發佈管理；它們也指定了編譯器的 Move 版本。

- `name` - 匯入套件時的名稱；
- `edition` - Move 語言的版本；目前唯一有效的值為 `2024`；

### 依賴項 (Dependencies) {#dependencies}

`[dependencies]` 章節用於指定專案的依賴項。每個依賴項都以鍵值對的形式指定，其中鍵是依賴項的名稱，值是依賴項規格。依賴項規格可以是 Git 儲存庫 URL 或本機目錄的路徑。

```toml
# Git 儲存庫
example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }

# 本機目錄
my_package = { local = "../my-package" }
```

套件也會從其依賴項匯入具名地址。例如，Sui 依賴項會將 `std` 和 `sui` 地址新增至專案，可在程式碼中取代完整的 `0x1` 和 `0x2` 地址使用。

從 Sui CLI 1.45 版開始，如果沒有明確列出任何 Sui 系統套件（`std`、`sui`、`system`、`bridge` 和 `deepbook`），將會自動新增為依賴項。

### 使用 Override 解決版本衝突 (Resolving Version Conflicts with Override) {#resolving-version-conflicts-with-override}

有時候依賴項之間會發生相同套件的不同版本之間發生衝突。例如，如果您有兩個依賴項使用不同版本的 Example 套件，您可以在 `[dependencies]` 章節中覆寫該依賴項。為此，請將 `override` 欄位新增至依賴項。將會使用 `[dependencies]` 章節中指定的依賴項版本，而非依賴項本身指定的版本。

```toml
[dependencies]
example = { override = true, git = "https://github.com/example/example.git", subdir = "crates/sui-framework/packages/sui-framework", rev = "framework/testnet" }
```

## TOML 樣式 (TOML Styles) {#toml-styles}

TOML 格式支援兩種表格樣式：內嵌 (inline) 和多行 (multiline)。上述範例皆使用內嵌樣式，但也可以使用多行樣式。您不會想將其用於 `[package]` 章節，但對於依賴項可能很有用。

```toml
# 內嵌樣式
[dependencies]
example = { override = true, git = "https://github.com/example/example.git", subdir = "crates/sui-framework/packages/sui-framework", rev = "framework/testnet" }
MyPackage = { local = "../my-package" }
```

```toml
# 多行樣式
[dependencies.example]
override = true
git = "https://github.com/example/example.git"
subdir = "crates/sui-framework/packages/sui-framework"
rev = "framework/testnet"

[dependencies.my_package]
local = "../my-package"
```

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的 [Move 套件管理 (Move Package Management)](https://docs.sui.io/develop/manage-packages/move-package-management)。
- Move 參考文件中的 [套件 (Packages)](./../../reference/packages)。
