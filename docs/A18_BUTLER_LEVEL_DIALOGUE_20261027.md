# A18 執事の挨拶バリエーション・館レベル連動（2026-10-27）

## 監修指示
- 執事に話しかけた直後の挨拶を増やす。
- 将来の拡張を容易にするため、現在の館レベルに応じて挨拶候補を切り替える。
- 挨拶の次に表示する用件メニューでは、直前に呼んだプレイヤー名を繰り返さない。

## 実装
- `layout-test/staff-flow.js`: `BUTLER_GREETINGS_BY_LEVEL` にLv.1〜6の候補を定義。Lv.1は8種類、Lv.2〜6は各3種類。既存の直前候補の連続回避を各レベル内で使用する。未定義レベルは明示エラー `E_BUTLER_GREETING_LEVEL`、他レベルの挨拶を暗黙に流用しない。
- `layout-test/index.html`: 実セーブの `progression.unlockedThroughLevel` に基づく `unlockedRooms()` を会話側へ渡す。スクリプトURLを更新してブラウザキャッシュによる旧セリフを回避。
- メニュー側は「お呼びでございますか。何なりとお申し付けください。」とし、名前を省略。最初の挨拶・写真のお渡し・初回チュートリアルの呼称は維持。
- 女性の「名前お嬢様」と男性の「名前様」の区別を維持。女性スタッフの会話は変更しない。
- Lv.2〜6の挨拶は現行のレベル到達を参照する仕組みとして先行登録。未実装のレベル別短編演出や画像素材の採用を意味しない。

## QA
- `docs/qa/test_butler_level_dialogue.py` / `butler_level_dialogue_qa.json`: 隔離ChromeにてLv.1の全8種類、Lv.2〜6の切替、メニュー・戻る、敬称、女性スタッフの非回帰、未定義レベルエラーを検証：50/50 PASS。
- `docs/qa/test_first_artwork_tutorial.py`: 実プロフィール・写真保存・展示・再起動の後の実ゲーム呼出しでも挨拶→名前なしメニューを検証：55/55 PASS。
- `docs/qa/test_opening_v1.py`: 21/21 PASS。
- `docs/qa/test_opening_framed_transitions.py`: 43/43 PASS。
- iPhone Safariでの表示確認は未実施。GitHub Pagesへの公開は別ゲートとし、事前承認と本番反映確認を要する。
