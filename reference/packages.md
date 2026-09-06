---
title: 套件 (Packages) | 參考手冊
description: Move 套件參考 (Move packages reference)：套件配置 (package layout)、Move.toml 套件清單 (manifest)、依賴項 (dependencies)、具名地址 (named addresses)，以及套件編譯 (package compilation)。
keywords:
  - Move
  - Sui
  - Move reference
  - packages
  - reference
  - package
questions:
  - How does Packages work in Move?
  - What is the syntax for Packages in Move?
  - What is Package Layout and Manifest Syntax in Move?
  - What is Named Addresses During Compilation in Move?
answer: 'Move packages reference: package layout, Move.toml manifest, dependencies, named addresses, and package compilation.'
goal:
  description: 'Reader understands move packages reference: package layout, Move.toml manifest, dependencies, named addresses, and package compilation'
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

# 套件 (Packages) {#packages}

套件讓 Move 程式設計師能更容易地重複使用原始碼，並在各個專案之間分享。Move
套件系統讓程式設計師能輕鬆地：

- 定義包含 Move 原始碼的套件；
- 透過[具名地址](./primitive-types/address)將套件參數化；
- 在其他 Move 原始碼中匯入及使用套件，並具現化具名地址；
- 建置套件並從套件產生相關的編譯成品；以及
- 使用編譯後 Move 成品周邊的通用介面。

## 套件版面配置與套件清單語法 (Package Layout and Manifest Syntax) {#package-layout-and-manifest-syntax}

Move 套件的原始碼目錄包含一個 `Move.toml` 套件清單檔案、一個產生的
`Move.lock` 檔案，以及一組子目錄：

```plaintext
a_move_package
├── Move.toml      （必要）
├── Move.lock      （產生）
├── sources        （必要）
├── doc_templates  （選用）
├── examples       （選用，測試與開發模式）
└── tests          （選用，測試模式）
```

標示為「必要」的目錄與檔案必須存在，該目錄才會被視為 Move
套件並建置。選用目錄可以存在；若存在，則會依據用於建置套件的模式納入
編譯程序。例如，以「開發」或「測試」模式建置時，`tests` 與 `examples`
目錄也會一併納入。

以下逐一說明：

1. [`Move.toml`](#movetoml) 檔案是套件清單，且為將目錄視為
   Move 套件的必要檔案。此檔案包含套件的中繼資料，例如名稱、
   依賴項等。
1. [`Move.lock`](#movelock) 檔案由 Move CLI 產生，包含套件及其依賴項的固定
   建置版本。它用於確保不同建置作業使用一致的版本，並使依賴項的變更
   顯示為此檔案的變更。
1. `sources` 目錄為必要目錄，包含構成套件的 Move 模組。
   此目錄中的模組一律會納入編譯程序。
1. `doc_templates` 目錄可包含文件範本，會在產生套件文件時使用。
1. `examples` 目錄可存放僅供開發及／或教學使用的額外程式碼；
   在 `test` 或 `dev` 模式之外編譯時，不會納入這些程式碼。
1. `tests` 目錄可包含僅在 `test` 模式編譯時，或執行
   [Move 單元測試](./unit-testing)時納入的 Move 模組。

### Move.toml 套件清單檔案 (Move.toml) {#movetoml}

Move 套件清單定義於 `Move.toml` 檔案中，語法如下。
選用欄位以 `*` 標示，`+` 表示一個或多個元素：

```toml
[package]
name = <string>
edition* = <string>      # 例如，使用 Move 2024 版本的 "2024.alpha"，
                         # 目前為 alpha。若未指定，預設為最新的穩定版本。
license* = <string>              # 例如，"MIT"、"GPL"、"Apache 2.0"
authors* = [<string>,+]  # 例如，["Joe Smith (joesmith@noemail.com)", "John Snow (johnsnow@noemail.com)"]

# 外部工具可在此區段加入額外欄位。例如，在 Sui 上會加入以下區段：
published-at* = "<hex-address>" # 套件發布所在的地址。應在首次發布後設定。

[dependencies] # （選用區段）依賴項的路徑
# 以以下格式宣告依賴項的一行或多行

# ##### 本機依賴項 #####
# 本機依賴項使用 `local = path`。路徑相對於套件根目錄
# Local = { local = "../path/to" }
# 若要解決版本衝突並強制指定依賴項覆寫的特定版本，
# 可使用 `override = true`
# Override = { local = "../conflicting/version", override = true }
# 若要在依賴項中具現化地址值，請使用 `addr_subst`
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

# ##### Git 依賴項 #####
# 遠端匯入使用 `{ git = "...", subdir = "...", rev = "..." }`。
# 必須提供修訂版本；可以是分支、標籤或提交雜湊。
# 若未指定 `subdir`，則使用儲存庫根目錄。
# MyRemotePackage = { git = "https://some.remote/host.git", subdir = "remote/path", rev = "main" }
<string> = {
    git = <URL ending in .git>,
    subdir=<git 儲存庫中包含 Move.toml 的目錄路徑>,
    rev=<git commit hash>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[addresses]  # （選用區段）在此套件中宣告具名地址
# 以以下格式宣告具名地址的一行或多行
# 與套件名稱相符的地址必須設定為 `"0x0"`，否則無法發布。
<addr_name> = "_" | "<hex_address>" # 例如，std = "_" 或 my_addr = "0xC0FFEECAFE"

# 具名地址可在 Move 中以 `@name` 存取，也會被匯出：
# 例如，標準函式庫匯出 `std = "0x1"`。
# alice = "0xA11CE"

[dev-dependencies] # （選用區段）與 [dependencies] 區段相同，但僅納入「開發」與「測試」模式
# dev-dependencies 區段可為 `--test` 與
# `--dev` 模式覆寫依賴項。例如，你可以在此引入僅供測試的依賴項。
# Local = { local = "../path/to/dev-build" }
<string> = {
    local = <string>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}
<string> = {
    git = <URL ending in .git>,
    subdir=<git 儲存庫中包含 Move.toml 的目錄路徑>,
    rev=<git commit hash>,
    override* = <bool>,
    addr_subst* = { (<string> = (<string> | "<hex_address>"))+ }
}

[dev-addresses] # （選用區段）與 [addresses] 區段相同，但僅納入「開發」與「測試」模式
# dev-addresses 區段可為 `--test`
# 與 `--dev` 模式覆寫具名地址。
<addr_name> = "<hex_address>" # 例如，alice = "0xB0B"
```

最簡套件清單範例：

```toml
[package]
name = "AName"
```

以下是較標準的套件清單範例，其中也包含 Move 標準函式庫，並以地址值 `0x1`
具現化來自 `LocalDep` 套件的具名地址 `std`：

```toml
[package]
name = "AName"
license = "Apache 2.0"

[addresses]
address_to_be_filled_in = "_"
specified_address = "0xB0B"

[dependencies]
# 本機依賴項
LocalDep = { local = "projects/move-awesomeness", addr_subst = { "std" = "0x1" } }
# Git 依賴項
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }

[dev-addresses] # 開發此模組時使用
address_to_be_filled_in = "0x101010101"
```

套件清單中的大多數區段都不難理解，但具名地址可能較難理解，因此我們會在
[編譯期間的具名地址](#named-addresses-during-compilation)中進一步檢視。

## 編譯期間的具名地址 (Named Addresses During Compilation) {#named-addresses-during-compilation}

回想一下，Move 具有[具名地址](./primitive-types/address)，而且具名地址無法在 Move 中宣告。相反地，它們是在套件層級宣告：在 Move 套件的套件清單檔案（`Move.toml`）中，你可以在套件內宣告具名地址、具現化其他具名地址，以及在 Move 套件系統中重新命名來自其他套件的具名地址。

讓我們逐一說明這些動作，以及如何在套件的套件清單中執行：

### 宣告具名地址 (Declaring Named Addresses) {#declaring-named-addresses}

假設我們在 `example_pkg/sources/A.move` 中有以下 Move 模組：

```move
module named_addr::a {
    public fun x(): address { @named_addr }
}
```

我們可以在 `example_pkg/Move.toml` 中透過兩種不同方式宣告具名地址 `named_addr`。第一種：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "_"
```

這會將 `named_addr` 宣告為套件 `example_pkg` 中的具名地址，且*此地址可以是任何有效的地址值*。特別是，匯入套件可以將具名地址 `named_addr` 的值選擇為它所需的任何地址。直觀而言，你可以將這視為以具名地址 `named_addr` 對套件 `example_pkg` 進行參數化，之後匯入套件便可將此套件具現化。

`named_addr` 也可以宣告為：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "0xCAFE"
```

這表示具名地址 `named_addr` 確實為 `0xCAFE`，且無法變更。這很有用，因為其他匯入套件可以使用此具名地址，而無須擔心指派給它的確切值。

透過這兩種不同的宣告方法，具名地址的資訊可在套件圖中以兩種方式流動：

- 前者（「未指派的具名地址」）允許具名地址值從匯入位置流向宣告位置。
- 後者（「已指派的具名地址」）允許具名地址值從宣告位置沿著套件圖向上流向使用位置。

透過這兩種讓具名地址資訊在整個套件圖中流動的方法，了解作用域與重新命名的相關規則便變得很重要。

## 命名地址的範圍與重新命名 (Scope and Renaming of Named Addresses) {#scope-and-renaming-of-named-addresses}

套件 `P` 中的命名地址 `N` 若符合下列條件，即在範圍內：

1. `P` 宣告了命名地址 `N`；或
2. `P` 的其中一個遞移依賴項中的套件宣告了命名地址 `N`，且在套件圖中，`P` 與宣告 `N` 的套件之間存在一條依賴項路徑，該路徑上沒有對 `N` 進行重新命名。

此外，套件中的每個命名地址都會匯出。因此，基於此項以及上述範圍規則，每個套件都可視為附帶一組命名地址；匯入該套件時，這些命名地址也會進入範圍。例如，若你匯入 `example_pkg`，該匯入也會將名為 `named_addr` 的命名地址帶入範圍。正因如此，若 `P` 匯入兩個套件 `P1` 和 `P2`，而兩者皆宣告命名地址 `N`，則 `P` 中會產生問題：在 `P` 中參考 `N` 時，所指的是哪個「`N`」？是來自 `P1` 還是 `P2`？為避免命名地址來源套件的不明確性，我們強制套件中所有依賴項帶入的範圍集合必須互不重疊，並提供在匯入帶入這些命名地址的套件時，對其進行「_重新命名命名地址_」的方式。

在上述 `P`、`P1` 與 `P2` 的範例中，匯入時可於我們的 `P` 內如下重新命名命名地址：

```toml
[package]
name = "P"
...
[dependencies]
P1 = { local = "some_path_to_P1", addr_subst = { "P1N" = "N" } }
P2 = { local = "some_path_to_P2"  }
```

經過此重新命名後，`N` 會參考來自 `P2` 的 `N`，而 `P1N` 則會參考來自 `P1` 的 `N`：

```move
module N::A {
    public fun x(): address { @P1N }
}
```

請務必注意，_重新命名並非區域性的_：一旦命名地址 `N` 在套件 `P` 中被重新命名為 `N2`，所有匯入 `P` 的套件都不會看見 `N`，而只會看見 `N2`，除非從 `P` 外部重新引入 `N`。這也是本節開頭的範圍規則第 (2) 條指定「套件圖中 `P` 與宣告 `N` 的套件之間，沒有重新命名 `N` 的依賴項路徑」的原因。

### 具現化命名地址 (Instantiating Named Addresses) {#instantiating-named-addresses}

只要命名地址在整個套件圖中始終具有相同值，即可多次具現化。若相同的命名地址（無論是否經過重新命名）在套件圖中以不同值具現化，則會發生錯誤。

只有在所有命名地址皆可解析為值時，Move 套件才能編譯。若套件希望公開未具現化的命名地址，便會產生問題。`[dev-addresses]` 區段可部分解決此問題。此區段可以為命名地址設定值，但無法引入任何命名地址。此外，只有根套件中的 `[dev-addresses]` 會包含在 `dev` 模式中。例如，具有下列套件清單的根套件無法在 `dev` 模式外編譯，因為 `named_addr` 尚未具現化：

```toml
[package]
name = "example_pkg"
...
[addresses]
named_addr = "_"

[dev-addresses]
named_addr = "0xC0FFEE"
```

## 使用方式與成品 (Usage and Artifacts) {#usage-and-artifacts}

Move 套件系統提供作為 CLI 一部分的命令列選項：
`sui move <command> <command_flags>`。除非提供特定路徑，否則所有套件命令
都會在目前所在的 Move 套件中執行。可透過執行 `sui move --help`
取得 Move CLI 的完整命令與旗標清單。

### 成品 (Artifacts) {#artifacts}

套件可使用 CLI 命令編譯。這會建立一個 `build` 目錄，其中包含
與建置相關的成品（包括位元組碼二進位檔、原始碼對應與文件）。`build`
目錄的一般配置如下：

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

## Move.lock 鎖定檔 (Move.lock) {#movelock}

當建置 Move 套件時，會在 Move 套件的根目錄產生 `Move.lock` 檔案。`Move.lock` 檔案包含套件及其建置設定的資訊，並作為 Move 編譯器與其他工具之間的通訊層，例如鏈特定的命令列介面及第三方套件管理員。

與 `Move.toml` 檔案相同，`Move.lock` 檔案也是以文字為基礎的 TOML 檔案。不過，與套件清單不同的是，`Move.lock` 檔案並非設計讓你直接編輯。工具鏈中的程序（例如 Move 編譯器）會存取並編輯此檔案，以讀取及附加相關資訊。你也不得將此檔案移離根目錄，因為它必須與套件中的 `Move.toml` 套件清單位於同一層級。

如果你對套件使用版本控制，建議將對應於你想要建置或發布之套件的 `Move.lock` 檔案納入版本控制。如此可確保套件的每次建置都是原始版本的完全複本，並且建置變更會明確顯示為 `Move.lock` 檔案的變更。

`Move.lock` 檔案是 TOML 檔案，目前包含下列欄位。

**注意**：未來可能會在鎖定檔中新增其他欄位，第三方套件管理員也可能新增欄位。

### `[move]` 區段 (The `[move]` Section) {#the-move-section}

此區段包含鎖定檔所需的核心資訊：

- 鎖定檔版本（用於檢查回溯相容性，以及未來為鎖定檔變更進行版本管理）。
- 用於產生此鎖定檔的 `Move.toml` 檔案雜湊值。
- 所有依賴項之 `Move.lock` 檔案的雜湊值。若不存在依賴項，此值會是空字串。
- 依賴項清單。

```toml
[move]
version = <string> # 鎖定檔版本，用於檢查回溯相容性。
manifest_digest = <hash> # 用於產生此鎖定檔之 Move.toml 檔案的 Sha3-256 雜湊值。
deps_digest = <hash> # 所有依賴項之 Move.lock 檔案的 Sha3-256 雜湊值。若不存在依賴項，此值會是空字串。
dependencies = { (name = <string>)* } # 依賴項清單。若沒有依賴項則不會存在。
```

### `[move.package]` 區段 (The `[move.package]` Sections) {#the-movepackage-sections}

Move 編譯器解析套件的每個依賴項後，會將依賴項的位置寫入 `Move.lock` 檔案。若某個依賴項無法解析，編譯器不會寫入 `Move.lock` 檔案，且建置會失敗。若所有依賴項皆成功解析，`Move.lock` 檔案會包含套件所有傳遞性依賴項的位置（本機與遠端）。這些資訊會以下列格式儲存在 `Move.lock` 檔案中：

```toml
# ...

[[move.package]]
name = "A"
source = { git = "https://github.com/b/c.git", subdir = "e/f", rev = "a1b2c3" }

[[move.package]]
name = "B"
source = { local = "../local-dep" }
```

### `[move.toolchain-version]` 區段 (The `[move.toolchain-version]` Section) {#the-movetoolchain-version-section}

如上所述，外部工具可能會在鎖定檔中新增額外欄位。例如，Sui 套件管理員會將工具鏈版本資訊加入鎖定檔，之後可用於鏈上原始碼驗證：

```toml
# ...

[move.toolchain-version]
compiler-version = <string> # 用於建置套件的 Move 編譯器版本，例如 "1.21.0"
edition = <string> # 用於建置套件的 Move 語言版本，例如 "2024.alpha"
flavor = <string> # 用於建置套件的 Move 編譯器風格，例如 "sui"
```
