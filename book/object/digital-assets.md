---
description: Move (Move) 如何原生處理數位資產：從同質化代幣到 NFT，具備內建安全性與型別層級的資源保證。
title: Move－數位資產語言 (Language for Digital Assets)
keywords:
  - Move
  - Sui
  - Move tutorial
  - move
  - language
  - digital
  - assets
questions:
  - What is Move - Language for Digital Assets in Move?
  - How do I use Move - Language for Digital Assets in Move?
answer: 'How Move handles digital assets natively: from fungible tokens to NFTs, with built-in safety and type-level resource guarantees.'
goal:
  description: 'Reader understands how Move handles digital assets natively: from fungible tokens to NFTs, with built-in safety and type-level resource guarantees'
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

# Move——數位資產語言 (Move - Language for Digital Assets) {#move---language-for-digital-assets}

智慧合約程式設計語言在歷史上一直著重於定義及管理數位資產。例如，Ethereum 的 ERC-20 標準率先制定了一組與數位貨幣代幣互動的標準，建立了在區塊鏈上建立及管理數位貨幣的藍圖。隨後，ERC-721 標準的推出標誌著重大演進，普及了非同質化代幣（NFT）的概念，亦即代表獨特且不可分割資產的代幣。這些標準為我們今日所見的複雜數位資產奠定了基礎。

<!-- ## Move 與數位資產 (Move and Digital Assets) -->

<!-- 註：考慮將 "native" 改為 "fine-grained" -->

然而，Ethereum 的程式設計模型缺乏資產的原生表示法。從外部來看，ERC-20 代幣的行為如同資產；但在合約內部，它僅以帳本中的項目存在——亦即地址到餘額的對應關係——而語言中沒有任何一個值 _就是_ 該資產。Move 從一開始便致力於為資產提供一級抽象，開闢思考及程式設計資產的新途徑。

<!-- Move 最初於 2018 年作為 Libra 專案的一部分建立。此語言旨在解決既有智慧合約語言的不足，尤其是在處理資產及存取控制方面。Move 語言旨在為這些概念提供一級抽象，以提升智慧合約程式設計的安全性及生產力。 -->

務必突顯資產不可或缺的特性：

- **所有權**：每項資產皆與一名擁有者相關聯，如同實體世界中直觀的所有權概念：正如你擁有一輛車，你也可以擁有數位資產。Move 以這樣的方式強制實施所有權：一旦資產被 _移動_，原擁有者便完全失去對它的任何控制權。此機制確保所有權明確且安全地變更。

- **不可複製**：在真實世界中，獨特物品無法毫不費力地複製。Move 將此原則套用至數位資產，確保它們無法在程式中任意複製。此特性對於維持數位資產的稀缺性及獨特性至關重要，並反映實體資產的內在價值。

- **不可丟棄**：如同你無法在不留痕跡的情況下意外遺失房屋或汽車，Move 確保任何資產都不會在程式中遭到丟棄或遺失。資產必須明確地轉移或銷毀。此特性確保數位資產受到審慎處理，防止意外遺失，並確保資產管理的可追責性。

你已經將這三項特性都視為語言功能接觸過了。所有權由[移動語意](./../move-basics/ownership-and-scope)強制實施：以值傳遞一個值會將其 _移動_，而先前的作用域會失去存取權。能力系統則控制另外兩項特性：沒有 [`copy`](./../move-basics/copy-ability) 能力的結構無法複製，沒有 [`drop`](./../move-basics/drop-ability) 能力的結構無法丟棄。在 [Move 基礎](./../move-basics)章節中看似一組限制的內容，實際上正是建模資產所需的完整工具組：同時不具備 `copy` 及 `drop` 的型別，每次建立時都 _必須_ 明確處理——儲存、轉移或銷毀。

## 總結 (Summary) {#summary}

- Move 的設計目標是為數位資產提供一級抽象，讓開發者能以原生方式建立及管理資產。
- 數位資產的必要特性包括所有權、不可複製性及不可丟棄性，Move 會透過其設計強制實施這些特性。
- 這些特性直接對應到你已經熟悉的語言功能：移動語意，以及 `copy` 和 `drop` 能力。
- Move 的資產模型反映真實世界的資產管理，確保安全且可追責的資產所有權及轉移。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Move：具備可程式化資源的語言（PDF）](https://developers.diem.com/papers/diem-move-a-language-with-programmable-resources/2019-06-18.pdf)
  作者為 Sam Blackshear、Evan Cheng、David L. Dill、Victor Gao、Ben Maurer、Todd Nowacki、Alistair Pott、
  Shaz Qadeer、Rain、Dario Russi、Stephane Sezer、Tim Zakian、Runtian Zhou\*
