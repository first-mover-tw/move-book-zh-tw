---
description: 什麼是 Sui 物件 (Object)：鏈上數位資產的唯一識別碼、型別、擁有權，以及轉移 (transfer) 和共享 (share) 等原生操作。
title: 什麼是物件 (Object)？
keywords:
  - Move
  - Sui
  - Move tutorial
  - what
  - object
  - object model
questions:
  - What is an Object?
  - How do I use What is an Object? in Move?
answer: 'What is a Sui Object: unique identifiers, types, ownership, and native operations like transfer and share for onchain digital assets.'
goal:
  description: 'Reader understands what is a Sui Object: unique identifiers, types, ownership, and native operations like transfer and share for onchain digital assets'
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

# 什麼是物件？ (What is an Object?) {#what-is-an-object}

在 Sui 中，*物件*是儲存單位。原本的 Move 會將資料儲存在帳戶之下，Sui 則會直接將物件儲存在全域狀態中，系統會記錄每個物件各自的身分、型別與擁有者。物件支援如 _transfer_ 與 _share_ 等原生儲存操作，並且旨在讓[前面章節](./digital-assets)介紹的資產特性——所有權、不可複製性、不可丟棄性——能夠實際運用。

在 Move 原始碼中，物件並不是一種新的值類型——它是具有 `key` 能力與特殊 `id` 欄位的一般 [struct](./../move-basics/struct)：

```move
/// 遊戲角色；與其他 struct 一樣，藉由 `key` 能力與
/// `id: UID` 欄位成為物件。
public struct Hero has key {
    id: UID,
    level: u8,
}
```

你所知道的所有 struct 知識依然適用。物件額外提供的是附加於儲存中物件的系統層級中繼資料。我們會在[使用物件](./../storage)章節中詳細介紹定義規則；此處則聚焦於每個物件都具備的特性：

- **型別**：每個物件都有型別，用以定義物件的結構與行為。不同型別的物件無法混合或互換使用，確保物件會依其型別系統正確使用。

- **唯一 ID**：每個物件都有唯一識別碼，用以區別其他物件。此 ID 會在建立物件時產生且不可變動，因此能跨交易與擁有者追蹤及參考物件。這就是上述定義中的 `id: UID` 欄位。

- **擁有者**：每個物件都與擁有者關聯，擁有者可控制對物件的變更。物件可以由帳戶獨佔擁有、由另一個物件擁有、與整個網路共用、設為不可變，或處於 _party_ 狀態——介於獨佔與共用所有權之間的狀態。我們會在[所有權](./ownership)章節中詳細討論這五種所有權狀態。

  請注意，所有權不會控制物件的機密性 &mdash; 你始終可以從 Move 外部讀取鏈上物件的內容。絕對不應在物件內儲存未加密的機密資訊。

- **資料**：物件封裝其資料，簡化管理與操作。資料結構與操作由物件的型別——也就是 struct 的欄位——所定義。

- **版本**：每個物件都帶有版本號，系統會在交易修改物件時遞增該版本。版本可防範 _replay_：交易會以特定版本參考其輸入物件，因此相同交易——或對已變更物件的過時參考——無法執行兩次。它扮演帳戶型區塊鏈中 _nonce_ 的角色，但以每個物件為單位，而非每個帳戶。

- **雜湊摘要**：每個物件都有雜湊摘要，亦即物件資料的雜湊值。雜湊摘要用於以密碼學方式驗證物件資料的完整性，並確保資料未遭竄改。每當物件資料變更時，都會重新計算雜湊摘要。

## 總結 (Summary) {#summary}

- 物件是 Sui 的儲存單位：儲存在全域狀態中，且由系統追蹤身分與所有權的具型別值。
- 在 Move 原始碼中，物件是具有 `key` 能力與 `id: UID` 欄位的 struct。
- 每個物件都有型別、唯一 ID、擁有者、資料、版本與雜湊摘要。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的 [Object Model](https://docs.sui.io/guides/developer/objects/object-model)。
