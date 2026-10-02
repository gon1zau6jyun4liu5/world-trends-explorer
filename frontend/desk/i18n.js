'use strict';
window.I18n = (() => {
 const messages = {
  "Google이 빈 목록을 반환했습니다. 이전에 받은 화제를 표시합니다.": ["Google이 빈 목록을 반환했습니다. 이전에 받은 화제를 표시합니다.", "Googleから空の一覧が返されました。以前取得した話題を表示します。", "Google returned an empty list. Showing previously received stories."],
  "낮·밤 표시: 켜짐": ["낮·밤 표시: 켜짐", "昼夜表示: オン", "Day/night: on"],
  "낮·밤 표시: 꺼짐": ["낮·밤 표시: 꺼짐", "昼夜表示: オフ", "Day/night: off"],
  "국가 목록 펼치기": ["국가 목록 펼치기", "国の一覧を開く", "Show country list"],
  "국가 목록 접기": ["국가 목록 접기", "国の一覧を閉じる", "Hide country list"],
  "설정": [
    "설정",
    "設定",
    "Settings"
  ],
  "화면 언어": [
    "화면 언어",
    "表示言語",
    "Display language"
  ],
  "세상의 관심을 읽는 창": [
    "세상의 관심을 읽는 창",
    "世界の関心を知る窓",
    "A window into the world"
  ],
  "World Trends 홈": [
    "World Trends 홈",
    "World Trends ホーム",
    "World Trends home"
  ],
  "주 메뉴": [
    "주 메뉴",
    "メインメニュー",
    "Main navigation"
  ],
  "세계의 화제": [
    "세계의 화제",
    "世界の話題",
    "World trends"
  ],
  "저장한 화제": [
    "저장한 화제",
    "保存した話題",
    "Saved stories"
  ],
  "내 앱 ↗": [
    "내 앱 ↗",
    "マイアプリ ↗",
    "My apps ↗"
  ],
  "지금, 세계의": [
    "지금, 세계의",
    "今、世界の",
    "What the world"
  ],
  "관심은.": [
    "관심은.",
    "関心は。",
    "is talking about."
  ],
  "나라별로 달라지는 화제, 그 뒤에 있는 이야기를 만나보세요.": [
    "나라별로 달라지는 화제, 그 뒤에 있는 이야기를 만나보세요.",
    "国ごとの話題と、その背景にあるニュースを見てみましょう。",
    "Explore what is trending in each country and the stories behind it."
  ],
  "검색 화제 + 현지 뉴스": [
    "검색 화제 + 현지 뉴스",
    "検索トレンド ＋ 現地ニュース",
    "Search trends + local news"
  ],
  "열어 둔 동안 10분마다 확인": [
    "열어 둔 동안 10분마다 확인",
    "開いている間は10分ごとに更新",
    "Checks every 10 minutes while open"
  ],
  "탐색 도구": [
    "탐색 도구",
    "閲覧ツール",
    "Explore tools"
  ],
  "전세계": [
    "전세계",
    "世界全体",
    "Worldwide"
  ],
  "내 국가": [
    "내 국가",
    "マイカントリー",
    "My countries"
  ],
  "아시아": [
    "아시아",
    "アジア",
    "Asia"
  ],
  "유럽": [
    "유럽",
    "ヨーロッパ",
    "Europe"
  ],
  "아메리카": [
    "아메리카",
    "アメリカ",
    "Americas"
  ],
  "오세아니아": [
    "오세아니아",
    "オセアニア",
    "Oceania"
  ],
  "아프리카": [
    "아프리카",
    "アフリカ",
    "Africa"
  ],
  "남극": [
    "남극",
    "南極",
    "Antarctica"
  ],
  "◎ 지구본 접기": [
    "◎ 지구본 접기",
    "◎ 地球儀を閉じる",
    "◎ Hide globe"
  ],
  "◎ 지구본 보기": [
    "◎ 지구본 보기",
    "◎ 地球儀を表示",
    "◎ Show globe"
  ],
  "＋ 관심 국가": [
    "＋ 관심 국가",
    "＋ 国を選ぶ",
    "＋ Choose countries"
  ],
  "↻ 새로고침": [
    "↻ 새로고침",
    "↻ 更新",
    "↻ Refresh"
  ],
  "새 소식 확인": [
    "새 소식 확인",
    "最新情報を確認",
    "Check for updates"
  ],
  "지구본에서 국가 선택": [
    "지구본에서 국가 선택",
    "地球儀で国を選択",
    "Select a country on the globe"
  ],
  "지금, 지구 반대편은": [
    "지금, 지구 반대편은",
    "今、地球の反対側では",
    "Right now, across the globe"
  ],
  "드래그로 지구를 돌려보세요. 나라에 마우스를 올리면 이름이, 선택하면 화제가 나타납니다.": [
    "드래그로 지구를 돌려보세요. 나라에 마우스를 올리면 이름이, 선택하면 화제가 나타납니다.",
    "ドラッグで地球を回せます。国にカーソルを合わせると国名、選ぶと話題を表示します。",
    "Drag to rotate. Hover for a country name; select it to see its stories."
  ],
  "지도 닫기": [
    "지도 닫기",
    "地図を閉じる",
    "Close map"
  ],
  "접기 ×": [
    "접기 ×",
    "閉じる ×",
    "Collapse ×"
  ],
  "▷ 자동 회전": [
    "▷ 자동 회전",
    "▷ 自動回転",
    "▷ Auto rotate"
  ],
  "Ⅱ 회전 멈춤": [
    "Ⅱ 회전 멈춤",
    "Ⅱ 回転を停止",
    "Ⅱ Pause rotation"
  ],
  "☀ 낮쪽 보기": [
    "☀ 낮쪽 보기",
    "☀ 昼の地域",
    "☀ Day side"
  ],
  "☾ 밤쪽 보기": [
    "☾ 밤쪽 보기",
    "☾ 夜の地域",
    "☾ Night side"
  ],
  "처음 위치": [
    "처음 위치",
    "最初の位置",
    "Reset view"
  ],
  "도시 시각 표시": [
    "도시 시각 표시",
    "都市の時刻を表示",
    "Show city times"
  ],
  "지구본을 불러오는 중…": [
    "지구본을 불러오는 중…",
    "地球儀を読み込み中…",
    "Loading the globe…"
  ],
  "회전 가능한 지구본": [
    "회전 가능한 지구본",
    "回転できる地球儀",
    "Interactive globe"
  ],
  "지구본 이동": [
    "지구본 이동",
    "地球儀の操作",
    "Globe navigation"
  ],
  "지구본 왼쪽으로 회전": [
    "지구본 왼쪽으로 회전",
    "地球儀を左に回転",
    "Rotate globe left"
  ],
  "지구본 위로 회전": [
    "지구본 위로 회전",
    "地球儀を上に回転",
    "Rotate globe up"
  ],
  "지구본 아래로 회전": [
    "지구본 아래로 회전",
    "地球儀を下に回転",
    "Rotate globe down"
  ],
  "지구본 오른쪽으로 회전": [
    "지구본 오른쪽으로 회전",
    "地球儀を右に回転",
    "Rotate globe right"
  ],
  "지구본 축소": [
    "지구본 축소",
    "地球儀を縮小",
    "Zoom out"
  ],
  "지구본 확대": [
    "지구본 확대",
    "地球儀を拡大",
    "Zoom in"
  ],
  "보이는 지역의 시각": [
    "보이는 지역의 시각",
    "表示地域の時刻",
    "Local times in view"
  ],
  "기준 시각": [
    "기준 시각",
    "基準時刻",
    "Reference time"
  ],
  "낮": [
    "낮",
    "昼",
    "Day"
  ],
  "밤": [
    "밤",
    "夜",
    "Night"
  ],
  "☀ 낮": [
    "☀ 낮",
    "☀ 昼",
    "☀ Day"
  ],
  "☾ 밤": [
    "☾ 밤",
    "☾ 夜",
    "☾ Night"
  ],
  "화제 조회 가능": [
    "화제 조회 가능",
    "話題を表示可能",
    "Stories available"
  ],
  "30초마다 시각 갱신 · 도시별 서머타임 반영": [
    "30초마다 시각 갱신 · 도시별 서머타임 반영",
    "30秒ごとに時刻更新・各都市の夏時間に対応",
    "Time updates every 30 seconds · Local daylight saving time"
  ],
  "낮·밤 경계는 현재 태양 위치의 근사치입니다. 시간대는 주요 도시 기준이며 국가 전체의 시간대 경계를 나타내지는 않습니다.": [
    "낮·밤 경계는 현재 태양 위치의 근사치입니다. 시간대는 주요 도시 기준이며 국가 전체의 시간대 경계를 나타내지는 않습니다.",
    "昼夜の境界は現在の太陽位置による概算です。時刻は主要都市のもので、国全体のタイムゾーン境界を示すものではありません。",
    "Day and night are approximate, based on the sun’s position. Times represent cities, not national time-zone boundaries."
  ],
  "내가 보는 나라": [
    "내가 보는 나라",
    "選択した国",
    "My countries"
  ],
  "소식을 준비하고 있습니다.": [
    "소식을 준비하고 있습니다.",
    "ニュースを準備しています。",
    "Preparing your stories."
  ],
  "국가별 화제": [
    "국가별 화제",
    "国ごとの話題",
    "Stories per country"
  ],
  "국가별 표시할 화제 수": [
    "국가별 표시할 화제 수",
    "国ごとの表示件数",
    "Number of stories per country"
  ],
  "1개": [
    "1개",
    "1件",
    "1"
  ],
  "3개": [
    "3개",
    "3件",
    "3"
  ],
  "5개": [
    "5개",
    "5件",
    "5"
  ],
  "10개": [
    "10개",
    "10件",
    "10"
  ],
  "전체": [
    "전체",
    "すべて",
    "All"
  ],
  "화제 없는 국가도 표시": [
    "화제 없는 국가도 표시",
    "話題のない国も表示",
    "Show countries without stories"
  ],
  "현재 목록에서 화제 찾기": [
    "현재 목록에서 화제 찾기",
    "現在の一覧から検索",
    "Search these stories"
  ],
  "Google RSS에 제공된 일부 급상승 검색어입니다. 전체 인기 순위가 아니며, 검색량은 근사치입니다.": [
    "Google RSS에 제공된 일부 급상승 검색어입니다. 전체 인기 순위가 아니며, 검색량은 근사치입니다.",
    "Google RSSによる急上昇検索語の一部です。総合ランキングではなく、検索数は概算です。",
    "Google RSS provides selected rising searches, not an overall popularity ranking. Search volumes are approximate."
  ],
  "현지 뉴스는 GDELT가 수집한 해당 국가 언론의 최근 24시간 보도로, 검색 인기 순위가 아닙니다. 국가를 선택해 조회하세요.": [
    "현지 뉴스는 GDELT가 수집한 해당 국가 언론의 최근 24시간 보도로, 검색 인기 순위가 아닙니다. 국가를 선택해 조회하세요.",
    "現地ニュースはGDELTが収集した過去24時間の現地メディア報道で、検索ランキングではありません。国を選んで取得します。",
    "Local news covers the past 24 hours of reporting by publishers in that country, collected by GDELT. Select a country to load it; this is not a search ranking."
  ],
  "원문 제목을 그대로 표시합니다. 관련 기사에서 한국어 번역을 열 수 있습니다.": [
    "원문 제목을 유지하며, 상세 화면에서 설정한 언어의 번역을 함께 표시합니다.",
    "見出しは原文で表示します。詳細で選択言語の翻訳を併記します。",
    "Original headlines are preserved. Open a story to see translations in your selected language."
  ],
  "데이터 안내 ↗": [
    "데이터 안내 ↗",
    "データについて ↗",
    "About the data ↗"
  ],
  "어느 나라가 궁금하세요?": [
    "어느 나라가 궁금하세요?",
    "どの国が気になりますか？",
    "Which countries interest you?"
  ],
  "닫기": [
    "닫기",
    "閉じる",
    "Close"
  ],
  "최대 8개국을 골라 한 화면에서 살펴보세요.": [
    "최대 8개국을 골라 한 화면에서 살펴보세요.",
    "最大8か国を選んで、ひとつの画面で見られます。",
    "Choose up to 8 countries to follow in one view."
  ],
  "선택한 국가와 저장한 화제는 연결된 기기에서 함께 사용합니다.": [
    "선택한 국가와 저장한 화제는 연결된 기기에서 함께 사용합니다.",
    "選択した国と保存した話題は接続端末で共有されます。",
    "Selected countries and saved stories are shared across your connected devices."
  ],
  "선택한 국가 보기": [
    "선택한 국가 보기",
    "選択した国を表示",
    "Show selected countries"
  ],
  "기사 상세 닫기": [
    "기사 상세 닫기",
    "記事の詳細を閉じる",
    "Close story details"
  ],
  "이 화제의 관련 기사": [
    "이 화제의 관련 기사",
    "この話題の関連記事",
    "Related articles"
  ],
  "다시 보고 싶은 이야기": [
    "다시 보고 싶은 이야기",
    "また読みたい話題",
    "Stories to revisit"
  ],
  "현지 뉴스 · GDELT": [
    "현지 뉴스 · GDELT",
    "現地ニュース · GDELT",
    "Local news · GDELT"
  ],
  "검색 화제 · Google": [
    "검색 화제 · Google",
    "検索トレンド · Google",
    "Search trends · Google"
  ],
  "관련 이미지 없음": [
    "관련 이미지 없음",
    "関連画像なし",
    "No related image"
  ],
  "관련 뉴스": [
    "관련 뉴스",
    "関連ニュース",
    "Related news"
  ],
  "저장 해제": [
    "저장 해제",
    "保存を解除",
    "Unsave"
  ],
  "저장": [
    "저장",
    "保存",
    "Save"
  ],
  "수신 지연": [
    "수신 지연",
    "取得が遅れています",
    "Delayed"
  ],
  "현재 화제 없음": [
    "현재 화제 없음",
    "現在の話題なし",
    "No stories right now"
  ],
  "선택 조회": [
    "선택 조회",
    "選択して取得",
    "Load on demand"
  ],
  "확인 중": [
    "확인 중",
    "確認中",
    "Checking"
  ],
  "현지 언론의 최근 24시간 보도입니다. 검색 인기 순위와 다릅니다.": [
    "현지 언론의 최근 24시간 보도입니다. 검색 인기 순위와 다릅니다.",
    "現地メディアによる過去24時間の報道です。検索ランキングではありません。",
    "Reporting by local publishers over the past 24 hours, not a search ranking."
  ],
  "현지 뉴스 불러오기": [
    "현지 뉴스 불러오기",
    "現地ニュースを取得",
    "Load local news"
  ],
  "아직 수신한 데이터가 없습니다": [
    "아직 수신한 데이터가 없습니다",
    "まだデータを取得していません",
    "No data received yet"
  ],
  "새로고침으로 다시 확인할 수 있습니다.": [
    "새로고침으로 다시 확인할 수 있습니다.",
    "更新して再確認できます。",
    "Refresh to try again."
  ],
  "일치하는 화제가 없습니다.": [
    "일치하는 화제가 없습니다.",
    "一致する話題がありません。",
    "No matching stories."
  ],
  "현재 제공된 화제가 없습니다.": [
    "현재 제공된 화제가 없습니다.",
    "現在提供されている話題はありません。",
    "No stories are currently available."
  ],
  "접기 ↑": [
    "접기 ↑",
    "折りたたむ ↑",
    "Show less ↑"
  ],
  "현지 보도 · 검색 순위 아님": [
    "현지 보도 · 검색 순위 아님",
    "現地報道・検索順位ではありません",
    "Local reporting · Not search rankings"
  ],
  "뉴스 다시 확인": [
    "뉴스 다시 확인",
    "ニュースを再確認",
    "Refresh news"
  ],
  "Google에서 더 보기 ↗": [
    "Google에서 더 보기 ↗",
    "Googleでもっと見る ↗",
    "More on Google ↗"
  ],
  "마음에 남는 화제를 모아두세요.": [
    "마음에 남는 화제를 모아두세요.",
    "気になる話題を保存しましょう。",
    "Keep the stories that interest you."
  ],
  "화제 옆의 ☆를 누르면 여기에 보관됩니다.": [
    "화제 옆의 ☆를 누르면 여기에 보관됩니다.",
    "話題の横にある☆を押すと、ここに保存されます。",
    "Select ☆ beside a story to save it here."
  ],
  "화제를 저장했습니다.": [
    "화제를 저장했습니다.",
    "話題を保存しました。",
    "Story saved."
  ],
  "저장을 해제했습니다.": [
    "저장을 해제했습니다.",
    "保存を解除しました。",
    "Story removed from saved."
  ],
  "★ 저장됨 · 해제하기": [
    "★ 저장됨 · 해제하기",
    "★ 保存済み・解除",
    "★ Saved · Remove"
  ],
  "☆ 이 화제 저장": [
    "☆ 이 화제 저장",
    "☆ この話題を保存",
    "☆ Save this story"
  ],
  "이 화제에 연결된 기사가 없습니다. 아래 검색을 이용해 주세요.": [
    "이 화제에 연결된 기사가 없습니다. 아래 검색을 이용해 주세요.",
    "関連記事がありません。下の検索をご利用ください。",
    "No articles are linked to this story. Try the searches below."
  ],
  "Google 검색 ↗": [
    "Google 검색 ↗",
    "Google 検索 ↗",
    "Search Google ↗"
  ],
  "뉴스 검색 ↗": [
    "뉴스 검색 ↗",
    "ニュース検索 ↗",
    "Search news ↗"
  ],
  "지구본을 불러오지 못했습니다. 아래 국가 버튼으로 탐색할 수 있습니다.": [
    "지구본을 불러오지 못했습니다. 아래 국가 버튼으로 탐색할 수 있습니다.",
    "地球儀を読み込めませんでした。下の国名ボタンをご利用ください。",
    "The globe could not load. Use the country buttons below."
  ],
  "새 소식을 확인합니다. 10분 이내에는 받은 목록을 재사용합니다.": [
    "새 소식을 확인합니다. 10분 이내에는 받은 목록을 재사용합니다.",
    "最新情報を確認します。取得から10分以内はキャッシュを使います。",
    "Checking for updates. Stories received in the last 10 minutes are reused."
  ],
  "화면을 준비하지 못했습니다. 페이지를 새로고침해 주세요.": [
    "화면을 준비하지 못했습니다. 페이지를 새로고침해 주세요.",
    "画面を準備できませんでした。再読み込みしてください。",
    "Could not load the page. Please refresh."
  ],
  "로그인이 만료되었습니다. 페이지를 새로고침해 주세요.": [
    "로그인이 만료되었습니다. 페이지를 새로고침해 주세요.",
    "ログインの有効期限が切れました。再読み込みしてください。",
    "Your session expired. Please refresh to sign in."
  ],
  "로그인이 필요합니다.": [
    "로그인이 필요합니다.",
    "ログインが必要です。",
    "Please sign in."
  ],
  "요청을 처리하지 못했습니다.": [
    "요청을 처리하지 못했습니다.",
    "リクエストを処理できませんでした。",
    "The request could not be completed."
  ],
  "현재 밤인 영역": [
    "현재 밤인 영역",
    "現在夜の地域",
    "Nighttime region"
  ],
  "태양 직하점": [
    "태양 직하점",
    "太陽直下点",
    "Subsolar point"
  ],
  "지구본을 돌리면 보이는 지역의 도시 시각이 나타납니다.": [
    "지구본을 돌리면 보이는 지역의 도시 시각이 나타납니다.",
    "地球儀を回すと、表示地域の都市時刻が見られます。",
    "Rotate the globe to see local city times."
  ],
  "회전 가능한 지구본. 방향키 또는 드래그로 회전하고 국가를 선택하세요.": [
    "회전 가능한 지구본. 방향키 또는 드래그로 회전하고 국가를 선택하세요.",
    "矢印キーまたはドラッグで回転して国を選べます。",
    "Use arrow keys or drag to rotate the globe and select a country."
  ],
  "화제가 있는 나라부터 불러오고 있습니다.": [
    "화제가 있는 나라부터 불러오고 있습니다.",
    "話題のある国から読み込んでいます。",
    "Loading countries with available stories."
  ],
  "현재 표시할 화제가 없습니다. ‘화제 없는 국가도 표시’를 켜면 수신 상태와 현지 뉴스 조회를 확인할 수 있습니다.": [
    "현재 표시할 화제가 없습니다. ‘화제 없는 국가도 표시’를 켜면 수신 상태와 현지 뉴스 조회를 확인할 수 있습니다.",
    "表示できる話題がありません。「話題のない国も表示」で取得状況や現地ニュースを確認できます。",
    "No stories to display. Enable “Show countries without stories” to see status and load local news."
  ],
  "Google이 요청을 일시 제한했습니다. 잠시 후 자동으로 다시 확인합니다.": [
    "Google이 요청을 일시 제한했습니다. 잠시 후 자동으로 다시 확인합니다.",
    "Googleがリクエストを一時制限しています。しばらくして自動で再確認します。",
    "Google is temporarily limiting requests. We will retry automatically."
  ],
  "다른 나라의 뉴스를 조회 중입니다. 잠시 후 다시 눌러 주세요.": [
    "다른 나라의 뉴스를 조회 중입니다. 잠시 후 다시 눌러 주세요.",
    "別の国のニュースを取得中です。少し待って再試行してください。",
    "Another country’s news is loading. Please try again shortly."
  ],
  "뉴스 제공처의 요청 간격 제한입니다. 잠시 후 다시 눌러 주세요.": [
    "뉴스 제공처의 요청 간격 제한입니다. 잠시 후 다시 눌러 주세요.",
    "ニュース提供元の間隔制限です。少し待って再試行してください。",
    "The news provider requires a pause between requests. Try again shortly."
  ],
  "현지 뉴스 제공처가 현재 요청을 제한하고 있습니다. 1분 후 다시 시도해 주세요.": [
    "현지 뉴스 제공처가 현재 요청을 제한하고 있습니다. 1분 후 다시 시도해 주세요.",
    "現地ニュースの提供元が制限中です。1分後に再試行してください。",
    "The local news provider is limiting requests. Try again in a minute."
  ],
  "최신 소식을 가져오지 못했습니다. 잠시 후 다시 확인해 주세요.": [
    "최신 소식을 가져오지 못했습니다. 잠시 후 다시 확인해 주세요.",
    "最新情報を取得できませんでした。しばらくして再試行してください。",
    "Could not load the latest stories. Please try again shortly."
  ],
  "이전에 받은 현지 뉴스입니다. 뉴스 다시 확인을 눌러 최신 보도를 조회하세요.": [
    "이전에 받은 현지 뉴스입니다. 뉴스 다시 확인을 눌러 최신 보도를 조회하세요.",
    "以前取得したニュースです。「ニュースを再確認」で最新の報道を取得できます。",
    "These are cached stories. Select Refresh news to check for newer reporting."
  ],
  "잠시 후 다시 확인해 주세요.": [
    "잠시 후 다시 확인해 주세요.",
    "しばらくして再試行してください。",
    "Please try again shortly."
  ],
  "페이지를 새로고침한 뒤 다시 시도하세요.": [
    "페이지를 새로고침한 뒤 다시 시도하세요.",
    "ページを再読み込みしてから再試行してください。",
    "Refresh the page and try again."
  ],
  "언어 설정을 저장했습니다.": [
    "언어 설정을 저장했습니다.",
    "言語設定を保存しました。",
    "Language preference saved."
  ],
  "화면 문구와 날짜에 적용하며, 연결된 기기에서도 유지됩니다.": [
    "화면 문구와 날짜에 적용하며, 연결된 기기에서도 유지됩니다.",
    "画面の文言と日付に適用され、接続端末でも維持されます。",
    "Applies to interface text and dates, and is saved across connected devices."
  ],
  "제목 번역": [
    "제목 번역",
    "見出しの翻訳",
    "Headline translations"
  ],
  "상세 모달을 열면 원문 아래에 선택한 언어의 기계 번역을 표시합니다.": [
    "상세 모달을 열면 원문 아래에 선택한 언어의 기계 번역을 표시합니다.",
    "詳細画面を開くと、原文の下に選択言語の機械翻訳を表示します。",
    "Open story details to see a machine translation below each original headline."
  ],
  "번역할 때 공개된 제목을 MyMemory에 전송합니다. 무료 서비스의 요청 한도가 있으며, 번역이 부정확하거나 일시적으로 제공되지 않을 수 있습니다.": [
    "번역할 때 공개된 제목을 MyMemory에 전송합니다. 무료 서비스의 요청 한도가 있으며, 번역이 부정확하거나 일시적으로 제공되지 않을 수 있습니다.",
    "翻訳時に公開見出しをMyMemoryへ送信します。無料サービスには利用制限があり、翻訳が不正確または一時的に利用できない場合があります。",
    "Public headlines are sent to MyMemory for translation. This free service has usage limits; translations may be inaccurate or temporarily unavailable."
  ],
  "원문과 번역을 함께 표시": [
    "원문과 번역을 함께 표시",
    "原文と翻訳を併記",
    "Original and translation side by side"
  ],
  "기계 번역 · MyMemory": [
    "기계 번역 · MyMemory",
    "機械翻訳 · MyMemory",
    "Machine translation · MyMemory"
  ],
  "번역 중…": [
    "번역 중…",
    "翻訳中…",
    "Translating…"
  ],
  "번역을 불러오지 못했습니다.": [
    "번역을 불러오지 못했습니다.",
    "翻訳を取得できませんでした。",
    "Translation is unavailable."
  ],
  "번역 다시 시도": [
    "번역 다시 시도",
    "翻訳を再試行",
    "Retry translation"
  ],
  "번역 열기 ↗": [
    "번역 열기 ↗",
    "翻訳を開く ↗",
    "Open translation ↗"
  ],
  "원문과 동일합니다.": [
    "원문과 동일합니다.",
    "原文と同じです。",
    "Same as the original."
  ],
  "한국어로 읽기 ↗": [
    "한국어로 읽기 ↗",
    "日本語で読む ↗",
    "Read in English ↗"
  ],
  "invalid_preferences": [
    "설정을 확인해 주세요.",
    "設定を確認してください。",
    "Please check your settings."
  ],
  "invalid_translation": [
    "번역할 내용을 확인해 주세요.",
    "翻訳する文章を確認してください。",
    "Please check the text to translate."
  ],
  "translation_unavailable": [
    "번역을 잠시 사용할 수 없습니다.",
    "翻訳を一時的に利用できません。",
    "Translation is temporarily unavailable."
  ],
  "stories": [
    "{n}개 화제",
    "{n}件の話題",
    "{n} stories"
  ],
  "regionTitle": [
    "{region}의 화제",
    "{region}の話題",
    "Stories in {region}"
  ],
  "savedSummary": [
    "저장한 화제 {n}개 · 기기 간 함께 보관됩니다",
    "保存した話題 {n}件・端末間で共有",
    "{n} saved stories · Shared across devices"
  ],
  "summary": [
    "화제 수신 {available}곳 / 탐색 {total}곳 · 국가별 {limit} · 제공된 화제 {count}개",
    "取得済み {available}か国 / {total}か国・国ごとに{limit}・話題 {count}件",
    "Stories from {available} / {total} countries · {limit} per country · {count} stories"
  ],
  "upTo": [
    "{n}개까지",
    "最大{n}件",
    "Up to {n}"
  ],
  "loadingSuffix": [
    " · 소식을 확인하는 중…",
    "・確認中…",
    " · Checking for updates…"
  ],
  "errorsSuffix": [
    " · 수신 지연 {n}곳",
    "・取得遅延 {n}か国",
    " · {n} countries delayed"
  ],
  "relatedLabel": [
    "{title} 관련 기사 보기",
    "{title}の関連記事を表示",
    "View articles about {title}"
  ],
  "imageSource": [
    "이미지: {source} · ",
    "画像: {source} · ",
    "Image: {source} · "
  ],
  "traffic": [
    "검색량 {n}",
    "検索数 {n}",
    "Searches {n}"
  ],
  "approxTraffic": [
    "근사 검색량 {n} · ",
    "推定検索数 {n} · ",
    "Approx. searches {n} · "
  ],
  "lastFetched": [
    "마지막 수신 {date}",
    "最終取得 {date}",
    "Last received {date}"
  ],
  "staleSuffix": [
    " · 마지막 수신 목록 표시",
    "・最後に取得した一覧を表示",
    " · Showing last received stories"
  ],
  "allStories": [
    "화제 {n}개 모두 보기 ↓",
    "話題{n}件をすべて表示 ↓",
    "Show all {n} stories ↓"
  ],
  "newsTime": [
    " · 수집 시각 · 검색 순위 아님",
    "・収集時刻・検索順位ではありません",
    " · Collection time · Not search rankings"
  ],
  "localSuffix": [
    " · 현지 뉴스",
    " · 現地ニュース",
    " · Local news"
  ],
  "countryCount": [
    "{n} / 8개국 선택",
    "{n} / 8か国を選択",
    "{n} / 8 countries selected"
  ],
  "pageTitle": [
    "World Trends · 지금 세계의 화제",
    "World Trends · 今、世界の話題",
    "World Trends · What’s trending now"
  ],
  "서울": [
    "서울",
    "ソウル",
    "Seoul"
  ],
  "도쿄": [
    "도쿄",
    "東京",
    "Tokyo"
  ],
  "뉴욕": [
    "뉴욕",
    "ニューヨーク",
    "New York"
  ],
  "로스앤젤레스": [
    "로스앤젤레스",
    "ロサンゼルス",
    "Los Angeles"
  ],
  "런던": [
    "런던",
    "ロンドン",
    "London"
  ],
  "파리": [
    "파리",
    "パリ",
    "Paris"
  ],
  "베를린": [
    "베를린",
    "ベルリン",
    "Berlin"
  ],
  "로마": [
    "로마",
    "ローマ",
    "Rome"
  ],
  "마드리드": [
    "마드리드",
    "マドリード",
    "Madrid"
  ],
  "타이베이": [
    "타이베이",
    "台北",
    "Taipei"
  ],
  "뉴델리": [
    "뉴델리",
    "ニューデリー",
    "New Delhi"
  ],
  "싱가포르": [
    "싱가포르",
    "シンガポール",
    "Singapore"
  ],
  "자카르타": [
    "자카르타",
    "ジャカルタ",
    "Jakarta"
  ],
  "시드니": [
    "시드니",
    "シドニー",
    "Sydney"
  ],
  "퍼스": [
    "퍼스",
    "パース",
    "Perth"
  ],
  "토론토": [
    "토론토",
    "トロント",
    "Toronto"
  ],
  "밴쿠버": [
    "밴쿠버",
    "バンクーバー",
    "Vancouver"
  ],
  "상파울루": [
    "상파울루",
    "サンパウロ",
    "São Paulo"
  ],
  "멕시코시티": [
    "멕시코시티",
    "メキシコシティ",
    "Mexico City"
  ],
  "부에노스아이레스": [
    "부에노스아이레스",
    "ブエノスアイレス",
    "Buenos Aires"
  ],
  "요하네스버그": [
    "요하네스버그",
    "ヨハネスブルグ",
    "Johannesburg"
  ],
  "베이징": [
    "베이징",
    "北京",
    "Beijing"
  ],
  "두바이": [
    "두바이",
    "ドバイ",
    "Dubai"
  ],
  "카이로": [
    "카이로",
    "カイロ",
    "Cairo"
  ],
  "모스크바": [
    "모스크바",
    "モスクワ",
    "Moscow"
  ],
  "오클랜드": [
    "오클랜드",
    "オークランド",
    "Auckland"
  ],
  "호놀룰루": [
    "호놀룰루",
    "ホノルル",
    "Honolulu"
  ],
  "앙카라": [
    "앙카라",
    "アンカラ",
    "Ankara"
  ],
  "북키프로스": [
    "북키프로스",
    "北キプロス",
    "Northern Cyprus"
  ],
  "소말릴란드": [
    "소말릴란드",
    "ソマリランド",
    "Somaliland"
  ]
};
 let language='ko';
 const staticNodes=[], staticAttrs=[];
 function t(key, vars={}) {
  const text=messages[key]?.[['ko','ja','en'].indexOf(language)] ?? key;
  return String(text).replace(/\{(\w+)\}/g, (match,name)=>vars[name] ?? match);
 }
 function capture() {
  const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walk.nextNode()) {
   const node=walk.currentNode, key=node.nodeValue.trim();
   if(messages[key]) staticNodes.push([node,key,node.nodeValue.match(/^\s*/)[0],node.nodeValue.match(/\s*$/)[0]]);
  }
  document.querySelectorAll('[aria-label],[placeholder]').forEach(node=>{
   for(const attr of ['aria-label','placeholder']) {
    const key=node.getAttribute(attr); if(messages[key]) staticAttrs.push([node,attr,key]);
   }
  });
 }
 function setLanguage(value) {
  language=['ko','ja','en'].includes(value)?value:'ko';
  document.documentElement.lang=language; document.title=t('pageTitle');
  staticNodes.forEach(([node,key,before,after])=>{if(node.isConnected) node.nodeValue=before+t(key)+after;});
  staticAttrs.forEach(([node,attr,key])=>node.setAttribute(attr,t(key)));
 }
 function country(code) {try{return new Intl.DisplayNames([language],{type:'region'}).of(code);}catch{return code;}}
 return {t,capture,setLanguage,country,get language(){return language;},get locale(){return {ko:'ko-KR',ja:'ja-JP',en:'en-US'}[language];}};
})();
