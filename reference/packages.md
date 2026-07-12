---
title: 套件 (Packages) | 參考手冊
description: Move 套件參考手冊 (Move packages reference)：套件配置 (package layout)、Move.toml
  清單檔 (manifest)、依賴 (dependencies)、具名地址 (named addresses)、套件編譯 (package compilation)。
---

# 套件 (Packages)

套件允許 Move 程式設計師更輕鬆地重複使用程式碼並跨專案共享。Move 套件系統允許程式設計師輕鬆地：

- 定義包含 Move 程式碼的套件；
- 透過 [具名地址](./primitive-types/address) 將套件參數化；
- 在其他 Move 程式碼中匯入和使用套件，並實例化具名地址；
- 建置套件並從套件產生相關的編譯產物；以及
- 圍繞編譯後的 Move 產物使用通用介面。

## 套件佈局與清單語法 (Package Layout and Manifest Syntax)

一個 Move 套件源目錄包含一個 `Move.toml` 套件清單檔案、一個產生的 `Move.lock` 檔案以及一組子目錄：

```plaintext
a_move_package
├── Move.toml      (必填)
├── Move.lock      (產生)
├── sources        (必填)
├── doc_templates  (選填)
├── examples       (選填，測試與開發模式)
└── tests          (選填，測試模式)
```

標記為「必填」的目錄和檔案必須存在，該目錄才會被視為 Move 套件並進行建置。選填目錄可以存在，若是存在，它們將根據建置套件時使用的模式包含在編譯過程中。例如，在「開發 (dev)」或「測試 (test)」模式下建置時，`tests` 和 `examples` 目錄也將被包含進去。

依次介紹各項：

1. [`Move.toml`](#movetoml) 檔案是套件清單，是目錄被視為 Move 套件的必要條件。此檔案包含有關套件的中繼資料（metadata），例如名稱、依賴項等。
1. [`Move.lock`](#movelock) 檔案由 Move CLI 產生，包含套件及其依賴項的固定建置版本。它用於確保不同建置之間使用一致的版本，並且依賴項的更改會顯現為此檔案的更改。
1. `sources` 目錄是必填的，包含組成套件的 Move 模組。此目錄中的模組將始終包含在編譯過程中。
1. `doc_templates` 目錄可以包含在產生套件文件時將使用的文件模板。
1. `examples` 目錄可以存放僅用於開發和/或教學的額外程式碼，這在 `test` 或 `dev` 模式之外編譯時不會被包含。
1. `tests` 目錄可以包含僅在 `test` 模式下編譯或執行 [Move 單元測試](./unit-testing) 時包含的 Move 模組。

### Move.toml

Move 套件清單定義在 `Move.toml` 檔案中，具有以下語法。選填欄位以 `*` 標記，`+` 表示一個或多個元素：

```toml
[package]
name = <string>
edition* = <string>      # 例如 "2024.alpha" 以使用 Move 2024 版本，
                         # 目前為 alpha 版。若未指定，將預設為最新的穩定版本。
license* = <string>              # 例如 "MIT", "GPL", "Apache 2.0"
authors* = [<string>,+]  # 例如 ["Joe Smith (joesmith@noemail.com)", "John Snow (johnsnow@noemail.com)"]

# 外部工具可能會向此部分加入額外欄位。例如，在 Sui 上會增加以下部分：
published-at* = "<hex-address>" # 套件發佈所在的地址。應在首次發佈後設定。

[dependencies] # (選填部分) 指向依賴項的路徑
# 以以下格式宣告一個或多行依賴項

# ##### 區域依賴 (Local Dependencies) #####
# 對於區域依賴，使用 `local = path`。路徑相對於套件根目錄
# Local = { local = "../path/to" }
# 要解決版本衝突並強制使用特定版本的依賴項覆蓋，可以使用 `override = true`
# Override = { local = "../conflicting/version", override = true }
# 要在依賴項中實例化地址值，請使用 `addr_subst`
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

# ##### Git 依賴 (Git Dependencies) #####
# 對於遠端匯入，使用 `{ git = "...", subdir = "...", rev = "..." }`。
# 必須提供版本號 (Revision)，可以是分支、標籤或提交雜湊 (commit hash)。
# 如果未指定 `subdir`，則使用儲存庫的根目錄。
# MyRemotePackage = { git = "https://some.remote/host.git", subdir = "remote/path", rev = "main" }
<string> = {
    git = <URL ending in .git>,
    subdir=<git 儲存庫內包含 Move.toml 的目錄路徑>,
    rev=<git 提交雜湊>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[addresses]  # (選填部分) 宣告此套件中的具名地址
# 以以下格式宣告一個或多行具名地址
# 與套件名稱匹配的地址必須設定為 `"0x0"`，否則將無法發佈。
<addr_name> = "_" | "<hex_address>" # 例如 std = "_" 或 my_addr = "0xC0FFEECAFE"

# 具名地址在 Move 中可作為 `@name` 存取。它們也會被匯出：
# 例如，`std = "0x1"` 是由標準庫匯出的。
# alice = "0xA11CE"

[dev-dependencies] # (選填部分) 與 [dependencies] 部分相同，但僅包含在 "dev" 和 "test" 模式中
# dev-dependencies 部分允許為 `--test` 和 `--dev` 模式覆蓋依賴項。
# 例如，你可以在此處引入僅限測試的依賴項。
# Local = { local = "../path/to/dev-build" }
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}
<string> = {
    git = <URL ending in .git>,
    subdir=<git 儲存庫內包含 Move.toml 的目錄路徑>,
    rev=<git 提交雜湊>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[dev-addresses] # (選填部分) 與 [addresses] 部分相同，但僅包含在 "dev" 和 "test" 模式中
# dev-addresses 部分允許為 `--test` 和 `--dev` 模式重寫具名地址。
<addr_name> = "<hex_address>" # 例如 alice = "0xB0B"
```

一個最小套件清單的範例：

```toml
[package]
name = "AName"
```

一個更標準的套件清單範例，它還包含了 Move 標準庫，並將來自 `LocalDep` 套件的具名地址 `std` 實例化為地址值 `0x1`：

```toml
[package]
name = "AName"
license = "Apache 2.0"

[addresses]
address_to_be_filled_in = "_"
specified_address = "0xB0B"

[dependencies]
# 區域依賴
LocalDep = { local = "projects/move-awesomeness", addr_subst = { "std" = "0x1" } }
# Git 依賴
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }

[dev-addresses] # 用於開發此模組時
address_to_be_filled_in = "0x101010101"
```

套件清單中的大多數部分都是不言自明的，但具名地址可能有點難以理解，因此我們在 [編譯期間的具名地址](#編譯期間的具名地址-named-addresses-during-compilation) 中進行更詳細的探討。

## 編譯期間的具名地址 (Named Addresses During Compilation)

回想一下 Move 具有 [具名地址](./primitive-types/address)，且具名地址不能在 Move 中宣告。相反地，它們是在套件層級宣告的：在 Move 套件的清單檔案 (`Move.toml`) 中，你宣告套件中的具名地址、實例化其他具名地址，並在 Move 套件系統內重新命名來自其他套件的具名地址。

讓我們逐一查看這些操作，以及它們是如何在套件清單中執行的：

### 宣告具名地址 (Declaring Named Addresses)

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

宣告 `named_addr` 為套件 `example_pkg` 中的具名地址，並且 _此地址可以是任何有效的地址值_。特別是，匯入套件可以將具名地址 `named_addr` 的值選定為它希望的任何地址。直觀上，你可以將這視為透過具名地址 `named_addr` 將 `example_pkg` 套件參數化，該套件隨後可以由匯入套件進行實例化。

`named_addr` 也可以宣告為：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "0xCAFE"
```

這表示具名地址 `named_addr` 精確地為 `0xCAFE` 且不能更改。這很有用，因此其他匯入套件可以使用此具名地址，而無需擔心分配給它的確切值。

透過這兩種不同的宣告方法，具名地址的資訊可以透過兩種方式在套件圖（package graph）中流動：

- 前者（「未分配的具名地址」）允許具名地址值從匯入點流向宣告點。
- 後者（「已分配的具名地址」）允許具名地址值從宣告點沿著套件圖向上流向使用點。

透過這兩種在整個套件圖中流動具名地址資訊的方法，理解圍繞作用域和重新命名的規則變得非常重要。

## 具名地址的作用域與重新命名 (Scope and Renaming of Named Addresses)

如果滿足以下條件，套件 `P` 中的具名地址 `N` 就在作用域內：

1. `P` 宣告了一個具名地址 `N`；或者
2. `P` 的某個傳遞依賴 (transitive dependency) 套件宣告了具名地址 `N`，且 `P` 與 `N` 的宣告套件之間的套件圖中存在一條路徑，且該路徑上沒有對 `N` 的重新命名。

此外，套件中的每個具名地址都會被匯出。因此，根據上述作用域規則，每個套件都可以看作是帶有一組具名地址，這些地址將在匯入該套件時帶入作用域。例如，如果你匯入 `example_pkg`，該匯入也會將 `named_addr` 具名地址帶入作用域。正因如此，如果 `P` 匯入了兩個套件 `P1` 和 `P2`，兩者都宣告了一個具名地址 `N`，那麼 `P` 中就會出現一個問題：當在 `P` 中參考 `N` 時，指的是哪一個「`N`」？是來自 `P1` 還是 `P2`？為了防止關於具名地址來源的歧義，我們強制要求套件中所有依賴項引入的作用域集合必須是不相交的（disjoint），並提供了一種在匯入帶入作用域的套件時 _重新命名具名地址_ 的方法。

在我們上面的 `P`、`P1` 和 `P2` 範例中，匯入時重新命名具名地址可以如下操作：

```toml
[package]
name = "P"
...
[dependencies]
P1 = { local = "some_path_to_P1", addr_subst = { "P1N" = "N" } }
P2 = { local = "some_path_to_P2"  }
```

透過這種重新命名，`N` 將參考來自 `P2` 的 `N`，而 `P1N` 將參考來自 `P1` 的 `N`：

```move
module N::A {
    public fun x(): address { @P1N }
}
```

重要的一點是，_重新命名不是局部的_：一旦具名地址 `N` 在套件 `P` 中被重新命名為 `N2`，所有匯入 `P` 的套件將看不到 `N` 而只能看到 `N2`，除非 `N` 從 `P` 之外重新引入。這就是為什麼本節開頭作用域規則中的第 (2) 條規定「`P` 與 `N` 的宣告套件之間的套件圖中存在一條路徑，且該路徑上沒有對 `N` 的重新命名。」

### 實例化具名地址 (Instantiating Named Addresses)

只要值始終相同，具名地址可以在整個套件圖中被多次實例化。如果同一個具名地址（無論是否重新命名）在整個套件圖中以不同的值被實例化，則會報錯。

只有在所有具名地址都解析為一個值時，Move 套件才能被編譯。如果套件希望公開一個未實例化的具名地址，這就產生了問題。這就是 `[dev-addresses]` 部分部分解決的問題。此部分可以為具名地址設定值，但不能引入任何具名地址。此外，只有根套件中的 `[dev-addresses]` 會包含在 `dev` 模式中。例如，具有以下清單的根套件在 `dev` 模式之外將無法編譯，因為 `named_addr` 將未被實例化：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "_"

[dev-addresses]
named_addr = "0xC0FFEE"
```

## 用法與產物 (Usage and Artifacts)

Move 套件系統帶有一個指令行選項作為 CLI 的一部分：
`sui move <command> <command_flags>`。除非提供了特定路徑，否則所有套件指令都將在目前包含的 Move 套件中執行。Move CLI 的完整指令和標記清單可以透過執行 `sui move --help` 找到。

### 產物 (Artifacts)

可以使用 CLI 指令編譯套件。這將建立一個 `build` 目錄，其中包含與建置模組相關的產物（包括位元組碼二進制檔案、來源對應 (source maps) 和文件）。`build` 目錄的一般佈局如下：

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

當套件建置時，會在 Move 套件的根目錄下產生 `Move.lock` 檔案。`Move.lock` 檔案包含有關你的套件及其建置設定的資訊，並作為 Move 編譯器與其他工具（如特定鏈的指令行介面和第三方程式套件管理器）之間的通訊層。

與 `Move.toml` 檔案一樣，`Move.lock` 檔案是一個基於文本的 TOML 檔案。然而，與套件清單不同的是，`Move.lock` 檔案並不打算讓你直接編輯。工具鏈上的行程（如 Move 編譯器）會存取並編輯該檔案，以讀取和向其中加入相關資訊。你也不能將該檔案從根目錄移動，因為它需要與套件中的 `Move.toml` 清單處於同一層級。

如果你為套件使用版本控制，建議的做法是簽入與你所需的建置或發佈套件相對應的 `Move.lock` 檔案。這可以確保你的套件的每次建置都是原始建置的精確副本，並且建置的更改將顯示為 `Move.lock` 檔案的更改。

`Move.lock` 檔案是一個 TOML 檔案，目前包含以下欄位。

**注意**：未來或第三方套件管理器也可能向鎖定檔案加入其他欄位。

### `[move]` 部分 (The `[move]` Section)

此部分包含鎖定檔案中所需的核心資訊：

- 鎖定檔案的版本（用於向後相容性檢查，以及將來鎖定檔案更改的版本控制）。
- 用於產生此鎖定檔案的 `Move.toml` 檔案的雜湊。
- 所有依賴項的 `Move.lock` 檔案的雜湊。如果不存在依賴項，這將是一個空字串。
- 依賴項列表。

```toml
[move]
version = <string> # 鎖定檔案版本，用於向後相容性檢查。
manifest_digest = <hash> # 用於產生此鎖定檔案的 Move.toml 檔案的 Sha3-256 雜湊。
deps_digest = <hash> # 所有依賴項的 Move.lock 檔案的 Sha3-256 雜湊。如果不存在依賴項，這將是一個空字串。
dependencies = { (name = <string>)* } # 依賴項列表。如果沒有依賴項則不存在。
```

### `[move.package]` 部分 (The `[move.package]` Sections)

在 Move 編譯器解析了套件的每個依賴項後，它會將依賴項的位置寫入 `Move.lock` 檔案。如果某個依賴項解析失敗，編譯器將不會寫入 `Move.lock` 檔案且建置失敗。如果所有依賴項都解析成功，`Move.lock` 檔案將包含套件所有傳遞依賴項的位置（區域和遠端）。這些將以以下格式儲存在 `Move.lock` 檔案中：

```toml
# ...

[[move.package]]
name = "A"
source = { git = "https://github.com/b/c.git", subdir = "e/f", rev = "a1b2c3" }

[[move.package]]
name = "B"
source = { local = "../local-dep" }
```

### `[move.toolchain-version]` 部分 (The `[move.toolchain-version]` Section)

如上所述，外部工具可能會向鎖定檔案加入額外欄位。例如，Sui 套件管理器向鎖定檔案加入工具鏈版本資訊，然後可用於鏈上源驗證：

```toml
# ...

[move.toolchain-version]
compiler-version = <string> # 用於建置套件的 Move 編譯器版本，例如 "1.21.0"
edition = <string> # 用於建置套件的 Move 語言版本，例如 "2024.alpha"
flavor = <string> # 用於建置套件的 Move 編譯器變體 (flavor)，例如 "sui"
```
