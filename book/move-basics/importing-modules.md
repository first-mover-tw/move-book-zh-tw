---
description: 如何在 Move 中使用 `use` 關鍵字匯入模組 (module)：單一匯入、群組匯入、成員匯入，以及解決命名衝突。
---

# 匯入模組 (Importing Modules) {#importing-modules}

Move 藉由允許模組匯入，達成高度模組化與程式碼重用。同一個 package 內的模組可以互相匯入，而新的 package 也可以依賴既有的 package 並使用其模組。本節將涵蓋匯入模組的基礎知識，以及如何在你自己的程式碼中使用它們。

## 匯入模組 (Importing a Module) {#importing-a-module}

同一個 package 中定義的模組可以互相匯入。`use` 關鍵字後面接模組路徑，模組路徑由 package 地址（或別名）與模組名稱以 `::` 分隔組成。

```move title="File: sources/module_one.move" file=packages/samples/sources/move-basics/importing-modules.move anchor=module_one

```

同一個 package 中定義的另一個模組，可以用 `use` 關鍵字匯入第一個模組。

```move title="File: sources/module_two.move" file=packages/samples/sources/move-basics/importing-modules-two.move anchor=module_two

```

> 注意：任何你想從另一個模組匯入的項目（struct、函式、常數等），都必須標記為 `public`（或 `public(package)` — 參見[可見性修飾詞 (visibility modifiers)](./visibility)），才能在其定義模組之外被存取。舉例來說，`module_one` 中的 `Character` struct 與 `new` 函式都被標記為 public，因此才能在 `module_two` 中使用。

## 匯入成員 (Importing Members) {#importing-members}

你也可以從模組中匯入特定的成員。當你只需要模組中的單一函式或單一型別時，這會很有用。語法與匯入模組相同，只是在模組路徑後面加上成員名稱。

```move file=packages/samples/sources/move-basics/importing-modules-members.move anchor=members

```

## 分組匯入 (Grouping Imports) {#grouping-imports}

匯入可以用大括號 `{}` 分組成單一 `use` 陳述式。當你需要從同一個模組或 package 匯入多個成員時，這能讓程式碼更簡潔、更有條理。

```move file=packages/samples/sources/move-basics/importing-modules-grouped.move anchor=grouped

```

在 Move 中匯入函式名稱較不常見，因為函式名稱可能重複而造成混淆。建議的做法是匯入整個模組，並用模組路徑來存取函式。型別的名稱是唯一的，應該個別匯入。

若要在一次分組匯入中同時匯入模組本身與其部分成員，可以使用代表該模組的 `Self` 關鍵字：

```move file=packages/samples/sources/move-basics/importing-modules-self.move anchor=self

```

## 解決名稱衝突 (Resolving Name Conflicts) {#resolving-name-conflicts}

當從不同模組匯入多個成員時，可能會發生名稱衝突。舉例來說，如果你匯入了兩個模組，且它們都有相同名稱的函式，你就需要用模組路徑來存取該函式。不同 package 中也可能存在同名的模組。為了解決衝突並避免模稜兩可，Move 提供了 `as` 關鍵字來重新命名匯入的成員。

```move file=packages/samples/sources/move-basics/importing-modules-conflict-resolution.move anchor=conflict

```

## 新增外部依賴 (Adding an External Dependency) {#adding-an-external-dependency}

Move package 可以依賴其他的 package；這些依賴項會列在稱為 `Move.toml` 的 [Package 清單檔 (Package Manifest)](./../concepts/manifest) 中。

Package 依賴項會如下所示地定義在 [Package 清單檔 (Package Manifest)](./../concepts/manifest) 中：

```ini title="Move.toml"
[dependencies]
Example = { git = "https://github.com/Example/example.git", subdir = "path/to/package", rev = "v1.2.3" }
Local = { local = "../my_other_package" }
```

`dependencies` 區段中，每個依賴的 package 都會有一筆項目。項目的 key 是 package 的名稱（範例中的 `Example` 或 `Local`），值則是一個 git 匯入表或本地路徑。git 匯入包含 package 的 URL、package 所在的子目錄，以及 package 的版本。本地路徑則是指向 package 目錄的相對路徑。

編譯器會在建置 package 時自動抓取（並在之後重新抓取）所列出的依賴項，而它們的所有依賴項也會一併提供給你的 package 使用。

> 從 sui CLI 1.45 版開始，若 `Move.toml` 中沒有列出系統 package，它們會自動被納入為所有 package 的依賴項。因此，`MoveStdlib`、`Sui`、`System`、`Bridge` 與 `Deepbook` 都無需明確匯入即可使用。

## 從另一個 Package 匯入模組 (Importing a Module from Another Package) {#importing-a-module-from-another-package}

通常，package 會在 `[addresses]` 區段中定義自己的地址。你可以使用別名來取代完整地址。舉例來說，你可以用 `sui::coin` 取代 `0x2::coin` 來參考 Sui 的 `coin` 模組。`sui` 這個別名是在 Sui Framework package 的清單檔中定義的。同樣地，`std` 別名是在標準函式庫 package 中定義的，可以用它取代 `0x1` 來存取標準函式庫模組。

若要從另一個 package 匯入模組，使用 `use` 關鍵字接模組路徑。模組路徑由 package 地址（或別名）與模組名稱組成，以 `::` 分隔。

```move file=packages/samples/sources/move-basics/importing-modules-external.move anchor=external

```

> 注意：模組地址名稱來自清單檔（`Move.toml`）的 `[addresses]` 區段，而非 `[dependencies]` 區段中使用的名稱。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[用法與別名 (Uses and Aliases)](./../../reference/uses)。
