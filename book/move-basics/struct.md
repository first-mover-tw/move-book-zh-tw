# 使用結構定義自定義類型 (Custom Types with Struct)

當涉及到定義自定義類型時，Move 的類型系統大放異彩。使用者定義的類型可以根據應用程式的特定需求量身定制，不僅在資料層級，在其行為上也是如此。在本節中，我們將介紹 `struct` 的定義及其使用方法。

## 結構 (Struct)

要定義自定義類型，可以使用 `struct` 關鍵字，後接類型的名稱。在名稱之後，您可以定義結構的欄位。每個欄位都使用 `欄位名稱: 欄位類型` 的語法定義。欄位定義必須以逗號分隔。欄位可以是任何類型，包括其他結構。

> Move 不支援遞迴結構，這意味著結構不能包含自身作為欄位。

```move file=packages/samples/sources/move-basics/struct.move anchor=def

```

在上面的範例中，我們定義了一個具有五個欄位的 `Record` 結構。`title` 欄位類型為 `String`，`artist` 欄位類型為 `Artist`，`year` 欄位類型為 `u16`，`is_debut` 欄位類型為 `bool`，而 `edition` 欄位類型為 `Option<u16>`。`edition` 欄位使用 `Option<u16>` 類型來表示版本是選填的。

結構預設是私有的，這意味著它們不能在定義它們的模組之外被匯入和使用。它們的欄位也是私有的，不能從模組外部存取。有關不同可見性修飾符的更多資訊，請參閱 [可見性](./visibility)。

> 結構的欄位是私有的，只能由定義該結構的模組存取。只有在定義結構的模組提供公開函式來存取欄位的情況下，才可能在其他模組中讀取和寫入結構的欄位。

## 建立與使用實例

我們剛才描述了結構的 **定義**。現在讓我們看看如何初始化並使用一個結構。結構可以使用 `結構名稱 { 欄位1: 值1, 欄位2: 值2, ... }` 的語法進行初始化。欄位可以按任何順序初始化，並且所有必要的欄位都必須設置。

```move file=packages/samples/sources/move-basics/struct.move anchor=pack

```

在上面的範例中，我們建立了一個 `Artist` 結構的實例，並將 `name` 欄位設置為字串 "The Beatles"。

要存取結構的欄位，可以使用 `.` 運算子後接欄位名稱。

```move file=packages/samples/sources/move-basics/struct.move anchor=access

```

只有定義結構的模組可以存取其欄位（包括可變存取和不可變存取）。因此，上述程式碼應與 `Artist` 結構位於同一個模組中。

## 解構結構 (Unpacking a struct)

結構預設是不可捨棄的，這意味著初始化的結構值必須被使用，無論是透過儲存還是 **解構 (unpacking)**。解構結構意味著將其拆解為其各個欄位。這可以使用 `let` 關鍵字後接結構名稱和欄位名稱來完成。

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack

```

在上面的範例中，我們解構了 `Artist` 結構，並建立了一個值為 `name` 欄位內容的新變數 `name`。由於變數沒有被使用，編譯器會發出警告。要消除警告，可以使用底線 `_` 來表示該變數是刻意不使用的。

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack_ignore

```

## 延伸閱讀

- Move 參考手冊中的 [結構 (Structs)](./../../reference/structs)。
