---
description: Sui 物件模型 (Sui Object Model) 詳解：Sui 區塊鏈 (Sui blockchain) 上數位資產 (digital asset) 表示法、所有權 (ownership) 與儲存 (storage) 背後的理論與概念。
title: 物件模型 (Object Model)
keywords:
  - Move
  - Sui
  - Move tutorial
  - object
  - model
  - object model
questions:
  - What is the Sui object model?
  - How do structs become objects?
  - What abilities do objects need?
answer: The Sui object model defines how Move structs with the key ability and a UID field become addressable onchain objects that can be owned, shared, frozen, or wrapped.
goal:
  description: Reader understands the Sui object model and how Move structs become onchain objects
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 30
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 物件模型 (Object Model) {#object-model}

到目前為止，我們將 Move 視為一門語言來研究：型別、函式與能力，全都作用於在單筆交易中生滅的值。但智慧合約唯有其狀態能持續保留時才有用。本章介紹「_物件模型_」——Sui 對資料如何在鏈上儲存、擁有與存取此問題的解答。

本章著重於理論與概念，為你接下來深入瞭解儲存操作與資源擁有權的實作做好準備。依照以下順序閱讀效果最佳：

- [數位資產語言](./digital-assets) - 為何 Move 將資產視為第一級值，以及構成資產的特性；
- [Move 的演進](./evolution-of-move) - 原始的帳戶式儲存模型如何運作，以及 Sui 為何取代它；
- [什麼是物件？](./object-model) - 作為儲存單位的物件：型別、ID、擁有者、版本與摘要；
- [擁有權](./ownership) - 物件可被擁有的五種方式，以及每種方式所允許的操作；
- [快速路徑與共識](./fast-path-and-consensus) - 擁有權如何決定交易的執行方式。

後續章節會直接建立在這些概念之上：[使用物件](./../storage)說明如何在程式碼中定義及管理物件，而
[進階可程式化能力](./../programmability)則涵蓋建構於其上的功能。

> 本章提供物件模型背後概念與原則的高階概覽。如需更詳細的協定層級說明，請參閱
> [Sui 文件](https://docs.sui.io/guides/developer/objects/object-model)。
