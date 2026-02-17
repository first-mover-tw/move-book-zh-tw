---

description: "How to import modules in Move using the use keyword: single imports, grouped imports, member imports, and resolving naming conflicts."
---

# 匯入模組 (Importing Modules)

<!--
    TODO: create a better example for:
        1. Importing a module in general
        2. Importing a member
        3. Importing multiple members
        4. Grouping imports
        5. Self keyword for groups
-->

<!--

Goals:
    - Show the import syntax
    - Local dependencies
    - External dependencies
    - Importing modules from other packages

 -->

Move 透過允許模組匯入來實現高度的模組化和程式碼重用。同一個套件中的模組可以互相匯入，新的套件也可以依賴已有的套件並使用其中的模組。本節將介紹匯入模組的基礎知識，以及如何在您自己的程式碼中使用它們。

## 匯入模組

在同一個套件中定義的模組可以互相匯入。`use` 關鍵字後接模組路徑，路徑由套件地址（或別名）和模組名稱組成，中間以 `::` 分隔。

```move title="檔案：sources/module_one.move" file=packages/samples/sources/move-basics/importing-modules.move anchor=module_one

```

在同一個套件中定義的另一個模組可以使用 `use` 關鍵字匯入第一個模組。

```move title="檔案：sources/module_two.move" file=packages/samples/sources/move-basics/importing-modules-two.move anchor=module_two

```

> 注意：任何您想從另一個模組匯入的項目（結構、函式、常數等）都必須標記 `public`（或 `public(package)` — 參見 [可見性修飾符](./visibility)）關鍵字，使其在其定義模組之外也可供存取。例如，`module_one` 中的 `Character` 結構和 `new` 函式都標記為 public，因此它們可以在 `module_two` 中使用。

## 匯入成員

您也可以從模組中匯入特定的成員。當您只需要模組中的單個函式或單個類型時，這非常有用。語法與匯入模組相同，但在模組路徑之後添加成員名稱。

```move file=packages/samples/sources/move-basics/importing-modules-members.move anchor=members

```

## 分組匯入

可以使用大括號 `{}` 將多個匯入項組合到單個 `use` 語句中。當從同一個模組或套件匯入多個成員時，這可以讓程式碼更簡潔、更有條理。

```move file=packages/samples/sources/move-basics/importing-modules-grouped.move anchor=grouped

```

在 Move 中，匯入函式名稱較不常見，因為函式名稱可能會重疊並導致混淆。建議的做法是匯入整個模組，並使用模組路徑來存取函式。類型具有唯一的名稱，應單獨匯入。

要在分組匯入中同時匯入成員和模組本身，可以使用 `Self` 關鍵字。`Self` 關鍵字指的是模組本身，可用於匯入模組及其成員。

```move file=packages/samples/sources/move-basics/importing-modules-self.move anchor=self

```

## 解決名稱衝突

當從不同模組匯入多個成員時，可能會發生名稱衝突。例如，如果您匯入的兩個模組都有一個名稱相同的函式，則需要使用模組路徑來存取該函式。在不同的套件中也可能存在同名的模組。為了縮小衝突並避免歧義，Move 提供了 `as` 關鍵字來為匯入的成員重新命名。

```move file=packages/samples/sources/move-basics/importing-modules-conflict-resolution.move anchor=conflict

```

## 添加外部依賴項

Move 套件可以依賴其他套件；依賴項列在名為 `Move.toml` 的 [套件清單 (Package Manifest)](./../concepts/manifest) 檔案中。

套件依賴項在 [套件清單](./../concepts/manifest) 中定義如下：

```ini title="Move.toml"
[dependencies]
Example = { git = "https://github.com/Example/example.git", subdir = "path/to/package", rev = "v1.2.3" }
Local = { local = "../my_other_package" }
```

`dependencies` 部分包含每個套件依賴項的條目。條目的鍵是套件的名稱（範例中的 `Example` 或 `Local`），值可以是 git 匯入表或本地路徑。git 匯入包含套件的 URL、套件所在的子目錄以及套件修訂版本。本地路徑是到套件目錄的相對路徑。

如果您添加了一個依賴項，其所有的依賴項也會對您的套件可用。

如果在 `Move.toml` 檔案中添加了依賴項，編譯器在構建套件時會自動獲取（以及後續重新獲取）這些依賴項。

> 從 1.45 版本的 Sui CLI 開始，如果 `Move.toml` 中不存在系統套件，系統套件會被自動作為依賴項包含在所有套件中。因此，無需明確匯入，`MoveStdLib`、`Sui`、`System`、`Bridge` 和 `Deepbook` 即可使用。

## 從另一個套件匯入模組

通常，套件在 `[addresses]` 部分定義其地址。您可以使用別名而不是完整地址。例如，您可以使用 `sui::coin` 代替 `0x2::coin` 來引用 Sui 的 `coin` 模組。`sui` 別名定義在 Sui 框架套件的清單中。類似地，`std` 別名定義在標準庫套件中，可用於代替 `0x1` 來存取標準庫模組。

要從另一個套件匯入模組，請使用 `use` 關鍵字後接模組路徑。模組路徑由套件地址（或別名）和模組名稱組成，以 `::` 分隔。

```move file=packages/samples/sources/move-basics/importing-modules-external.move anchor=external

```

> 注意：模組地址名稱來自清單檔案 (`Move.toml`) 的 `[addresses]` 部分，而不是 `[dependencies]` 部分中使用的名稱。
