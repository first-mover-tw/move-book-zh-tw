---
description: 如何使用 `use` 關鍵字在 Move 中匯入模組：單一匯入、群組匯入、成員匯入，以及解決命名衝突。
title: 匯入模組 (Modules)
keywords:
  - Move
  - Sui
  - Move tutorial
  - importing
  - modules
questions:
  - What is Importing Modules in Move?
  - How do I use Importing Modules in Move?
  - What is Importing a Module in Move?
  - What is Importing Members in Move?
answer: 'How to import modules in Move using the use keyword: single imports, grouped imports, member imports, and resolving naming conflicts.'
goal:
  description: 'Reader understands import modules in Move using the use keyword: single imports, grouped imports, member imports, and resolving naming conflicts'
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

# 匯入模組 (Importing Modules) {#importing-modules}

Move 透過允許匯入模組，實現高度模組化與原始碼重用。同一個套件內的模組可以彼此匯入，而新的套件也可以依賴既有套件並使用其中的模組。本節將介紹匯入模組的基礎知識，以及如何在你自己的原始碼中使用它們。

## 匯入模組 (Importing a Module) {#importing-a-module}

在同一個套件中定義的模組可以彼此匯入。`use` 關鍵字後方接著模組路徑，該路徑由套件地址（或別名）與模組名稱組成，兩者以 `::` 分隔。

```move title="File: sources/module_one.move" file=packages/samples/sources/move-basics/importing-modules.move anchor=module_one

```

同一套件中定義的另一個模組可以使用 `use` 關鍵字匯入第一個模組。

```move title="File: sources/module_two.move" file=packages/samples/sources/move-basics/importing-modules-two.move anchor=module_two

```

> 注意：任何你想從另一個模組匯入的項目（結構、函式、常數等），都必須以 `public`（或 `public(package)`，請參閱[可見性修飾詞](./visibility)）關鍵字標記，才能在其定義模組外部存取。例如，`module_one` 中的 `Character` 結構與 `new` 函式皆已標記為公開，因此可在 `module_two` 中使用。

## 匯入成員 (Importing Members) {#importing-members}

你也可以從模組匯入特定成員。當你只需要模組中的單一函式或單一型別時，這會很有用。其語法與匯入模組相同，但需在模組路徑後方加上成員名稱。

```move file=packages/samples/sources/move-basics/importing-modules-members.move anchor=members

```

## 將匯入分組 (Grouping Imports) {#grouping-imports}

你可以使用大括號 `{}`，將匯入項目分組至單一 `use` 陳述式中。從同一個模組或套件匯入多個成員時，這能讓原始碼更整潔且更有條理。

```move file=packages/samples/sources/move-basics/importing-modules-grouped.move anchor=grouped

```

在 Move 中，匯入函式名稱較不常見，因為函式名稱可能重複而造成混淆。建議的做法是匯入整個模組，並使用模組路徑存取函式。型別具有唯一名稱，應個別匯入。

若要在一次群組匯入中同時匯入模組本身與其部分成員，請使用代表該模組的 `Self` 關鍵字：

```move file=packages/samples/sources/move-basics/importing-modules-self.move anchor=self

```

## 解決名稱衝突 (Resolving Name Conflicts) {#resolving-name-conflicts}

從不同模組匯入多個成員時，可能會發生名稱衝突。例如，若你匯入兩個都具有相同名稱函式的模組，便需要使用模組路徑存取該函式。不同套件中也可能存在相同名稱的模組。為解決衝突並避免歧義，Move 提供 `as` 關鍵字來重新命名匯入的成員。

```move file=packages/samples/sources/move-basics/importing-modules-conflict-resolution.move anchor=conflict

```

## 新增外部依賴項 (Adding an External Dependency) {#adding-an-external-dependency}

Move 套件可以依賴其他套件；依賴項會列於名為 `Move.toml` 的[套件清單](./../concepts/manifest)文件中。

套件依賴項在[套件清單](./../concepts/manifest)中的定義如下：

```ini title="Move.toml"
[dependencies]
Example = { git = "https://github.com/Example/example.git", subdir = "path/to/package", rev = "v1.2.3" }
Local = { local = "../my_other_package" }
```

`dependencies` 區段包含每個套件依賴項的一個項目。項目的鍵是套件名稱（範例中的 `Example` 或 `Local`），而值則是 git 匯入表格或區域路徑。git 匯入包含套件 URL、套件所在的子目錄，以及套件修訂版本。區域路徑則是套件目錄的相對路徑。

編譯器會在建置套件時自動擷取（並在後續重新擷取）列出的依賴項，而其所有依賴項也會提供給你的套件使用。

> 自 sui CLI 1.45 版起，若 `Move.toml` 中未包含系統套件，系統套件便會自動納入為所有套件的依賴項。因此，無須明確匯入即可使用 `MoveStdlib`、`Sui`、`System`、`Bridge` 與 `Deepbook`。

## 從另一個套件匯入模組 (Importing a Module from Another Package) {#importing-a-module-from-another-package}

一般而言，套件會在 `[addresses]` 區段中定義其地址。你可以使用別名來取代完整地址。例如，與其使用 `0x2::coin` 參考 Sui 的 `coin` 模組，你可以使用 `sui::coin`。`sui` 別名定義於 Sui Framework 套件的套件清單中。同樣地，`std` 別名定義於 Standard Library 套件中，可用來取代 `0x1` 以存取標準函式庫模組。

若要從另一個套件匯入模組，請使用 `use` 關鍵字後接模組路徑。模組路徑由套件地址（或別名）與模組名稱組成，兩者以 `::` 分隔。

```move file=packages/samples/sources/move-basics/importing-modules-external.move anchor=external

```

> 注意：模組地址名稱取自套件清單文件（`Move.toml`）的 `[addresses]` 區段，而非 `[dependencies]` 區段中使用的名稱。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[使用與別名 (Uses and Aliases)](./../../reference/uses)。
