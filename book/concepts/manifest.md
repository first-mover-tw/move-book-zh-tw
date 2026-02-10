# 專案清單 (Package Manifest)

`Move.toml` 是一個清單檔案，用於描述[套件](./packages)及其相依性。它以 [TOML](https://toml.io/en/) 格式編寫，包含多個區塊，其中最重要的是 `[package]`、`[dependencies]` 和 `[addresses]`。

```toml
[package]
name = "my_project"
version = "0.0.0"
edition = "2024"

[dependencies]
Example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }

[addresses]
std =  "0x1"
alice = "0xA11CE"

[dev-addresses]
alice = "0xB0B"
```

## 區塊設定

### Package (套件)

`[package]` 區塊用於描述套件。此區塊中的任何欄位都不會發佈在鏈上，但它們被用於工具和版本管理；它們還為編譯器指定 Move 版本。

- `name` - 套件被導入時的名稱；
- `version` - 套件的版本，可用於發佈管理；
- `edition` - Move 語言的版本；目前唯一有效的值是 `2024`。

### Dependencies (相依性)

`[dependencies]` 區塊用於指定專案的相依性。每個相依性都指定為鍵值對 (key-value pair)，其中鍵是相依性的名稱，值是相依性的規格。相依性規格可以是 Git 存儲庫 URL 或本地目錄的路徑。

```toml
# Git 存儲庫
Example = { git = "https://github.com/example/example.git", subdir = "path/to/package", rev = "framework/testnet" }
# 本地目錄
MyPackage = { local = "../my-package" }
```

套件還從其他套件導入地址。例如，Sui 相依性將 `std` 和 `sui` 地址添加到專案中。這些地址可以在程式碼中用作地址的別名。

從 Sui CLI 1.45 版本開始，如果沒有明確列出 Sui 系統套件（`std`、`sui`、`system`、`bridge` 和 `deepbook`），它們會被自動添加為相依性。

### 使用 Override 解決版本衝突

有時相依性具有相同套件的衝突版本。例如，如果您有兩個使用不同版本 Example 套件的相依性，您可以在 `[dependencies]` 區塊中覆蓋該相依性。為此，請將 `override` 欄位添加到相依性中。`[dependencies]` 區塊中指定的相依性版本將被使用，而不是其自身指定的版本。

```toml
[dependencies]
Example = { override = true, git = "https://github.com/example/example.git", subdir = "crates/sui-framework/packages/sui-framework", rev = "framework/testnet" }
```

### Dev-dependencies (開發相依性)

可以在清單中添加 `[dev-dependencies]` 區塊。它用於在開發和測試模式下覆蓋相依性。例如，如果您想在開發模式下使用不同版本的 Sui 套件，您可以向 `[dev-dependencies]` 區塊添加自定義相依性規格。

### Addresses (地址)

`[addresses]` 區塊用於添加地址別名。任何地址都可以在此區塊中指定，然後在程式碼中用作別名。例如，如果您將 `alice = "0xA11CE"` 添加到此區塊，您可以在程式碼中使用 `alice` 作為 `0xA11CE`。

### Dev-addresses (開發地址)

`[dev-addresses]` 區塊與 `[addresses]` 相同，但僅適用於測試和開發模式。重要的是要記住，在此區塊中無法引入新的別名，只能覆蓋現有的別名。因此在上面的範例中，如果您將 `alice = "0xB0B"` 添加到此區塊，`alice` 地址在測試和開發模式下將是 `0xB0B`，在常規構建中將是 `0xA11CE`。

## TOML 風格

TOML 格式支持兩種表格風格：行內風格 (inline) 和多行風格 (multiline)。上面的範例使用的是行內風格，但也可以使用多行風格。您不會想在 `[package]` 區塊中使用它，但它對於相依性可能很有用。

```toml
# 行內風格
[dependencies]
Example = { override = true, git = "https://github.com/example/example.git", subdir = "crates/sui-framework/packages/sui-framework", rev = "framework/testnet" }
MyPackage = { local = "../my-package" }
```

```toml
# 多行風格
[dependencies.Example]
override = true
git = "https://github.com/example/example.git"
subdir = "crates/sui-framework/packages/sui-framework"
rev = "framework/testnet"

[dependencies.MyPackage]
local = "../my-package"
```

## 進一步閱讀

- Move 參考手冊中的[套件](./../../reference/packages)。
