---
description: 如何在 Move 中使用行註解、區塊註解與文件註解來撰寫文件及註解原始碼。
title: 註解 (Comments)
keywords:
  - Move
  - Sui
  - Move tutorial
  - comments
questions:
  - What is Comments in Move?
  - How do I use Comments in Move?
  - What is Line Comment in Move?
  - What is Block Comment in Move?
answer: How to use line comments, block comments, and doc comments in Move for documentation and code annotation.
goal:
  description: Reader understands use line comments, block comments, and doc comments in Move for documentation and code annotation
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

# 註解 (Comments) {#comments}

註解可用來新增備註或記錄你的程式碼。編譯器會忽略註解，且不會產生 Move 位元組碼。你可以使用註解說明程式碼的作用、為自己或其他開發者新增備註、暫時移除部分程式碼，或產生文件。Move 中有三種註解：單行註解、區塊註解與文件註解。

## 單行註解 (Line Comment) {#line-comment}

你可以使用雙斜線 `//` 註解該行其餘內容。`//` 之後的所有內容都會被編譯器忽略。

```move file=packages/samples/sources/move-basics/comments-line.move anchor=main

```

## 區塊註解 (Block Comment) {#block-comment}

區塊註解用於註解一個程式碼區塊。它們以 `/*` 開始，並以 `*/` 結束。`/*` 與 `*/` 之間的所有內容都會被編譯器忽略。你可以使用區塊註解註解單行或多行內容，甚至可以用它們註解一行中的部分內容。

```move file=packages/samples/sources/move-basics/comments-block.move anchor=main

```

這個範例有些極端，但它展示了使用區塊註解的所有方式。

## 文件註解 (Doc Comment) {#doc-comment}

文件註解是用來為你的程式碼產生文件的特殊註解。它們類似單行註解，但以三個斜線 `///` 開始，並放置於所記錄項目的定義之前，例如模組、結構、函式或常數。

```move file=packages/samples/sources/move-basics/comments-doc.move anchor=main

```

文件工具會將公開成員的文件註解收集到參考頁面中；本書各處連結的[標準函式庫與框架文件](https://docs.sui.io/references/framework)正是以這種方式產生。撰寫良好的文件註解會說明函式的作用，以及它會在何種條件下中止。

## 空白字元 (Whitespace) {#whitespace}

與某些語言不同，空白字元（空格、定位字元與換行）不會影響程式的含義。
