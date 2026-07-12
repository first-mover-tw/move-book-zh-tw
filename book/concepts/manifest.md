---
description: Move.toml 套件清單 (Package Manifest)：套件中繼資料、相依套件、具名地址與相依套件覆寫詳解。
---

# 套件清單 (Package Manifest) {#package-manifest}

`Move.toml` 是描述 [套件](./packages) 及其相依性的清單檔案。它以 [TOML](https://toml.io/en/) 格式撰寫，包含多個區段，其中最重要的是 `[package]`、`[dependencies]` 與 `[addresses]`。

```toml
[package]
name = "my_project"
edition = "2024"

[dependencies]
example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }
```

## 區段 (Sections) {#sections}

### 套件 (Package) {#package}

`[package]` 區段用來描述套件。此區段中的欄位皆不會發佈到鏈上，但會用於工具與版本發布管理；它們也會指定編譯器使用的 Move 版本。

- `name` - 匯入此套件時使用的名稱；
- `edition` - Move 語言的版本；目前唯一有效的值是 `2024`；

### 相依性 (Dependencies) {#dependencies}

`[dependencies]` 區段用來指定專案的相依性。每個相依性都以鍵值對的形式指定，其中鍵是相依性的名稱，值是相依性的規格。相依性規格可以是 git repository 的網址，或是本機目錄的路徑。

```toml
# git repository
example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }

# 本地目錄
my_package = { local = "../my-package" }
```

套件也會從其相依性匯入具名地址。舉例來說，Sui 相依性會將 `std` 與 `sui` 地址加入專案中，可在程式碼中取代完整的 `0x1` 與 `0x2` 地址使用。

從 Sui CLI 1.45 版開始，若專案中沒有明確列出任何 Sui 系統套件（`std`、`sui`、`system`、`bridge` 與 `deepbook`），這些套件會自動被加入為相依性。

### 使用 Override 解決版本衝突 (Resolving Version Conflicts with Override) {#resolving-version-conflicts-with-override}

有時相依性之間會有同一個套件版本衝突的情況。舉例來說，如果你有兩個相依性使用不同版本的 Example 套件，你可以在 `[dependencies]` 區段中覆寫該相依性。作法是在該相依性中加入 `override` 欄位。此時會使用 `[dependencies]` 區段中指定的版本，而非該相依性自身指定的版本。

```toml
[dependencies]
example = { override = true, git = "https://github.com/example/example.git", subdir = "crates/sui-framework/packages/sui-framework", rev = "framework/testnet" }
```

## TOML 風格 (TOML Styles) {#toml-styles}

TOML 格式支援兩種表格書寫風格：inline 與 multiline。上面的範例使用的是 inline 風格，但也可以使用 multiline 風格。你不會想在 `[package]` 區段使用 multiline 風格，但它對相依性設定來說可能很有用。

```toml
# 單行樣式
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

- Sui Docs 中的 [Move Package Management](https://docs.sui.io/develop/manage-packages/move-package-management)。
- Move Reference 中的 [Packages](./../../reference/packages)。
