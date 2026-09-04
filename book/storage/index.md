---
description: 了解如何在 Move 中使用 Sui 物件 (objects)：儲存能力、轉移函式、所有權規則及物件生命週期管理。
title: 使用物件 (Objects)
keywords:
  - Move
  - Sui
  - Move tutorial
  - using
  - objects
  - object model
questions:
  - How does storage work on Sui?
  - How do I store objects onchain?
answer: Sui storage covers how objects with key and store abilities are persisted onchain, including transfer functions, storage operations, and the UID/ID system.
goal:
  description: Reader understands how objects are stored, transferred, and managed on Sui
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

# 使用物件 (Using Objects) {#using-objects}

[物件模型][object-model]章節從概念上介紹了物件：具備身分識別、擁有者，以及會影響執行方式之擁有權狀態的儲存單位。本章將這些概念轉化為原始碼。你將學習如何定義物件型別、如何建立及銷毀物件，以及如何在擁有權狀態之間移動物件──轉移、凍結及共享。

各節內容彼此相互建立，建議依序閱讀：

- [能力：Key](./key-ability) - 將結構轉換為物件的能力；
- [能力：Store](./store-ability) - 允許將型別儲存於物件內部，並控制誰能操作該物件的能力；
- [Sui 驗證器：內部限制](./internal-constraint) - 在位元組碼層級保留關鍵操作給定義該型別之模組的規則；
- [儲存函式](./storage-functions) - 將物件放入儲存空間的操作：轉移、凍結及共享；
- [UID 與 ID](./uid-and-id) - 每個物件的身分識別及其生命週期；
- [以物件身分接收](./transfer-to-object) - 讓物件擁有其他物件的機制。

> [Sui Framework](./../programmability/sui-framework) 中的兩個型別幾乎會出現在本章所有範例中：`UID`──儲存在每個物件中的唯一識別碼──以及 `TxContext`──描述目前交易的特殊值，可作為任何函式的最後一個引數使用。稍後將深入介紹兩者（本章的 [UID 與 ID](./uid-and-id)，以及下一章的 [交易情境](./../programmability/transaction-context)）；剛開始時，只要知道 `object::new(ctx)` 會使用交易情境產生全新且唯一的 `UID` 即可。

若你尚未閱讀[物件模型][object-model]章節，建議先從該章開始，再繼續閱讀。

[object-model]: ./../object
