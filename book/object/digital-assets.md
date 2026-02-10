# Move — 數位資產的專屬語言 (Move - Language for Digital Assets)

智慧合約程式語言歷來專注於定義和管理數位資產。例如，以太坊 (Ethereum) 的 ERC-20 標準開創了一套與數位貨幣代幣互動的標準，建立了在區塊鏈上建立和管理數位貨幣的藍圖。隨後，ERC-721 標準的引入標誌著一次重大的演進，普及了非同質化代幣 (NFTs) 的概念，用於表示唯一的、不可分割的資產。這些標準為我們今天看到的複雜數位資產奠定了基礎。

然而，以太坊的程式模型缺乏資產的原生表示。換句話說，從外部看，智慧合約表現得像一個資產，但語言本身並沒有一種生來即能表示資產的方式。Move 從一開始就旨在為資產提供 **一等抽象 (first-class abstraction)**，為思考和編寫資產開啟了新的途徑。

強調資產的核心屬性至關重要：

- **所有權 (Ownership):** 每個資產都與所有者相關聯，這反映了現實世界中直觀的所有權概念 — 就像您擁有一輛車一樣，您可以擁有一個數位資產。Move 強制執行所有權，一旦資產被 **移動 (moved)**，原所有者就完全失去了對它的控制權。這種機制確保了清晰且安全的權屬變更。
- **不可複製 (Non-copyable):** 在現實世界中，獨特的物品無法被輕易複製。Move 將此原則應用於數位資產，確保它們不能在程式中被隨意複製。這一屬性對於維持數位資產的稀缺性和唯一性至關重要，反映了實體資產的內在價值。
- **不可丟棄 (Non-discardable):** 就像您不會無緣無故地丟失一棟房子或一輛車一樣，Move 確保任何資產都不會在程式中被丟棄或丟失。相反，資產必須被明確地轉移或銷毀。這一屬性保證了對數位資產的審慎處理，防止意外流失並確保資產管理的可問責性。

Move 成功地在其設計中封裝了這些屬性，成為數位資產的理想語言。

## 總結 (Summary)

- Move 旨在為數位資產提供一等抽象，使開發人員能夠以原生方式建立和管理資產。
- 數位資產的基本屬性包括所有權、不可複製性和不可丟棄性，Move 在其設計中強制執行這些屬性。
- Move 的資產模型反映了真實世界的資產管理方式，確保了資產所有權和轉移的安全與可問責性。

## 延伸閱讀

- [Move: A Language With Programmable Resources (pdf)](https://developers.diem.com/papers/diem-move-a-language-with-programmable-resources/2019-06-18.pdf) — 作者：Sam Blackshear, Evan Cheng, David L. Dill, Victor Gao, Ben Maurer, Todd Nowacki, Alistair Pott, Shaz Qadeer, Rain, Dario Russi, Stephane Sezer, Tim Zakian, Runtian Zhou*
