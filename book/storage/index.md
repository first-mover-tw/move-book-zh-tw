---
description: 了解如何在 Move 中使用 Sui 物件（object）：儲存能力 (storage abilities)、轉移函式 (transfer functions)、所有權規則 (ownership rules) 以及物件生命週期管理 (object lifecycle management)。
---

# 使用物件 (Using Objects) {#using-objects}

[物件模型][object-model] 章節從概念上介紹了物件：儲存的單位，具有身分、擁有者，以及形塑執行方式的擁有權狀態。本章將這些概念轉化為程式碼。你將學到如何定義物件型別、如何建立與銷毀物件，以及如何在擁有權狀態之間移動它們 - 轉移、凍結與共享。

各小節彼此銜接,建議依序閱讀:

- [能力：Key (Ability: Key)](./key-ability) -讓 struct 轉變為物件的能力;
- [能力：Store (Ability: Store)](./store-ability) -允許型別被儲存於物件內部的能力,並控制誰可以操作該物件;
- [Sui 驗證器：內部約束 (Sui Verifier: Internal Constraint)](./internal-constraint) - bytecode 層級的規則,將關鍵操作保留給定義該型別的模組;
- [儲存函式 (Storage Functions)](./storage-functions) - 將物件放入儲存空間的操作:轉移、凍結與共享;
- [UID 與 ID (UID and ID)](./uid-and-id) - 每個物件的身分,以及其生命週期;
- [作為物件接收 (Receiving as Object)](./transfer-to-object) - 讓物件能擁有其他物件的機制。

> 來自 [Sui Framework](./../programmability/sui-framework) 的兩個型別幾乎出現在本章的每一個範例中:`UID` - 儲存在每個物件中的唯一識別碼,以及 `TxContext` - 描述當前交易的特殊值,任何函式都可以將其作為最後一個引數取得。這兩者稍後都會有深入說明(本章的 [UID 與 ID (UID and ID)](./uid-and-id),下一章的 [交易情境 (Transaction Context)](./../programmability/transaction-context));現階段只需知道 `object::new(ctx)` 會使用交易情境來產生一個全新、唯一的 `UID`。

如果你還沒讀過 [物件模型][object-model] 章節,建議先從那裡開始,再繼續閱讀本章。

[object-model]: ./../object
