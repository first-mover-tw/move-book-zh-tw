// doc_ids 的差分測試 oracle：拿**上游自己的程式碼**算出一份 sidebar.yml 的
// doc id 集合，讓 `scripts/zh_tw/sidebar.py::doc_ids` 去對照。
//
// 為什麼需要這個：doc_ids 的判準連續四輪被外部 review 改（R6 太窄 → R7 太寬
// → R8 太窄 → R9 撞鍵），每一輪都是拿語料樣本反推語法規格（L20）。震盪的
// 根因是判定權在我手上；這裡把判定權交還給真正的消費者。
//
// 消費鏈與 docusaurus 官方文件**不同**，必須逐段照抄：
//   book/sidebar.yml → site/src/plugins/yaml-sidebar.ts::loadSidebarsFromYaml
//     （這一層會把沒有 type 的 mapping 補成 type: 'doc'）
//   → @docusaurus/plugin-content-docs normalizeSidebars → collectSidebarsDocIds
//
// 用法：node sidebar_doc_ids.mjs <sidebar.yml>  → stdout 一行一個 doc id。
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const siteDir = path.resolve(import.meta.dirname, '../../site');
const require = createRequire(pathToFileURL(path.join(siteDir, 'noop.cjs')));

// pnpm 的 node_modules 是嚴格樹：plugin-content-docs 不是 site 的直接依賴
// （經由 preset-classic 帶進來），從 site/ 解析不到 —— 先解析 preset-classic
// 的入口，再以它為根解析。套件的 exports 只開 `./lib/*`，所以走 lib 路徑，
// 不要 require package.json（會 ERR_PACKAGE_PATH_NOT_EXPORTED）。
const presetRequire = createRequire(require.resolve('@docusaurus/preset-classic'));
const { normalizeSidebars } = presetRequire(
  '@docusaurus/plugin-content-docs/lib/sidebars/normalization.js',
);
const { collectSidebarsDocIds, transformSidebarItems } = presetRequire(
  '@docusaurus/plugin-content-docs/lib/sidebars/utils.js',
);
// index.js 的順序是 normalizeSidebars → validateSidebars → …，validate 這一步
// 不能省：少了它，`{label: [...]}` 這種缺 id 的條目會一路走到
// collectSidebarDocIds 而吐出字面上的 `undefined`，oracle 就變成在替一個
// build 不起來的 sidebar 編造答案。
const { validateSidebars } = presetRequire(
  '@docusaurus/plugin-content-docs/lib/sidebars/validation.js',
);
const YAML = require('yaml');

// site/src/plugins/yaml-sidebar.ts::processSidebar 的逐行等價物。原檔是 TS
// 且被 docusaurus 的 build 管線編譯，這裡不引入 TS 工具鏈；改動上游那個檔
// 時這份也要跟著改 —— test_sidebar.py 有一條測試釘住它的 sha256。
function processSidebar(sidebar, parentIndex, parentEnumerate = true) {
  let index = 0;
  return sidebar.map((item) => {
    if (typeof item === 'string') return item;
    // 原檔是寬鬆比較 `==`，這裡照抄不改成 `===`：`enumerate: 0` 之類的
    // 值在兩者下結果相反，抄本一旦「順手修正」就不再是抄本。
    // eslint-disable-next-line eqeqeq
    const enumerate = (item.enumerate == false ? false : true) && parentEnumerate;
    if ('enumerate' in item) delete item.enumerate;
    if (item.type === undefined) item.type = 'doc';
    if (enumerate && item.type === 'category' && item.label && item.link) {
      index++;
      item.label = `${parentIndex ? `${parentIndex}.` : ''}${index}. ${item.label}`;
    }
    if (item.type === 'category' && item.items) {
      item.items = processSidebar(item.items, index, enumerate);
    }
    if (enumerate && item.type === 'doc' && item.label) {
      index++;
      item.label = `${parentIndex ? `${parentIndex}.` : ''}${index}. ${item.label}`;
    }
    return item;
  });
}

const parsed = YAML.parse(fs.readFileSync(process.argv[2], 'utf8'));
const sidebars = {};
for (const [key, value] of Object.entries(parsed)) sidebars[key] = processSidebar(value);
const normalized = normalizeSidebars(sidebars);
validateSidebars(normalized);

// 要問的是「哪些 id **必須**解析得到一份 doc」，不是 collectSidebarDocIds
// 字面上收了誰。`collectSidebarDocIds` 漏掉 `type: ref`，但 props.js 的
// normalizeItem 對 'doc' 與 'ref' 走同一條 convertDocLink → getDocById，
// 而 getDocById 對不存在的 id 直接 throw（props.js:33-45, 83-89）——
// dangling ref 一樣掛 build，只是比 checkSidebarsDocIds 晚一階。
//
// 所以先用上游自己的 transformSidebarItems 把 ref 改寫成 doc，再交給上游
// 自己的 collectSidebarDocIds。順序仍然由上游決定，這裡不自己走訪。
const refsAsDocs = Object.fromEntries(
  Object.entries(normalized).map(([name, items]) => [
    name,
    transformSidebarItems(items, (item) =>
      item.type === 'ref' ? { ...item, type: 'doc' } : item,
    ),
  ]),
);
const byName = collectSidebarsDocIds(refsAsDocs);
for (const ids of Object.values(byName)) for (const id of ids) console.log(id);
