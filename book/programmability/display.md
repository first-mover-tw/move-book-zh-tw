# 物件顯示 (Object Display)

Sui 上的物件在結構和行為上都是顯性的，並且可以以易於理解的方式顯示。然而，為了支援客戶端更豐富的元資料，有一種標準且高效的方式來向客戶端「描述」它們 —— 即 [Sui 框架](./sui-framework) 中定義的 `Display` 物件。

## 背景

在歷史上，人們曾有過不同的嘗試，試圖就物件的標準結構達成一致，以便在使用者介面中顯示。其中一種方法是在物件結構體中定義特定的欄位，當這些欄位存在時，就會在 UI 中使用。這種方法不夠靈活，要求開發人員在每個物件中定義相同的欄位，有時這些欄位對該物件來說並沒有意義。

```move file=packages/samples/sources/programmability/display.move anchor=background

```

如果任何欄位包含靜態資料，它將在每個物件中重複出現。此外，由於 Move 沒有介面 (interfaces)，如果不「手動」檢查物件的類型，就無法知道物件是否具有特定欄位，這使得客戶端獲取資料變得更加複雜。

## 物件顯示 (Object Display)

為了探討這些問題，Sui 引入了一種標準的物件顯示描述方式。與其在物件結構體中定義欄位，顯示元資料 (display metadata) 存儲在一個單獨的物件中，該物件與類型相關聯。透過這種方式，顯示元資料不會重複，且易於擴展和維護。

Sui Display 的另一個重要特性是能夠定義模板，並在這些模板中使用物件欄位。這不僅提供了更靈活的顯示方式，還將開發人員從「在每個物件中定義具有相同名稱和類型的相同欄位」的需求中解放出來。

> 物件顯示由 [Sui 全節點 (Sui Full Node)](https://docs.sui.io/guides/operator/sui-full-node) 原生支援，如果物件類型有關聯的 Display，客戶端即可獲取任何物件的顯示元資料。

```move file=packages/samples/sources/programmability/display.move anchor=hero

```

## 創作者特權 (Creator Privilege)

雖然物件可以由帳戶擁有，並受限於 [絕對所有權 (True Ownership)](./../object/ownership#account-owner-or-single-owner)，但 Display 可以由物件的 **創作者 (creator)** 擁有。透過這種方式，創作者可以更新顯示元資料並全域套用更改，而無需更新每個物件。創作者還可以將 Display 轉移給另一個帳戶，甚至為物件開發具有自定義功能的應用程式來管理元資料。

## 標準欄位

最廣泛支援的欄位包括：

- `name`: 物件的名稱。當使用者檢視物件時顯示。
- `description`: 物件的描述。當使用者檢視物件時顯示。
- `link`: 指向在應用程式中使用的物件連結。
- `image_url`: 解析為物件影像的 URL 或 blob。
- `thumbnail_url`: 指向較小影像的 URL，用於錢包、瀏覽器和其他產品中的預覽。
- `project_url`: 指向與物件或創作者相關的網站連結。
- `creator`: 指示物件創作者的字串。

> 請參考 [Sui 文件](https://docs.sui.io/standards/display) 以獲取支援欄位的最新清單。

雖然有一組標準欄位，但 Display 物件並不強制要求使用它們。開發人員可以根據需要定義任何欄位，而客戶端可以隨意使用它們。某些應用程式可能需要額外欄位並省略其他欄位，Display 足夠靈活以支援這些需求。

## 使用 Display

`Display` 物件定義在 `sui::display` 模組中。它是一個泛型結構，接收一個 phantom 類型作為參數。該 phantom 類型用於將 `Display` 物件與其描述的類型相關聯。`Display` 物件的 `fields` 是一個鍵值對的 `VecMap`，其中鍵是欄位名稱，值是欄位數值。`version` 欄位用於對顯示元資料進行版本控制，並在 `update_display` 呼叫時更新。

```move
module sui::display;

public struct Display<phantom T: key> has key, store {
    id: UID,
    /// 包含顯示欄位。目前支援的欄位有：name, link, image 和 description。
    fields: VecMap<String, String>,
    /// 只能由發佈者 (Publisher) 手動更新的版本。
    version: u16
}
```

要建立新的 Display，需要 [發佈者 (Publisher)](./publisher) 物件，因為它作為類型所有權的證明。

## 模板語法 (Template Syntax)

目前，Display 支援簡單的字串插值 (string interpolation)，並可以在其模板中使用結構體欄位（及路徑）。語法非常簡單 —— `{path}` 會被該路徑下欄位的數值替換。路徑是由句點分隔的欄位名稱列表，如果是巢狀欄位，則從根物件開始。

```move file=packages/samples/sources/programmability/display.move anchor=nested
```

上述 `LittlePony` 類型的 Display 可以定義如下：

```json
{
  "name": "Just a pony",
  "image_url": "{image_url}",
  "description": "{metadata.description}"
}
```

## 多個 Display 物件

對於特定的類型 `T`，可以建立的 `Display<T>` 物件數量沒有限制。然而，全節點將使用最近更新的 `Display<T>`。

## 延伸閱讀

- [Sui 物件顯示 (Sui Object Display)](https://docs.sui.io/standards/display) 官方文件
- [發佈者 (Publisher)](./publisher) —— 創作者的代表
