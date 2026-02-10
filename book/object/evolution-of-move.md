# Move 的演進 (Evolution of Move)

雖然 Move 的創立初衷是為了管理數位資產，但其最初的存儲模型相對笨重，且不太適應許多使用案例。例如，如果 Alice 想將資產 X 轉移給 Bob，Bob 必須先建立一個新的「空」資源，之後 Alice 才能將資產 X 轉移給他。這個過程不夠直觀，且帶來了實作上的挑戰，部分原因在於 [Diem](https://www.diem.com/en-us) 設計上的限制。原始設計的另一個缺點是缺乏內建的「轉移 (transfer)」操作支援，導致每個模組都必須實作自己的存儲轉移邏輯。此外，在單個帳戶中管理多樣化的異質資產集合也特別具有挑戰性。

Sui 透過重新設計物件的存儲和所有權模型來應對這些挑戰，使其更貼近現實世界中的物件互動方式。憑藉原生所有權和 **轉移 (transfer)** 的觀念，Alice 可以直接將資產 X 轉移給 Bob。此外，Bob 無需任何準備步驟即可維護不同資產的集合。這些改進為 Sui 的物件模型 (Object Model) 奠定了基礎。

## 總結 (Summary)

- Move 最初的存儲模型不適合管理數位資產，需要複雜且受限的轉移操作。
- Sui 引入了物件模型 (Object Model)，提供了原生的所有權觀念，簡化了資產管理並啟用了異質資產集合。

## 延伸閱讀

- Sam Blackshear 所撰寫的 [為什麼我們創造了 Sui Move (Why We Created Sui Move)](https://blog.sui.io/why-we-created-sui-move/)。
