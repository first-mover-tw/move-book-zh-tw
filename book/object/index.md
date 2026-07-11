---
description: Sui 物件模型解析 (The Sui Object Model Explained)：Sui 區塊鏈上數位資產表示、擁有權與儲存背後的理論與概念。
---

# 物件模型 (Object Model) {#object-model}

到目前為止，我們把 Move 當作一種語言在研究：型別、函式與能力，這些操作的值都在單一交易內誕生與消亡。但智能合約唯有在其狀態能夠持久化時才有用。本章介紹**物件模型 (Object Model)**——這是 Sui 對於「鏈上資料如何被儲存、擁有與存取」這個問題所給出的答案。

本章聚焦於理論與概念，為你即將深入研究儲存操作與資源所有權的實務內容做好準備。建議依序閱讀：

- [數位資產的語言 (Language for Digital Assets)](./digital-assets) - 為什麼 Move 將資產視為一等公民值，以及哪些特性構成一項資產；
- [Move 的演進 (Evolution of Move)](./evolution-of-move) - 原本的帳戶式儲存模型如何運作，以及 Sui 為何要取而代之；
- [什麼是物件？ (What is an Object?)](./object-model) - 作為儲存單位的物件：型別、ID、擁有者、版本與摘要；
- [所有權 (Ownership)](./ownership) - 物件可被擁有的五種方式，以及各自允許的操作；
- [快速路徑與共識 (Fast Path and Consensus)](./fast-path-and-consensus) - 所有權如何決定交易的執行方式。

後續章節將直接建立在這些概念之上：[使用物件 (Using Objects)](./../storage) 展示物件在程式碼中如何被定義與管理，而
[進階可程式化性 (Advanced Programmability)](./../programmability) 涵蓋了建立在其之上的各種功能。

> 本章是物件模型背後概念與原則的高階概覽。若需要更詳細、協定層級的說明，請參閱
> [Sui 文件](https://docs.sui.io/guides/developer/objects/object-model)。
