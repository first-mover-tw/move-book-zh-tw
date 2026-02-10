---
title: '套件 (Packages) | 參考手冊'
description: "Move 套件參考手冊：套件結構、Move.toml 清單檔案、依賴關係、具名地址以及套件編譯。"
---

# 套件 (Packages)

套件允許 Move 程式設計師更輕鬆地重用程式碼並在專案間分享。Move 套件系統允許程式設計師輕鬆地：

- 定義包含 Move 程式碼的套件；
- 透過 [具名地址 (named addresses)](./primitive-types/address) 對套件進行參數化；
- 在其他 Move 程式碼中導入並使用套件，並實例化具名地址；
- 構建套件並從套件生成相關的編譯產物；以及
- 圍繞已編譯的 Move 產物使用通用界面。

## 套件結構與清單 (Manifest) 語法

一個 Move 套件源目錄包含一個 `Move.toml` 套件清單檔案、一個生成的 `Move.lock` 檔案以及一組子目錄：

```plaintext
a_move_package
├── Move.toml      (必填)
├── Move.lock      (自動生成)
├── sources        (必填)
├── doc_templates  (選填)
├── examples       (選填, 測試與開發模式)
└── tests          (選填, 測試模式)
```

標記為「必填」的目錄和檔案必須存在，該目錄才會被視為 Move 套件並進行構建。選填目錄可以存在，如果存在，它們將根據構建套件時使用的模式包含在編譯過程中。例如，在「開發 (dev)」或「測試 (test)」模式下構建時，`tests` 和 `examples` 目錄也將被包含在內。

逐一說明如下：

1. [`Move.toml`](#movetoml) 檔案是套件清單，是將目錄視為 Move 套件的必要條件。此檔案包含有關套件的中繼資料 (metadata)，例如名稱、依賴關係等。
1. [`Move.lock`](#movelock) 檔案由 Move CLI 生成，包含套件及其依賴關係的固定構建版本。它用於確保在不同構建之間使用一致的版本，並使依賴關係的更改在該檔案中明顯體現。
1. `sources` 目錄是必填的，包含組成套件的 Move 模組。此目錄中的模組將始終被包含在編譯過程中。
1. `doc_templates` 目錄可以包含在為套件生成文件時使用的文件範本。
1. `examples` 目錄可以存放僅用於開發和/或教學的額外程式碼，這在 `test` 或 `dev` 模式以外進行編譯時不會被包含。
1. `tests` 目錄可以包含僅在 `test` 模式下編譯或運行 [Move 單元測試](./unit-testing) 時才包含的 Move 模組。

### Move.toml

Move 套件清單定義在 `Move.toml` 檔案中，具有以下語法。選填欄位標有 `*`，`+` 表示一個或多個元素：

```toml
[package]
name = <string>
edition* = <string>      # 例如，"2024.alpha" 表示使用 Move 2024 版本，
                         # 目前處於 alpha 階段。如果未指定，將預設為最新的穩定版本。
license* = <string>              # 例如，"MIT", "GPL", "Apache 2.0"
authors* = [<string>,+]  # 例如，["Joe Smith (joesmith@noemail.com)", "John Snow (johnsnow@noemail.com)"]

# 外部工具可能會向此部分添加額外欄位。例如，在 Sui 上會添加以下部分：
published-at* = "<hex-address>" # 套件發布的地址。應在第一次發布後設置。

[dependencies] # (選填部分) 依賴關係的路徑
# 以以下格式宣告依賴關係的一個或多行

# ##### 本地依賴 (Local Dependencies) #####
# 對於本地依賴，使用 `local = path`。路徑相對於套件根目錄
# Local = { local = "../path/to" }
# 若要解決版本衝突並強制使用特定版本的依賴覆蓋，您可以使用 `override = true`
# Override = { local = "../conflicting/version", override = true }
# 若要在依賴關係中實例化地址數值，請使用 `addr_subst`
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

# ##### Git 依賴 (Git Dependencies) #####
# 對於遠端導入，使用 `{ git = "...", subdir = "...", rev = "..." }`。
# 必須提供修訂版本 (Revision)，它可以是分支、標籤或提交雜湊值 (commit hash)。
# 如果未指定 `subdir`，則使用儲存庫的根目錄。
# MyRemotePackage = { git = "https://some.remote/host.git", subdir = "remote/path", rev = "main" }
<string> = {
    git = <以 .git 結尾的 URL>,
    subdir=<git 儲存庫內包含 Move.toml 的目錄路徑>,
    rev=<git 提交雜湊值>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[addresses]  # (選填部分) 在此套件中宣告具名地址
# 以以下格式宣告具名地址的一個或多行
# 與套件名稱匹配的地址必須設置為 `"0x0"`，否則將無法發布。
<addr_name> = "_" | "<hex_address>" # 例如，std = "_" 或 my_addr = "0xC0FFEECAFE"

# 具名地址在 Move 中可作為 `@name` 存取。它們也會被匯出：
# 例如，`std = "0x1"` 由標準函數庫匯出。
# alice = "0xA11CE"

[dev-dependencies] # (選填部分) 與 [dependencies] 部分相同，但僅包含在 "dev" 和 "test" 模式中
# dev-dependencies 部分允許為 `--test` 和 `--dev` 模式覆蓋依賴關係。
# 您可以在此處引入僅限測試的依賴關係。
# Local = { local = "../path/to/dev-build" }
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}
<string> = {
    git = <以 .git 結尾的 URL>,
    subdir=<git 儲存庫內包含 Move.toml 的目錄路徑>,
    rev=<git 提交雜湊值>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[dev-addresses] # (選填部分) 與 [addresses] 部分相同，但僅包含在 "dev" 和 "test" 模式中
# dev-addresses 部分允許在 `--test` 和 `--dev` 模式下覆寫具名地址。
<addr_name> = "<hex_address>" # 例如，alice = "0xB0B"
```

一個最小化套件清單的範例：

```toml
[package]
name = "AName"
```

一個更標準的套件清單範例，它還包含了 Move 標準函數庫，並將來自 `LocalDep` 套件的具名地址 `std` 實例化為地址值 `0x1`：

```toml
[package]
name = "AName"
license = "Apache 2.0"

[addresses]
address_to_be_filled_in = "_"
specified_address = "0xB0B"

[dependencies]
# 本地依賴
LocalDep = { local = "projects/move-awesomeness", addr_subst = { "std" = "0x1" } }
# Git 依賴
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }

[dev-addresses] # 用於開發此模組時
address_to_be_filled_in = "0x101010101"
```

套件清單中的大多數部分都是不言自明的，但具名地址可能有點難以理解，因此我們在 [編譯期間的具名地址](#編譯期間的具名地址) 中更詳細地介紹。

## 編譯期間的具名地址

回想一下 Move 具有 [具名地址 (named addresses)](./primitive-types/address)，且具名地址不能在 Move 中宣告。相反地，它們是在套件層級宣告的：在 Move 套件的清單檔案 (`Move.toml`) 中，您可以宣告套件中的具名地址、實例化其他具名地址，以及在 Move 套件系統內重新命名來自其他套件的具名地址。

讓我們逐一查看這些操作，以及它們是如何在套件清單中執行的：

### 宣告具名地址

假設我們在 `example_pkg/sources/A.move` 中有一個 Move 模組如下：

```move
module named_addr::a {
    public fun x(): address { @named_addr }
}
```

我們可以在 `example_pkg/Move.toml` 中以兩種不同的方式宣告具名地址 `named_addr`。第一種：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "_"
```

將 `named_addr` 宣告為套件 `example_pkg` 中的具名地址，且 *此地址可以是任何有效的地址值*。特別是，導入套件可以選擇將具名地址 `named_addr` 的數值設置為其希望的任何地址。直觀地說，您可以將此視為透過具名地址 `named_addr` 對套件 `example_pkg` 進行參數化，隨後該套件可以由導入套件實例化。

`named_addr` 也可以宣告為：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "0xCAFE"
```

這說明具名地址 `named_addr` 正好是 `0xCAFE` 且無法更改。這對其他導入套件很有用，因為它們可以使用此具名地址，而無需擔心分配給它的確切數值。

透過這兩種不同的宣告方法，具名地址資訊可以透過兩種方式在套件圖 (package graph) 中流動：

- 前者（"未配置的具名地址"）允許具名地址數值從導入端流向宣告端。
- 後者（"已配置的具名地址"）允許具名地址數值從宣告端向套件圖上游流向使用端。

透過這兩種在整個套件圖中流動具名地址資訊的方法，理解有關作用域 (scoping) 和重新命名的規則變得非常重要。

## 具名地址的作用域與重新命名

如果滿足以下條件，套件 `P` 中的具名地址 `N` 就在作用域內：

1. `P` 宣告了一個具名地址 `N`；或者
2. 在 `P` 的傳遞依賴 (transitive dependencies) 中的某個套件宣告了具名地址 `N`，且套件圖中 `P` 與 `N` 的宣告套件之間存在一條依賴路徑，且該路徑上沒有對 `N` 進行重新命名。

此外，套件中的每個具名地址都會被匯出。因此，根據上述作用域規則，每個套件都可以看作是帶有一組具名地址的，當套件被導入時，這些具名地址將被引入作用域。例如，如果您導入 `example_pkg`，該導入也會將 `named_addr` 具名地址引入作用域。正因為如此，如果 `P` 導入了兩個套件 `P1` 和 `P2`，這兩個套件都宣告了一個具名地址 `N`，那麼在 `P` 中就會出現一個問題：當在 `P` 中引用 `N` 時，指的是哪一個「`N`」？是來自 `P1` 還是 `P2` 的那個？為了防止關於具名地址來源的這種歧義，我們強制要求套件中所有相依性引入的作用域集合必須是不相交的 (disjoint)，並提供一種在導入引入它們的套件時 *重新命名具名地址* 的方法。

在我們上面的 `P`、`P1` 和 `P2` 範例中，導入時重新命名具名地址可以執行如下操作：

```toml
[package]
name = "P"
...
[dependencies]
P1 = { local = "some_path_to_P1", addr_subst = { "P1N" = "N" } }
P2 = { local = "some_path_to_P2"  }
```

透過這種重新命名，`N` 指的是來自 `P2` 的 `N`，而 `P1N` 將指的是來自 `P1` 的 `N`：

```move
module N::A {
    public fun x(): address { @P1N }
}
```

請務必注意，*重新命名不是區域性的*：一旦具名地址 `N` 在套件 `P` 中被重新命名為 `N2`，所有導入 `P` 的套件將看不到 `N`，而只能看到 `N2`，除非 `N` 從 `P` 外部重新引入。這就是為什麼本節開頭作用域規則中的規則 (2) 指定了「套件圖中 `P` 與 `N` 的宣告套件之間的一條路徑，且沒有對 `N` 進行重新命名」。

### 實例化具名地址

具名地址可以在套件圖中多次實例化，只要它始終具有相同的數值即可。如果同一個具名地址（無論是否重新命名）在套件圖中以不同的數值實例化，則會報錯。

僅當所有具名地址都解析為一個值時，才能編譯 Move 套件。如果套件希望公開一個未實例化的具名地址，這就會出現問題。這就是 `[dev-addresses]` 部分部分解決的問題。此部分可以為具名地址設置數值，但不能引入任何具名地址。此外，只有根套件中的 `[dev-addresses]` 會包含在 `dev` 模式中。例如，具有以下清單的根套件在 `dev` 模式之外將無法編譯，因為 `named_addr` 將未實例化：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "_"

[dev-addresses]
named_addr = "0xC0FFEE"
```

## 用法與產物 (Artifacts)

Move 套件系統在 CLI 中提供了一個命令列選項：`sui move <command> <command_flags>`。除非提供了特定路徑，否則所有套件命令都將在目前的 Move 套件中運行。Move CLI 命令和標籤的完整列表可以透過執行 `sui move --help` 來查看。

### 產物 (Artifacts)

可以使用 CLI 命令編譯套件。這將建立一個包含構建相關產物（包括位元組碼二進位檔案、源映射和文件）的 `build` 目錄。`build` 目錄的一般佈局如下：

```plaintext
a_move_package
├── BuildInfo.yaml
├── bytecode_modules
│   ├── dependencies
│   │   ├── <dep_pkg_name>
│   │   │   └── *.mv
│   │   ...
│   │   └──  <dep_pkg_name>
│   │       └── *.mv
│   ...
│   └── *.mv
├── docs
│   ├── dependencies
│   │   ├── <dep_pkg_name>
│   │   │   └── *.md
│   │   ...
│   │   └──  <dep_pkg_name>
│   │       └── *.md
│   ...
│   └── *.md
├── source_maps
│   ├── dependencies
│   │   ├── <dep_pkg_name>
│   │   │   └── *.mvsm
│   │   ...
│   │   └──  <dep_pkg_name>
│   │       └── *.mvsm
│   ...
│   └── *.mvsm
└── sources
    ...
    └── *.move
    ├── dependencies
    │   ├── <dep_pkg_name>
    │   │   └── *.move
    │   ...
    │   └──  <dep_pkg_name>
    │       └── *.move
    ...
    └── *.move
```

## Move.lock

當套件構建時，會在 Move 套件的根目錄下生成 `Move.lock` 檔案。`Move.lock` 檔案包含有關您的套件及其構建配置的資訊，並作為 Move 編譯器與其他工具（如特定鏈的命令列介面和第三方套件管理器）之間的通訊層。

與 `Move.toml` 檔案一樣，`Move.lock` 檔案是基於文本的 TOML 檔案。然而，與套件清單不同的是，`Move.lock` 檔案不打算讓您直接編輯。工具鏈上的進程（如 Move 編譯器）會存取並編輯該檔案，以讀取與向其追加相關資訊。您也絕不能將檔案從根目錄移動，因為它需要與套件中的 `Move.toml` 清單處於同一層級。

如果您為套件使用版本控制，建議的做法是檢入與您所需的構建或發布套件相對應的 `Move.lock` 檔案。這可以確保套件的每次構建都是原始構建的精確副本，並且對構建的更改將在 `Move.lock` 檔案的更改中體現出來。

`Move.lock` 檔案是一個 TOML 檔案，目前包含以下欄位。

**注意**：未來或其他第三方套件管理器也可能向鎖定檔案添加其他欄位。

### `[move]` 部分

此部分包含鎖定檔案中所需的核心資訊：

- 鎖定檔案的版本（用於後向相容性檢查，以及未來對鎖定檔案更改的版本控制）。
- 用於生成此鎖定檔案的 `Move.toml` 檔案的雜湊值。
- 所有相依性的 `Move.lock` 檔案的雜湊值。如果不存在相依性，這將是一個空字串。
- 相依性清單。

```toml
[move]
version = <string> # 鎖定檔案版本，用於後向相容性檢查。
manifest_digest = <hash> # 用於生成此鎖定檔案的 Move.toml 檔案的 Sha3-256 雜湊值。
deps_digest = <hash> # 所有相依性的 Move.lock 檔案的 Sha3-256 雜湊值。如果不存在相依性，這將是一個空字串。
dependencies = { (name = <string>)* } # 相依性列表。如果沒有相依性則不顯示。
```

### `[[move.package]]` 部分

在 Move 編譯器解析套件的每個相依性後，它會將相依性的位置寫入 `Move.lock` 檔案。如果相依性解析失敗，編譯器將不會寫入 `Move.lock` 檔案，且構建失敗。如果所有相依性都解析成功，`Move.lock` 檔案將包含該套件所有傳遞依賴項的位置（本地和遠端）。這些資訊將以以下格式存儲在 `Move.lock` 檔案中：

```toml
# ...

[[move.package]]
name = "A"
source = { git = "https://github.com/b/c.git", subdir = "e/f", rev = "a1b2c3" }

[[move.package]]
name = "B"
source = { local = "../local-dep" }
```

### `[move.toolchain-version]` 部分

如上所述，外部工具可能會向鎖定檔案添加額外欄位。例如，Sui 套件管理器會向鎖定檔案添加工具鏈版本資訊，然後可用於鏈上源驗證：

```toml
# ...

[move.toolchain-version]
compiler-version = <string> # 用於構建套件的 Move 編譯器版本，例如 "1.21.0"
edition = <string> # 用於構建套件的 Move 語言版本，例如 "2024.alpha"
flavor = <string> # 用於構建套件的 Move 編譯器變體，例如 "sui"
```
