---
description: 模組 (Modules) 是 Move 的建構區塊：了解如何在 Sui 智慧合約中宣告、組織及編譯模組 (modules)。
title: 模組 (Module)
keywords:
  - Move
  - Sui
  - Move tutorial
  - module
  - modules
questions:
  - What is Module in Move?
  - How do I use Module in Move?
  - What is Module Declaration in Move?
  - What is Address and Named Address in Move?
answer: 'Modules are the building blocks of Move: learn how to declare, organize, and compile modules in your Sui smart contracts.'
goal:
  description: 'Reader understands modules are the building blocks of Move: learn how to declare, organize, and compile modules in your Sui smart contracts'
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

# 模組 (Module) {#module}

模組是 Move 中組織原始碼的基本單位。模組用於將原始碼分組及隔離，而且模組的所有成員預設皆為模組私有。這使模組成為信任邊界：如後續章節所示，只有定義型別的模組可以建立、修改及銷毀其值。本節將說明如何定義模組、宣告其成員，以及從其他模組存取它。

## 模組宣告 (Module Declaration) {#module-declaration}

模組使用 `module` 關鍵字宣告，後接以 `::` 分隔的套件地址與模組名稱，接著是分號及模組主體。模組名稱應採用 `snake_case` 格式——全部使用小寫字母，並以底線分隔單字。模組名稱在套件中必須是唯一的。

通常，`sources/` 資料夾中的單一文件會包含單一模組。檔案名稱應與模組名稱相符——例如，`donut_shop` 模組應儲存在 `donut_shop.move` 檔案中。你可以在[程式碼撰寫慣例](./../guides/code-quality-checklist)章節中進一步閱讀程式碼撰寫慣例。

> 若需要在一個檔案中宣告多個模組，必須使用[模組區塊](#module-block)語法。

```move file=packages/samples/sources/move-basics/module-label.move anchor=module

```

## 地址與具名地址 (Address and Named Address) {#address-and-named-address}

模組地址可透過兩種方式指定：作為地址*字面值*（不需要 `@` 前綴），或作為在[套件清單](./../concepts/manifest)中宣告的套件名稱。

```move file=packages/samples/sources/move-basics/module.move anchor=address_literal

```

Move.toml 中的套件區段：

```toml
[package]
name = "book"
edition = "2024"
```

## 模組成員 (Module Members) {#module-members}

模組成員在模組主體內宣告。為了說明這點，讓我們定義一個簡單的模組，其中包含匯入、常數、結構及函式：

```move file=packages/samples/sources/move-basics/module-members.move anchor=members

```

每個成員都以各自的關鍵字開頭：`use` 將其他模組帶入作用域（[匯入模組](./importing-modules)）、`const` 定義永不變更的值（[常數](./constants)）、`struct` 宣告自訂資料型別（[結構](./struct)），而 `fun` 宣告函式（[函式](./function)）。暫時不必擔心細節——本章會為每一項提供專屬章節；目前只要能辨識這些關鍵字，並知道它們全都位於模組層級即可。

## 模組區塊 (Module Block) {#module-block}

Move 的 2024 版以前版本要求模組主體必須是*模組區塊*——以大括號 `{}` 包圍的模組內容。區塊語法仍受支援，而相較於上述的*標籤*語法，唯一偏好使用它的理由是在一個檔案中宣告多個模組——這很少需要，也不是建議的做法。

```move file=packages/samples/sources/move-basics/module.move anchor=members

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[模組](./../../reference/modules)。
