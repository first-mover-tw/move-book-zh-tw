---
description: 模組 (Modules) 是 Move 的建構區塊：學習如何在你的 Sui 智慧合約中宣告、組織與編譯模組。
---

# 模組 (Module) {#module}

模組是 Move 中程式碼組織的基本單位。模組用於將程式碼分組並隔離，模組的所有成員預設對模組外部是私有的。這使得模組成為一個信任邊界：如後續章節所示，只有定義某型別的模組才能建立、修改與銷毀該型別的值。在本節中，你將學習如何定義模組、宣告其成員，以及如何從其他模組存取它。

## 模組宣告 (Module Declaration) {#module-declaration}

模組使用 `module` 關鍵字宣告，後面接套件地址與模組名稱，兩者以 `::` 分隔，接著是分號與模組主體。模組名稱應使用 `snake_case` 風格——全部小寫字母，單詞之間以底線分隔。模組名稱在套件中必須是唯一的。

通常，`sources/` 資料夾中的一個檔案包含一個模組。檔案名稱應與模組名稱一致——例如，`donut_shop` 模組應存放在 `donut_shop.move` 檔案中。你可以在
[程式碼慣例](./../guides/code-quality-checklist) 章節中閱讀更多關於程式碼慣例的內容。

> 如果你需要在一個檔案中宣告多個模組，你必須使用 [模組區塊 (Module Block)](#module-block) 語法。

```move file=packages/samples/sources/move-basics/module-label.move anchor=module

```

## 地址與具名地址 (Address and Named Address) {#address-and-named-address}

模組地址可以用兩種方式指定：作為地址 _字面量_（不需要 `@` 前綴），或作為
[套件清單 (Package Manifest)](./../concepts/manifest) 中宣告的套件名稱。

```move file=packages/samples/sources/move-basics/module.move anchor=address_literal

```

Move.toml 中的 Package 區段：

```toml
[package]
name = "book"
edition = "2024"
```

## 模組成員 (Module Members) {#module-members}

模組成員在模組主體內宣告。為了說明這點，讓我們定義一個簡單的模組，其中包含一個匯入、一個常數、一個結構體與一個函式：

```move file=packages/samples/sources/move-basics/module-members.move anchor=members

```

每個成員都以自己的關鍵字開頭：`use` 將其他模組帶入作用域
（[匯入模組](./importing-modules)）、`const` 定義一個永遠不變的值
（[常數](./constants)）、`struct` 宣告一個自訂資料型別（[結構體](./struct)），而 `fun`
宣告一個函式（[函式](./function)）。目前先不用擔心細節——這些內容在本章中各自都有專門的章節；現在只需要認識這些關鍵字，並知道它們都存在於模組層級即可。

## 模組區塊 (Module Block) {#module-block}

Move 的 2024 版之前的版本要求模組主體必須是一個 _模組區塊_——即模組的內容以大括號 `{}` 包裹。這種區塊語法仍然受到支援，而選擇它而非上述 _標籤_ 語法的唯一理由，是在一個檔案中宣告多個模組——這種情況很少需要，也不是建議的做法。

```move file=packages/samples/sources/move-basics/module.move anchor=members

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [模組 (Modules)](./../../reference/modules)。
