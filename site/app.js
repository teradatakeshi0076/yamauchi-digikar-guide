(function () {
  'use strict';
  var G = window.GUIDE || { cats: [], topics: [] };
  var V = G.ver ? '?v=' + G.ver : '';
  var CAT = {}; G.cats.forEach(function (c) { CAT[c.id] = c; });
  var TOP = {}; G.topics.forEach(function (t) { TOP[t.id] = t; });
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var app = $('#app'), q = $('#q'), res = $('#results'), qclear = $('#qclear');

  /* ---------- 保存(使えない環境でも動く) ---------- */
  function load(k, d) { try { var v = localStorage.getItem('dg.' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem('dg.' + k, JSON.stringify(v)); } catch (e) {} }

  /* ---------- 文字の正規化 ---------- */
  function norm(s) {
    s = String(s || '').normalize('NFKC').toLowerCase();
    s = s.replace(/[ァ-ヶ]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0x60); });
    return s.replace(/[\s・、。,.「」『』()（）\[\]【】:：;；!！?？"'＂〜~\-ー―→⇒]/g, function (c) { return c === 'ー' ? 'ー' : ''; });
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- 言い換え辞書 ---------- */
  var SYN = [
    ['取消', '取り消し', '取り消す', 'とりけし', 'キャンセル', 'やめる', '取りやめ'],
    ['削除', '消す', '消したい'],
    ['返金', '払い戻し', '払戻', 'お金を返す', '返す'],
    ['資格', '保険証', '資格確認書', '被保険者証'],
    ['マイナ', 'マイナンバー', 'マイナ保険証', 'オンライン資格', '顔認証', 'カードリーダー'],
    ['処方', '薬', 'くすり', '投薬', '処方箋', '処方せん'],
    ['傷病名', '病名', '診断名'],
    ['レセプト', 'レセ', '保険請求', '月初', '請求作業'],
    ['未収', '未収金', '払えない', '足りない', '後払い', '後日払い', '持ち合わせ'],
    ['領収書', '領収証', 'レシート', '明細書'],
    ['自費', '自由診療', '保険外', '美容', '自費診療'],
    ['会計', '精算', 'お会計', '支払い', '支払'],
    ['新規', '初めて', 'はじめて', '新患', '新しい患者', '新規患者'],
    ['再来', '2回目', '二回目', '再来患者'],
    ['定期', '定期登録', 'いつもの薬', '前回と同じ', 'do処方', '定期処方'],
    ['ログイン', '入れない', '起動', '立ち上げ', 'パスワード', 'サインイン'],
    ['障害発生', '動かない', 'つながらない', '繋がらない', 'フリーズ', 'エラー', '止まった', '固まった'],
    ['印刷', 'プリント', '出力', '発行'],
    ['公費', '助成', '医療証', '受給者証'],
    ['生活保護', '生保', 'せいほ', '医療扶助'],
    ['労災', '仕事中', '業務中'],
    ['自賠責', '交通事故'],
    ['コメント', 'メモ', '備考'],
    ['検査', '採血', '検査結果'],
    ['点滴', '注射'],
    ['変更', '変わった', '直す', '修正', '訂正'],
    ['予約', 'よやく', '予約枠'],
    ['後日', 'あとから', '後から', 'あとで', '後で', '翌日'],
    ['忘れ', 'わすれ', '持ってない', '持っていない', '不携帯'],
    ['当日', '今日', 'その日']
  ].map(function (g) { return g.map(norm); });

  // 検索語の言い換えを作る。[語, 重み] の並び。
  // 1) 入力そのまま(重み1)
  // 2) 入力の中の辞書語だけを言い換えた形(重み0.8)。例「投薬日数を一括」→「処方日数を一括」
  // 3) 辞書語そのもの(重み0.3)。長い文で入れた時の拾い漏れを防ぐ補助。弱くして、他の項目が
  //    題名どおりの項目より上に来ないようにする
  function variants(term) {
    var v = [[term, 1]];
    var add = function (w, k) {
      if (!w) return;
      for (var i = 0; i < v.length; i++) if (v[i][0] === w) { if (v[i][1] < k) v[i][1] = k; return; }
      v.push([w, k]);
    };
    SYN.forEach(function (g) {
      g.forEach(function (m) {
        if (m.length < 2 || term.indexOf(m) < 0) return;
        g.forEach(function (w) {
          if (w === m) return;
          add(term.split(m).join(w), term === m ? 0.8 : 0.8);
          add(w, term === m ? 0.8 : 0.3);
        });
      });
    });
    return v;
  }

  /* ---------- 検索の下ごしらえ ---------- */
  var IDX = G.topics.map(function (t) {
    var steps = [];
    (t.parts || []).forEach(function (p) { if (p.heading) steps.push(p.heading); (p.steps || []).forEach(function (s) { steps.push(String(s.text || '').replace(/\[\[[^\]]+\]\]/g, ''), String(s.note || '').replace(/\[\[[^\]]+\]\]/g, '')); }); });
    return {
      t: t,
      f: [
        [norm(t.title), 10],
        [norm((t.keywords || []).join('|')), 6],
        [norm((t.situations || []).join('|')), 5],
        [norm(t.summary) + '|' + norm(t.manualTitle), 4],
        [norm((t.warnings || []).concat(t.tips || []).join('|')), 2],
        [norm(steps.join('|')), 1]
      ]
    };
  });
  var PREF_RE = /(北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|神奈川|新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄)/;

  function termScore(ix, vs) {
    var best = 0;
    vs.forEach(function (pair) {
      var w = pair[0], s = 0;
      if (/^\d+$/.test(w)) {
        // 数字だけ(法別番号など)は、前後が数字でない所で一致したときだけ数える(「12」が「120」に当たらないように)。
        // 題名・検索用の言葉を重く、本文(都道府県の公費の表など)も軽く数える
        var re = new RegExp('(^|[^0-9])' + w + '([^0-9]|$)');
        ix.f.forEach(function (f) { if (re.test(f[0])) s += f[1]; });
        if (s && /公費|助成/.test(ix.t.title)) s += 6;
      } else {
        ix.f.forEach(function (f) { if (f[0].indexOf(w) >= 0) s += f[1]; });
      }
      s *= pair[1];
      if (s > best) best = s;
    });
    return best;
  }
  function bigrams(s) { var a = []; for (var i = 0; i < s.length - 1; i++) a.push(s.substr(i, 2)); return a; }

  // 動作確認用(検索の回帰テストで使う)
  window.__guideSearch = function (raw) { return search(raw).map(function (o) { return { id: o.t.id, s: Math.round(o.s) }; }); };
  window.__guideVariants = function (raw) { return variants(norm(raw)); };
  function search(raw) {
    var terms = String(raw).split(/[\s　]+/).map(norm).filter(Boolean);
    if (!terms.length) return [];
    var wantPref = PREF_RE.test(raw);
    var vss = terms.map(variants);
    var out = [];
    IDX.forEach(function (ix) {
      var total = 0, ok = true;
      vss.forEach(function (vs) { var s = termScore(ix, vs); if (!s) ok = false; total += s; });
      if (ok) out.push({ t: ix.t, s: total });
    });
    if (!out.length) {
      // 言葉が完全に一致しない時: 2文字ずつのかけらで近いものを探す
      var bg = bigrams(terms.join(''));
      if (bg.length) {
        IDX.forEach(function (ix) {
          var hit = 0, sc = 0;
          bg.forEach(function (b) {
            var w = 0; ix.f.forEach(function (f) { if (f[1] >= 4 && f[0].indexOf(b) >= 0) w = Math.max(w, f[1]); });
            if (w) { hit++; sc += w; }
          });
          if (hit / bg.length >= 0.5) out.push({ t: ix.t, s: sc * hit / bg.length, fuzzy: true });
        });
      }
    }
    out.forEach(function (o) { if (o.t.region === 'other' && !wantPref) o.s *= 0.3; });
    // 題名と同じ言葉で探した時は、その項目を必ず一番上に。題名にそのまま含まれる時も上げる
    var whole = terms.join('');
    out.forEach(function (o) {
      var nt = norm(o.t.title);
      if (nt === whole) o.s += 1000;
      else if (whole.length >= 2 && nt.indexOf(whole) >= 0) o.s += 20;
    });
    out.sort(function (a, b) { return b.s - a.s || a.t.order - b.t.order; });
    return out.slice(0, 14).map(function (o) { o.terms = vss; return o; });
  }

  function hl(text, vss) {
    var s = esc(text);
    var words = [];
    (vss || []).forEach(function (vs) { vs.forEach(function (w) { if (w.length >= 1) words.push(w); }); });
    if (!words.length) return s;
    // 正規化した語で、元の文字列の該当部分に印をつける(カタカナ/ひらがなの違いも吸収)
    var n = norm(text), marks = [];
    words.sort(function (a, b) { return b.length - a.length; }).forEach(function (w) {
      var i = n.indexOf(w); if (i >= 0) marks.push([i, i + w.length]);
    });
    if (!marks.length || n.length !== text.normalize('NFKC').replace(/[\s・、。,.「」『』()（）\[\]【】:：;；!！?？"'＂〜~\-―→⇒]/g, '').length) return s;
    // 元文字列の位置との対応表
    var map = [], src = text;
    for (var i = 0; i < src.length; i++) { if (norm(src[i]).length) map.push(i); }
    var flags = new Array(src.length).fill(false);
    marks.forEach(function (m) { for (var k = m[0]; k < m[1] && k < map.length; k++) flags[map[k]] = true; });
    var outS = '', open = false;
    for (var j = 0; j < src.length; j++) {
      if (flags[j] && !open) { outS += '<mark>'; open = true; }
      if (!flags[j] && open && norm(src[j]).length) { outS += '</mark>'; open = false; }
      outS += esc(src[j]);
    }
    if (open) outS += '</mark>';
    return outS;
  }

  /* ---------- 検索欄 ---------- */
  var sel = -1, cur = [];
  function chip(cat) { var c = CAT[cat] || { name: cat, tone: 'navy' }; return '<span class="chip t-' + c.tone + '">' + esc(c.name) + '</span>'; }
  function bestLine(t, vss) {
    var cands = (t.situations || []).concat(t.keywords || []);
    for (var i = 0; i < cands.length; i++) {
      var n = norm(cands[i]);
      for (var a = 0; a < vss.length; a++) for (var b = 0; b < vss[a].length; b++) if (n.indexOf(vss[a][b]) >= 0 && (t.situations || []).indexOf(cands[i]) >= 0) return 'こんな時: ' + hl(cands[i], vss);
    }
    return esc(t.summary);
  }
  /* 最近の検索(この端末だけ・8件) 結果を開いた時の言葉だけ残す */
  function rememberQuery() {
    var v = q.value.trim(); if (!v) return;
    var list = load('searches', []).filter(function (x) { return x !== v; });
    list.unshift(v); save('searches', list.slice(0, 8));
  }
  function renderRecent() {
    var list = load('searches', []);
    cur = []; sel = -1;
    if (!list.length || document.activeElement !== q) { res.hidden = true; return; }
    res.innerHTML = '<div class="r-head"><span>最近の検索</span><button type="button" class="r-clear" id="rClear">履歴を消す</button></div>' +
      list.map(function (w) {
        return '<button type="button" class="r-item r-recent" data-q="' + esc(w) + '"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg><span>' + esc(w) + '</span></button>';
      }).join('');
    res.hidden = false;
  }
  res.addEventListener('mousedown', function (e) {
    // 押した瞬間に検索欄から外れて一覧が閉じないように
    if (e.target.closest('.r-recent, .r-clear')) e.preventDefault();
  });
  res.addEventListener('click', function (e) {
    var b = e.target.closest('.r-recent');
    if (b) { q.value = b.dataset.q; renderResults(); q.focus(); return; }
    if (e.target.closest('.r-clear')) { save('searches', []); res.hidden = true; q.focus(); }
  });

  function renderResults() {
    var v = q.value.trim();
    qclear.hidden = !v;
    if (!v) { renderRecent(); return; }
    cur = search(v); sel = cur.length ? 0 : -1;
    if (!cur.length) {
      res.innerHTML = '<div class="r-none">「' + esc(v) + '」に合う手順が見つかりません。<br>短い言葉(例:「返金」「保険証」「取消」)や、別の言い方で試してください。</div>';
    } else {
      res.innerHTML = (cur[0].fuzzy ? '<div class="r-none" style="padding:6px 12px">近い手順を表示しています</div>' : '') +
        cur.map(function (o, i) {
          return '<a class="r-item" role="option" href="#/t/' + o.t.id + '" aria-selected="' + (i === sel) + '">' +
            '<div class="r-top"><span class="r-title">' + hl(o.t.title, o.terms) + '</span>' + chip(o.t.category) + '</div>' +
            '<div class="r-sub">' + bestLine(o.t, o.terms) + '</div></a>';
        }).join('');
    }
    res.hidden = false;
  }
  function moveSel(d) {
    if (!cur.length) return;
    sel = (sel + d + cur.length) % cur.length;
    var items = res.querySelectorAll('.r-item');
    items.forEach(function (el, i) { el.setAttribute('aria-selected', i === sel); });
    items[sel].scrollIntoView({ block: 'nearest' });
  }
  q.addEventListener('input', renderResults);
  q.addEventListener('focus', renderResults);
  q.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); moveSel(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); moveSel(-1); }
    else if (e.key === 'Enter') { if (cur[sel]) { rememberQuery(); location.hash = '#/t/' + cur[sel].t.id; closeResults(); q.blur(); } }
    else if (e.key === 'Escape') { if (q.value) { q.value = ''; renderResults(); } else q.blur(); }
  });
  qclear.addEventListener('click', function () { q.value = ''; renderResults(); q.focus(); });
  function closeResults() { res.hidden = true; }
  document.addEventListener('click', function (e) { if (e.target.isConnected && !$('#search').contains(e.target)) closeResults(); });
  res.addEventListener('click', function (e) { if (e.target.closest('a.r-item')) { rememberQuery(); closeResults(); q.blur(); } });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== q && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); q.select(); }
    if (e.key === 'Escape' && !$('#lightbox').hidden) closeLB();
  });

  /* ---------- 文字の大きさ ---------- */
  var fontBtn = $('#fontBtn');
  function applyBig(b) { document.documentElement.classList.toggle('big', b); fontBtn.setAttribute('aria-pressed', b); }
  applyBig(!!load('big', false));
  fontBtn.addEventListener('click', function () { var b = !document.documentElement.classList.contains('big'); applyBig(b); save('big', b); });

  /* ---------- アイコン ---------- */
  var ICONS = {
    desk: '<rect x="3" y="11" width="18" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/><circle cx="12" cy="5" r="0"/>',
    card: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16c.6-1.5 1.7-2 3-2s2.4.5 3 2M14 10h4M14 13h3"/>',
    note: '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 16h5"/>',
    yen: '<path d="M7 4l5 7 5-7M12 11v9M8 13h8M8 16h8"/>',
    cal: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M8 14h2M12 14h2M8 17h2"/>',
    calc: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h1M12 11h1M16 11h0M8 15h1M12 15h1M16 15v3"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    power: '<path d="M12 3v8"/><path d="M6.3 7.3a8 8 0 1 0 11.4 0"/>',
    clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    star: '<path d="M12 4l2.5 5 5.5.8-4 3.9.9 5.5L12 16.6 7.1 19.2l.9-5.5-4-3.9 5.5-.8z"/>'
  };
  function ic(n) { return '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + (ICONS[n] || '') + '</svg>'; }

  /* ---------- 画面 ---------- */
  function catCount(id) { return G.topics.filter(function (t) { return t.category === id; }).length; }
  function linkList(ids, empty) {
    var items = ids.map(function (id) { return TOP[id]; }).filter(Boolean);
    if (!items.length) return '<div class="empty">' + empty + '</div>';
    return '<ul class="list">' + items.map(function (t) { return '<li><a href="#/t/' + t.id + '">' + chip(t.category) + '<span>' + esc(t.title) + '</span></a></li>'; }).join('') + '</ul>';
  }

  function home() {
    var sits = [], seen = {};
    ['uketsuke', 'hoken', 'kaikei', 'shinsatsu', 'login'].forEach(function (c) {
      G.topics.forEach(function (t) {
        if (t.category === c && t.region !== 'other' && (t.situations || []).length && !seen[t.id] && sits.length < 14) {
          var per = sits.filter(function (s) { return s.t.category === c; }).length;
          if (per < 3) { seen[t.id] = 1; sits.push({ t: t, s: t.situations[0] }); }
        }
      });
    });
    var views = load('views', {});
    var often = Object.keys(views).filter(function (k) { return TOP[k]; }).sort(function (a, b) { return views[b] - views[a]; }).slice(0, 6);
    app.innerHTML =
      '<div class="hello"><div><h1>どの作業を調べますか?</h1><p class="lead">上の検索欄に、やりたいことや困っていることを普段の言葉で入れてください。</p></div></div>' +
      '<h2>分野から探す</h2><div class="cats">' + G.cats.map(function (c) {
        return '<a class="cat ' + c.tone + '" href="#/c/' + c.id + '"><div style="display:flex;align-items:center">' + ic(c.icon) + '<span class="cnt">' + catCount(c.id) + '件</span></div><b>' + esc(c.name) + '</b><small>' + esc(c.desc) + '</small></a>';
      }).join('') + '</div>' +
      (sits.length ? '<h2>こんな時は?</h2><div class="sits">' + sits.map(function (x) { return '<a class="sit" href="#/t/' + x.t.id + '">' + esc(x.s) + '</a>'; }).join('') + '</div>' : '') +
      '<div class="cols" style="margin-top:32px">' +
      '<div class="box"><h3>★ お気に入り</h3>' + linkList(load('fav', []), 'よく使う手順は、手順ページの「★ お気に入り」で、ここに置いておけます。') + '</div>' +
      '<div class="box"><h3>最近見た手順</h3>' + linkList(load('recent', []).slice(0, 6), 'まだありません。') + '</div>' +
      '</div>' +
      (often.length ? '<div class="box" style="margin-top:16px"><h3>この端末でよく見る手順</h3>' + linkList(often, '') + '</div>' : '') +
      foot();
  }

  function foot() { return '<div class="foot">元の資料: デジカル操作マニュアル(レセコン一体型・レセコン単体)更新日 ' + esc(G.manualDate) + '。画面写真はマニュアルのものです(見本の患者名を含みます)。</div>'; }

  function catPage(id) {
    var c = CAT[id]; if (!c) return notFound();
    var list = G.topics.filter(function (t) { return t.category === id; });
    var main = list.filter(function (t) { return t.region !== 'other'; });
    var other = list.filter(function (t) { return t.region === 'other'; });
    var row = function (t) { return '<a class="trow" href="#/t/' + t.id + '"><b>' + esc(t.title) + '</b><small>' + esc(t.summary) + '</small></a>'; };
    app.innerHTML = '<div class="crumb"><a href="#/">ホーム</a> › ' + esc(c.name) + '</div>' +
      '<h1>' + esc(c.name) + '</h1><p class="lead">' + esc(c.desc) + '</p>' +
      (id === 'receipt' ? '<p class="lead" style="margin-top:6px">月に1回の作業です。上から順に進めてください。</p>' : '') +
      '<div class="tlist' + (id === 'receipt' ? ' flow' : '') + '" style="margin-top:20px">' + main.map(row).join('') + '</div>' +
      (other.length ? '<details class="more"><summary>東京都以外の公費(' + other.length + '件)</summary><div class="tlist" style="margin-top:12px">' + other.map(row).join('') + '</div></details>' : '') +
      foot();
  }

  function topicPage(id) {
    var t = TOP[id]; if (!t) return notFound();
    var c = CAT[t.category] || { name: '' };
    var recent = load('recent', []).filter(function (x) { return x !== id; }); recent.unshift(id); save('recent', recent.slice(0, 12));
    var views = load('views', {}); views[id] = (views[id] || 0) + 1; save('views', views);
    var fav = load('fav', []), isFav = fav.indexOf(id) >= 0;
    var done = load('done.' + id, {});
    var n = 0;
    var parts = (t.parts || []).map(function (p, pi) {
      var raw = p.raw;
      var steps = (p.steps || []).map(function (s, si) {
        var key = pi + '-' + si;
        var label = raw ? '' : String(++n);
        return '<li class="step' + (done[key] ? ' done' : '') + '" data-k="' + key + '">' +
          '<button class="num" aria-label="手順' + label + 'を済みにする" title="押すと「済み」になります">' + (done[key] ? '✓' : label) + '</button>' +
          '<div>' + (s.text ? '<div class="stxt">' + rich(s.text) + '</div>' : '') +
          (s.note ? '<div class="snote">※ ' + rich(s.note) + '</div>' : '') +
          ((s.imgs || []).length ? '<div class="shots">' + s.imgs.map(function (src) {
            var sz = (G.sizes || {})[src];
            var wh = sz ? ' width="' + sz[0] + '" height="' + sz[1] + '" style="width:' + sz[0] + 'px"' : '';
            return '<button class="shot" data-src="' + esc(src) + '" aria-label="画面写真を拡大"><img loading="lazy" src="' + esc(src + V) + '"' + wh + ' alt="' + esc(s.text) + 'の画面"></button>';
          }).join('') + '</div>' : '') + '</div></li>';
      }).join('');
      return '<section class="part' + (raw ? ' raw' : '') + '">' + (p.heading ? '<h2>' + esc(p.heading) + '</h2>' : (pi > 0 ? '<div style="height:16px"></div>' : '')) + '<ol class="steps">' + steps + '</ol></section>';
    }).join('');
    var pg = t.pages && t.pages.length ? (t.pages[0] === t.pages[t.pages.length - 1] ? t.pages[0] : t.pages[0] + '〜' + t.pages[t.pages.length - 1]) : '';
    app.innerHTML = '<div class="crumb"><a href="#/">ホーム</a> › <a href="#/c/' + t.category + '">' + esc(c.name) + '</a></div>' +
      '<div class="tp-head"><div><h1>' + esc(t.title) + '</h1><p class="lead">' + esc(t.summary) + '</p></div>' +
      '<div class="tp-acts"><button class="star" id="favBtn" aria-pressed="' + isFav + '">' + (isFav ? '★ お気に入り済み' : '☆ お気に入り') + '</button><button class="star" onclick="window.print()">印刷</button></div></div>' +
      '<div class="meta">マニュアル ' + esc(t.manualTitle || '') + (pg ? '(' + pg + 'ページ)' : '') + '</div>' +
      (t.warnings.length ? '<div class="warn"><b>注意</b><ul>' + t.warnings.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul></div>' : '') +
      parts +
      (n > 1 ? '<div class="donebar">番号を押すと「済み」になります。<button id="resetDone">済みを全部もどす</button></div>' : '') +
      (t.tips.length ? '<div class="tips"><b>知っておくと便利</b><ul>' + t.tips.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul></div>' : '') +
      linksHtml(t) +
      (t.related.length ? '<h2>あわせて見る</h2><div class="rel">' + t.related.map(function (r) { return TOP[r] ? '<a href="#/t/' + r + '">' + esc(TOP[r].title) + '</a>' : ''; }).join('') + '</div>' : '') +
      sameCat(t) + foot();

    $('#favBtn').addEventListener('click', function () {
      var f = load('fav', []), i = f.indexOf(id);
      if (i >= 0) f.splice(i, 1); else f.unshift(id);
      save('fav', f); this.setAttribute('aria-pressed', i < 0); this.textContent = i < 0 ? '★ お気に入り済み' : '☆ お気に入り';
    });
    app.querySelectorAll('.step .num').forEach(function (b) {
      b.addEventListener('click', function () {
        var li = b.closest('.step'), k = li.dataset.k, d = load('done.' + id, {});
        d[k] = !d[k]; if (!d[k]) delete d[k]; save('done.' + id, d);
        li.classList.toggle('done', !!d[k]);
        var lbl = b.getAttribute('aria-label').replace(/[^0-9]/g, '');
        b.textContent = d[k] ? '✓' : lbl;
      });
    });
    var rd = $('#resetDone'); if (rd) rd.addEventListener('click', function () { save('done.' + id, {}); topicPage(id); });
    app.querySelectorAll('.shot').forEach(function (b) {
      b.addEventListener('click', function () { openLB(b.dataset.src, t.title); });
      // 画面写真は表示する大きさの2倍の細かさで書き出してあるので、半分の大きさで表示する(はみ出す分だけ縮める)
      var im = b.querySelector('img');
      var fit = function () { if (im.naturalWidth) im.style.width = Math.round(im.naturalWidth / 2) + 'px'; };
      if (!(G.sizes || {})[b.dataset.src]) { if (im.complete) fit(); else im.addEventListener('load', fit); }
    });
  }


  /* 文中のアイコン [[img/icon_xxx.webp]] と URL を表示用にする(元の文字は esc 済み) */
  function rich(text) {
    var h = esc(text);
    h = h.replace(/\[\[(img\/[A-Za-z0-9_]+\.webp)\]\]/g, function (m, src) { return '<img class="ic-inline" src="' + src + V + '" alt="">'; });
    h = h.replace(/(https?:\/\/[A-Za-z0-9\-._~:\/?#@!$&'*+,;=%]+)/g, function (u) { return '<a href="' + u + '" target="_blank" rel="noopener">' + u + '</a>'; });
    return h;
  }
  function linksHtml(t) {
    if (!(t.links || []).length) return '';
    return '<h2>参考リンク</h2><ul class="links">' + t.links.map(function (l) {
      return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + '</a><small>' + esc(l.url) + '(マニュアル' + l.page + 'ページ)</small></li>';
    }).join('') + '</ul><p class="links-note">外部のサイトです。内容や表示はリンク先のサイトによります。</p>';
  }

  function sameCat(t) {
    var list = G.topics.filter(function (x) { return x.category === t.category && x.region !== 'other'; });
    var i = list.indexOf(t); if (i < 0) return '';
    var prev = list[i - 1], next = list[i + 1];
    if (!prev && !next) return '';
    return '<div class="rel" style="margin-top:28px;justify-content:space-between">' +
      (prev ? '<a href="#/t/' + prev.id + '">← ' + esc(prev.title) + '</a>' : '<span></span>') +
      (next ? '<a href="#/t/' + next.id + '">' + esc(next.title) + ' →</a>' : '') + '</div>';
  }

  function notFound() { app.innerHTML = '<h1>ページが見つかりません</h1><p><a href="#/">ホームへ戻る</a></p>'; }

  /* ---------- 画像の拡大 ---------- */
  var lb = $('#lightbox'), lbBody = $('#lbBody');
  function openLB(src, cap) {
    // 最初から本文の1.5倍の大きさで開く(細かく書き出してあるので、大きくしてもぼやけない)。押すと画面に合わせた大きさ
    var sz = (G.sizes || {})[src];
    lbBody.className = 'lb-body zoom';
    lbBody.innerHTML = '<img src="' + esc(src + V) + '" alt="">';
    var big = lbBody.querySelector('img');
    var setBig = function (w) { big.style.width = Math.round(w * 1.5) + 'px'; };
    if (sz) setBig(sz[0]); else big.addEventListener('load', function () { setBig(big.naturalWidth / 2); });
    $('#lbCap').textContent = cap + '(画像を押すと全体表示／大きく表示を切り替え)';
    lb.hidden = false; document.body.style.overflow = 'hidden';
    big.addEventListener('click', function (e) { e.stopPropagation(); lbBody.classList.toggle('zoom'); });
  }
  function closeLB() { lb.hidden = true; lbBody.innerHTML = ''; document.body.style.overflow = ''; }
  $('#lbClose').addEventListener('click', closeLB);
  lbBody.addEventListener('click', function (e) { if (e.target === lbBody) closeLB(); });

  /* ---------- 道案内 ---------- */
  function route() {
    var h = location.hash.replace(/^#/, '') || '/';
    var m;
    closeResults();
    if (!lb.hidden) closeLB();
    app.classList.toggle('wide', /^\/t\//.test(h));
    if ((m = h.match(/^\/t\/(.+)$/))) topicPage(decodeURIComponent(m[1]));
    else if ((m = h.match(/^\/c\/(.+)$/))) catPage(m[1]);
    else home();
    window.scrollTo(0, 0);
    var t = h.match(/^\/t\/(.+)$/) && TOP[decodeURIComponent(h.slice(3))];
    document.title = (t ? t.title + '｜' : '') + 'デジカル操作ガイド｜やまうちクリニック';
  }
  window.addEventListener('hashchange', function () { q.value = ''; qclear.hidden = true; route(); });
  route();
})();
