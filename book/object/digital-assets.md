---
description:
  Move 如何原生處理數位資產 (digital assets)：從同質化代幣 (fungible tokens) 到 NFT，具備內建安全性與型別層級的資源保證
  (type-level resource guarantees)。
---

# Move - 數位資產的語言 (Move - Language for Digital Assets) {#move---language-for-digital-assets}

智能合約程式語言在歷史上一直專注於定義與管理數位資產。舉例來說，以太坊的 ERC-20 標準率先建立了一套與數位貨幣代幣互動的標準，為區塊鏈上建立與管理數位貨幣立下了藍圖。隨後，ERC-721 標準的推出標誌著重大演進，讓非同質化代幣（NFT）的概念普及開來，這種代幣代表獨特且不可分割的資產。這些標準為我們今日所見的複雜數位資產打下了基礎。

<!-- ## Move and Digital Assets -->

<!-- note: consider "native" -> "fine-grained" -->

然而，以太坊的程式設計模型缺乏對資產的原生表示方式。從外部來看，ERC-20 代幣的行為就像資產一樣，但在合約內部，它僅僅是帳本中的條目——一個地址對應餘額的映射——在語言層面上並不存在真正代表資產的值。從一開始，Move 的目標就是為資產提供第一等抽象，為思考與撰寫資產相關程式開啟了新的途徑。

<!-- Move was initially created in 2018 as part of the Libra project. The language was designed to address shortcomings in existing smart contract languages, especially in handling assets and access control. The Move language aims to provide first-class abstractions for these concepts, improving the safety and productivity of smart contract programming. -->

值得特別強調的是，哪些特性對資產而言是不可或缺的：

- **所有權（Ownership）：** 每一項資產都與一位擁有者相關聯，這反映了現實世界中所有權的直觀概念，就像你可以擁有一輛車一樣，你也可以擁有一項數位資產。Move 以這樣的方式強制執行所有權：一旦資產被*移動（moved）*，前一位擁有者就完全喪失對它的任何控制權。這個機制確保了所有權轉移的清晰與安全。

- **不可複製（Non-copyable）：** 在現實世界中，獨一無二的物品無法輕易地被複製。Move 將這個原則套用到數位資產上，確保它們在程式中無法被任意複製。這項特性對於維持數位資產的稀缺性與獨特性至關重要，反映出實體資產本身的內在價值。

- **不可丟棄（Non-discardable）：** 就像你不會在毫無痕跡的情況下不小心弄丟一間房子或一輛車，Move 確保程式中任何資產都不會被丟棄或遺失。相反地，資產必須被明確地轉移或銷毀。這項特性保證了數位資產能被審慎地處理，避免意外遺失，並確保資產管理過程中的可課責性。

上述三項特性，你其實已經以語言特性的形式接觸過了。所有權由[移動語意](./../move-basics/ownership-and-scope)強制執行：以傳值方式傳遞一個值會將其*移動*，而先前的作用域則喪失存取權。而能力系統則控制著另外兩項特性：沒有 [`copy`](./../move-basics/copy-ability) 能力的結構體無法被複製，沒有 [`drop`](./../move-basics/drop-ability) 能力的結構體則無法被丟棄。在[Move 基礎](./../move-basics)這一章看似是一組限制的東西，實際上正是為資產建模量身打造的工具組：一個既沒有 `copy` 也沒有 `drop` 能力的型別，在每次被建立時都*必須*被明確地處理——儲存、轉移，或銷毀。

## 總結 (Summary) {#summary}

- Move 的設計目標是為數位資產提供第一等抽象，讓開發者能夠原生地建立與管理資產。
- 數位資產的必要特性包括所有權、不可複製性與不可丟棄性，而 Move 在其設計中強制執行這些特性。
- 這些特性直接對應到你已經認識的語言特性：移動語意，以及 `copy` 與 `drop` 能力。
- Move 的資產模型反映了現實世界中的資產管理方式，確保資產所有權與轉移過程的安全性與可課責性。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Move: A Language With Programmable Resources (pdf)](https://developers.diem.com/papers/diem-move-a-language-with-programmable-resources/2019-06-18.pdf)，作者 Sam Blackshear、Evan Cheng、David L. Dill、Victor Gao、Ben Maurer、Todd Nowacki、Alistair Pott、
  Shaz Qadeer、Rain、Dario Russi、Stephane Sezer、Tim Zakian、Runtian Zhou\*
