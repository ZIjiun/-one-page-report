# Icons

Icons help the reader sort categories before reading the words. Used badly they are noise and
make the page look machine-made.

## Evidence

- Nielsen Norman Group, "Icon Usability" (Aurora Harley, 2014): very few icons are universal
  (home, print, search); **always show a text label**; keep one meaning per icon across the
  product; the **5-second rule**: if you need more than about five seconds to think of an icon
  for a concept, it will not communicate it; keep shapes simple.
- Borkin, Bylinskii et al., "Beyond Memorability: Visualization Recognition and Recall"
  (IEEE InfoVis 2015): pictograms used well do not hurt memorability and can improve recall;
  titles that state the takeaway matter most.
- No emoji (they render differently on each system) and no brand logos **as icons** (trademarks):
  these two are house rules, not research findings. A product's own logo in the header, supplied
  by the user, is imagery, not an icon (`references/imagery.md`).

## Decision steps

1. **Is this a place where the reader sorts categories quickly, or a node in a diagram?** Zone
   tabs, card tags, category labels, list items, platform or role rows, timeline events, and the
   nodes of a diagram (the house in "can you charge at home?", the car on a route, the battery in
   a calculation). If it is a title, a big number or body text: **no icon**.
2. **5-second rule.** No obvious icon within about five seconds → no icon.
3. **Pick from the table below** (Lucide names; all bundled in `assets/icons.json`). Add new pairs to the
   table in your reply if you use one not listed.
4. **One concept = one icon, across the whole page.** If "problem" is a warning triangle, nothing
   else uses the warning triangle.
5. **Always with text.** Icons never carry meaning alone.
6. If an icon needs a moment of thought (e.g. "swords" for a fantasy game), list it as a design
   choice for the user (core rule 2).

## Concept → icon (Lucide)

| Concept (zh / en) | Icon |
|---|---|
| 成果 results | `trophy` |
| 問題 issues | `triangle-alert` |
| 做法 how / what we did | `wrench` |
| 下一步 next | `flag` |
| 時程 timeline | `calendar-days` |
| 狀態 status | `activity` |
| 風險 risk | `shield-alert` |
| 需要支援 support needed | `life-buoy` |
| 決策、請您決定 the ask | `scale` |
| 方案 options | `git-branch` |
| 建議 recommendation | `thumbs-up` |
| 效益 benefit | `trending-up` |
| 成本 cost | `dollar-sign` |
| 預算 budget | `wallet` |
| 目標 goal | `target` |
| 品質 quality | `star` |
| 人氣、使用者 users, reach | `users` |
| 生態、整合 ecosystem, integration | `puzzle` |
| 客戶 customer | `user` |
| 團隊、人力 team, headcount | `users-round` |
| 營收 revenue | `banknote` |
| 時間、效率 time, speed | `clock` |
| 安全 security | `shield-check` |
| 系統、伺服器 system | `server` |
| 資料 data | `database` |
| 文件 document | `file-text` |
| 會議、溝通 meeting, communication | `messages-square` |
| 訓練 training | `graduation-cap` |
| 上線、發布 launch | `rocket` |
| 公布 announcement | `megaphone` |
| 修正 fix, patch | `bandage` |
| 錯誤 bug | `bug` |
| 下載、更新 download, update | `download` |
| 價格、折扣 price, discount | `tag` |
| 新產品、新內容 new package | `package-plus` |
| 畫面、視覺 visuals | `sun` |
| 玩法、遊戲 gameplay | `gamepad-2` |
| 介面 UI | `layout-dashboard` |
| 技術 tech | `cpu` |
| 電腦 PC | `monitor` |
| 主機、電視 console, TV | `tv` |
| 掌機、平板 handheld | `tablet` |
| 手機 phone | `smartphone` |
| 已完成 done | `circle-check` |
| 進行中 in progress | `hourglass` |
| 延遲 late | `clock` (+ red text) |
| 想法 idea | `lightbulb` |
| 流程 process | `workflow` |

## Placement in the spec

- Zone tab: `"icon": "trophy"`.
- Card tag: `"icon": "star"`.
- Chip row / table row / issue / timeline event: `"icon": "..."`.
- Inside any text: `{{icon:name}}` (use sparingly).
