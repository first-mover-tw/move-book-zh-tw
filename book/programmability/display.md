---
description: Sui 中的物件顯示 (Object Display)：使用顯示登錄 (Display Registry) 為你的物件定義中繼資料範本，並將顯示 (Display) 從 V1 遷移至 V2。
title: 物件顯示 (Object Display)
keywords:
  - Move
  - Sui
  - Move tutorial
  - object
  - display
  - object model
questions:
  - What is Object Display in Move?
  - How do I use Object Display in Move?
  - What is Background in Move?
answer: 'Object Display in Sui: define metadata templates for your objects with the Display Registry, and migrate Display from V1 to V2.'
goal:
  description: 'Reader understands object Display in Sui: define metadata templates for your objects with the Display Registry, and migrate Display from V1 to V2'
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

# 物件顯示 (Object Display) {#object-display}

Sui 上的物件在其結構與行為上皆明確定義，因此能以易於理解的方式顯示。不過，為了支援提供給用戶端的更豐富中繼資料，系統提供了一種標準且有效率的「描述」方式：註冊於 [Sui Framework](./sui-framework) 定義之系統 _Display Registry_ 中的 `Display` 物件。

## 背景 (Background) {#background}

過去曾嘗試針對可在使用者介面中顯示的物件，協議出一套標準結構。其中一種作法是在物件 struct 中定義特定欄位；存在這些欄位時，UI 便會使用它們。此作法不夠靈活，要求開發者在每個物件中定義相同欄位，而有時這些欄位對物件而言並不合理。

```move file=packages/samples/sources/programmability/display.move anchor=background

```

若任何欄位包含靜態資料，這些資料便會在每個物件中重複。而且，由於 Move 沒有介面，若不「手動」檢查物件型別，便無法得知物件是否具有特定欄位，使得用戶端擷取作業更為複雜。

## 物件顯示 (Object Display) {#object-display-1}

為解決這些問題，Sui 導入以標準方式描述供顯示用的物件。不再於物件 struct 中定義欄位，而是將顯示中繼資料儲存在與型別 `T` 關聯的獨立物件 `Display<T>` 中。如此一來，顯示中繼資料不會重複，也容易擴充與維護。

Sui Display 的另一項重要功能，是能夠定義範本，並在範本中使用物件欄位。這不僅能提供更靈活的顯示方式，也讓開發者不必在每個物件中定義名稱與型別完全相同的欄位。

> Object Display 受到 [Sui Full Node](https://docs.sui.io/operators/full-node/sui-full-node) 的原生支援；若物件型別關聯了 Display，用戶端即可擷取任何物件的顯示中繼資料。

## 顯示登錄表 (Display Registry) {#display-registry}

每個型別 `T` 恰有一個 `Display<T>`，且位於可預測的地址。這兩項特性皆來自 _Display Registry_：位於保留地址 `0xd` 的系統共享物件（請參閱 [Reserved Addresses](./../appendix/reserved-addresses)）。建立 display 時，其物件 ID 會從登錄表的 `UID` 與型別 `T` [衍生](https://docs.sui.io/references/framework/sui_sui/derived_object)。因此，任何人——包括 RPC 與其他用戶端——都能離線計算 `Display<T>` 的 ID，並直接擷取它，無須掃描事件或查詢歷史資料。

```move
module sui::display_registry;

/// display 的根節點，用於衍生地址。
/// 地址由系統在 `0xd` 產生。
public struct DisplayRegistry has key { id: UID }

/// 保存型別 `T` 的顯示值。
public struct Display<phantom T> has key {
    id: UID,
    /// 指定 display 物件的所有 (key,value) 項目。
    fields: VecMap<String, String>,
    /// 管理此 display 的 `DisplayCap` ID。已遷移的 V1
    /// display 在取得 capability 前為 `None`。
    cap_id: Option<ID>,
}

/// 用於管理 display 的 capability 物件。
public struct DisplayCap<phantom T> has key, store { id: UID }
```

`Display<T>` 物件本身為 _shared_，其權限則由另一個受擁有的物件——`DisplayCap<T>` [capability](./capability)——表示。capability 持有者可隨時對顯示欄位執行 `set`、`unset` 或 `clear`，而這些變更會全域套用，無須更新每個物件。capability 可以轉移給其他帳戶，或內建至具有自訂中繼資料管理功能的應用程式。

## 建立顯示項目 (Creating a Display) {#creating-a-display}

新的 `Display` 透過兩個函式之一建立；兩者皆接受 `DisplayRegistry` 的可變參考，並回傳 `Display<T>` 及其 `DisplayCap<T>`：

- `display_registry::new<T>` - 接受 [Internal Permit](./../move-basics/internal-permit)，因此只能從定義 `T` 的模組中呼叫；
- `display_registry::new_with_publisher<T>` - 接受 [Publisher](./publisher) 物件，適用於在定義模組外建立 display 的情況。

由於登錄表是共享物件，無法在[模組初始化函式](./module-initializer)中存取；display 會在套件發布後，透過獨立的一次性呼叫立即建立：

```move file=packages/samples/sources/programmability/display.move anchor=hero

```

`set` 呼叫會定義範本欄位，而 `share` 會藉由共享 `Display` 物件完成建立流程；接著，`DisplayCap` 會轉移給發布者，供其日後更新欄位。請注意，此函式定義為 `entry` 而非 `public`：一次性設定函式最好不要納入套件的公開 API，以便後續升級時移除它——[升級相容性規則](https://docs.sui.io/develop/publish-upgrade-packages/upgrade)會凍結 `public` 函式簽章，但不會凍結 `entry` 函式簽章。

## 標準欄位 (Standard Fields) {#standard-fields}

最廣泛支援的欄位如下：

- `name` - 物件名稱。使用者檢視物件時會顯示此名稱。
- `description` - 物件說明。使用者檢視物件時會顯示此說明。
- `link` - 應用程式中可使用的物件連結。
- `image_url` - 物件圖片的 URL 或 blob。
- `thumbnail_url` - 用於錢包、瀏覽器及其他產品作為預覽的小型圖片 URL。
- `project_url` - 與物件或建立者關聯的網站連結。
- `creator` - 指出物件建立者的字串。

> 如需最新的支援欄位清單，請參閱 [Sui Documentation](https://docs.sui.io/develop/objects/display)。

雖然有一組標準欄位，Display 物件並不強制要求使用它們。開發者可以定義所需的任何欄位，而用戶端可依其需求使用這些欄位。有些應用程式可能需要額外欄位，並省略其他欄位；Display 足夠靈活，能夠支援這些情況。

## 範本語法 (Template Syntax) {#template-syntax}

Display 中的每個值都是 _format string_，亦即由字面文字與以 `{`、`}` 分隔的運算式組成。最簡單的運算式是欄位路徑：`{path}` 會替換為該路徑欄位的值；路徑是從正在顯示的物件開始，由點分隔的欄位名稱清單。若要輸出字面的大括號，請將其加倍：`{{` 會變成 `{`。

```move file=packages/samples/sources/programmability/display.move anchor=nested

```

上方型別 `LittlePony` 的 Display 可定義如下：

```json
{
  "name": "Just a pony",
  "image_url": "{image_url}",
  "description": "{metadata.description}"
}
```

欄位路徑僅是最基本的運算式。完整形式包含三個部分：走訪資料的 _chain_、以 `|` 分隔的選用 _fallbacks_ 清單，以及以 `:` 為前綴、用來控制值如何轉譯的選用 _transform_：

```text
{ chain | fallback | ... : transform }
```

以下各節說明此語法中最常出現的部分。如需完整語法——字面值、struct 與 enum 值、衍生物件存取，以及完整的 transform 清單——請參閱 [Object Display Syntax](https://docs.sui.io/references/object-display-syntax) 參考資料。

### 向量與映射索引 (Vector and Map Indexing) {#vector-and-map-indexing}

chain 可使用方括號索引 `vector` 或 `VecMap`。數值索引一律帶有型別後綴，例如 `0u64` 而非 `0`；也可以使用另一個欄位的值作為索引：

```text
{items[0u64]}           `items` vector 的第一個元素
{items[idx]}            使用 `idx` 欄位的值作為索引
{scores[6u32]}          在 VecMap 中查詢鍵 `6u32`，並回傳其值
```

### 動態欄位存取 (Dynamic Field Access) {#dynamic-field-access}

範本可存取物件本身欄位以外的資料，並從儲存空間載入[動態欄位](./dynamic-fields)。`->` 運算子會載入動態欄位，`=>` 會載入[動態物件欄位](./dynamic-object-fields)，而鍵放在方括號中：

```text
{parent->['color']}     字串鍵 'color' 的動態欄位
{parent->['color'].x}   讀取已載入值上的欄位 `x`
{parent=>['hat']}       動態物件欄位（值為完整物件）
```

由於每次載入都會從儲存空間讀取資料，因此會受到預算限制：範本預設最多可執行 8 次物件載入，`->` 的成本為一次，`=>` 的成本為兩次。

### 轉譯 (Transforms) {#transforms}

預設會將值轉譯為人類可讀的字串。`:` 後的 transform 可改變此行為，適用於非純文字的值，例如位元組向量或時間戳記：

| Transform          | 效果                                                |
| ------------------ | --------------------------------------------------- |
| `str` _(default)_  | 人類可讀字串；`String` 與 `vector<u8>` 使用 UTF-8。 |
| `hex`              | 小寫、補零的十六進位格式。                          |
| `base64`           | Base64 編碼的位元組；接受 `url` 與 `nopad` 修飾詞。 |
| `bcs`              | BCS 序列化值後再進行 Base64 編碼，適用於聚合型別。  |
| `json`             | 結構化 JSON 值；僅限其為完整 format string 時使用。 |
| `timestamp` (`ts`) | 讀取為 Unix 毫秒的數值，並格式化為 ISO 8601。       |
| `url`              | 類似 `str`，但會對保留的 URL 字元進行百分比編碼。   |

```text
{amount:hex}                    將 `amount` 轉譯為十六進位
{created_at:ts}                 "2023-04-12T17:00:00Z"
{metadata:json}                 將整個 struct 輸出為 JSON
```

### 備援值 (Fallbacks) {#fallbacks}

若 chain 評估為 null——欄位缺失、索引超出範圍，或為 `None` [Option](./../move-basics/option)——便會嘗試 `|` 後的下一個 chain。以單引號包圍的字串字面值可作為方便的預設值：

```text
{display_name | name | 'Anonymous'}
```

若每個替代項目皆為 null，整個 format string 便會評估為 null，且該欄位會從結果中省略。

## 從 V1 遷移至 V2 (Migrating from V1 to V2) {#migrating-from-v1-to-v2}

本頁所述、由登錄表支援的 Display 是此標準的第二版：_Display V2_。原始版本 V1 實作於 `sui::display` 模組，早於登錄表出現：V1 `Display<T>` 物件是受擁有而非共享的物件，只能使用 `Publisher` 物件建立，並透過事件發現。同一型別可以存在任意數量的 V1 display，而完整節點會使用最近更新的一個。V2 以從登錄表衍生的方式取代基於事件的發現機制，並將「任意數量的 display」縮減為每種型別恰好一個。

現有 V1 display 已由系統遷移自動移轉至 V2：對每個具有 V1 display 的型別，系統已有一個欄位相同、且 `cap_id` 設為 `none` 的共享 `Display<T>`。若要管理此類 display，建立者可透過下列兩種方式之一取得其 `DisplayCap`：

- `claim` - 將舊版 V1 `Display` 物件作為型別權限的證明並消耗它，同時將其銷毀；
- `claim_with_publisher` - 改用 [Publisher](./publisher) 物件；剩餘的 V1 物件之後可透過 `delete_legacy` 銷毀。

```move file=packages/samples/sources/programmability/display.move anchor=migrate

```

若 V1 display 是在系統遷移完成後建立，`display_registry::migrate_v1_to_v2` 函式會直接執行遷移：建立 V2 `Display`、從舊版物件複製欄位、銷毀舊版物件，並回傳新 display 及其 capability。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Object Display](https://docs.sui.io/develop/objects/display) 於 Sui Documentation
- [Object Display Syntax](https://docs.sui.io/references/object-display-syntax) - 完整的範本語言參考資料
- [Publisher](./publisher) - 建立者的表示方式
- [Internal Permit](./../move-basics/internal-permit) - 用於建立 display 的授權
