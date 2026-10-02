"""Inline SVG diagrams for the HCR guide (diagram-design rules, guide tokens).

All colors come from the guide's CSS custom properties through classes (.dg ...),
so the diagrams follow the page's light/dark theme. Width is 376 so they read on
a phone without horizontal scroll. Connectors are orthogonal with r=8 elbows.
"""
import html as _h
import unicodedata

W = 376
NODE_FS, SUB_FS, LBL_FS = 13, 12, 12


def tw(s, fs):
    """Text width: wide/full-width chars cost 1em, others ~0.6em."""
    w = 0.0
    for ch in s:
        if unicodedata.combining(ch):
            continue
        w += 1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.6
    return w * fs


def r4(v):
    return int(-(-v // 4) * 4)


def esc(s):
    return _h.escape(s, quote=True)


class D:
    def __init__(self, slug, title, desc, height):
        self.slug, self.title, self.desc, self.h = slug, title, desc, height
        self.zones, self.lines, self.labels, self.nodes, self.extra = [], [], [], [], []

    # ---------- primitives ----------
    def zone(self, x, y, w, h, label):
        self.zones.append(
            f'<rect class="zone" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
            f'<text class="zt" x="{x + 12}" y="{y + 19}">{esc(label)}</text>')

    def line(self, d, kind=""):
        cls = "ln" + (" acc" if "acc" in kind else "") + (" dash" if "dash" in kind else "")
        mk = f"{self.slug}-a" + ("c" if "acc" in kind else "")
        self.lines.append(f'<path class="{cls}" d="{d}" marker-end="url(#{mk})"/>')

    def label(self, x, y, text, anchor="start"):
        """Masked arrow label. (x, y) is the mask's top-left (anchor=start) or top-center (anchor=middle)."""
        w = r4(tw(text, LBL_FS) + 8)
        x0 = x - w / 2 if anchor == "middle" else x
        self.labels.append(
            f'<rect class="lm" x="{x0}" y="{y}" width="{w}" height="16" rx="2"/>'
            f'<text class="lt" x="{x0 + w / 2}" y="{y + 12.5}" text-anchor="middle">{esc(text)}</text>')
        return x0, w

    def node(self, x, y, w, h, name, sub=None, kind="", href=None, keys=""):
        assert tw(name, NODE_FS) + 16 <= w, (name, tw(name, NODE_FS), w)
        if sub:
            assert tw(sub, SUB_FS) + 12 <= w, (sub, tw(sub, SUB_FS), w)
        cx = x + w / 2
        ny = y + h / 2 + (-3 if sub else 4.5)
        body = (f'<rect class="bx{(" " + kind) if kind else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
                f'<text class="nm" x="{cx}" y="{ny}" text-anchor="middle">{esc(name)}</text>')
        if sub:
            body += f'<text class="sb" x="{cx}" y="{ny + 17}" text-anchor="middle">{esc(sub)}</text>'
        if href:
            self.n = getattr(self, "n", 0) + 1
            body = (f'<a class="dg-n" id="{self.slug}-{self.n}" href="{href}" data-t="{esc(name)}" data-k="{esc(keys + " " + (sub or ""))}">'
                    f'<title>{esc(name)} 설명으로 이동</title>{body}</a>')
        self.nodes.append(body)

    def raw(self, s):
        self.extra.append(s)

    def svg(self):
        s = self.slug
        return (f'<figure class="dgwrap"><svg class="dg" viewBox="0 0 {W} {self.h}" role="img" '
                f'aria-labelledby="{s}-title {s}-desc">'
                f'<title id="{s}-title">{esc(self.title)}</title><desc id="{s}-desc">{esc(self.desc)}</desc>'
                f'<defs><marker id="{s}-a" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                f'<polygon class="mk" points="0 0, 8 3, 0 6"/></marker>'
                f'<marker id="{s}-ac" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                f'<polygon class="mk acc" points="0 0, 8 3, 0 6"/></marker></defs>'
                + "".join(self.zones) + "".join(self.lines) + "".join(self.labels)
                + "".join(self.nodes) + "".join(self.extra) + "</svg></figure>")


# ------------------------------------------------------------------ 1. 기능 지도
def feature_map():
    d = D("dg-map", "HCR 기능 지도",
          "지도관제·목록관제·마이페이지 세 탭에 들어 있는 주요 기능과, 배차와 대리 접수로 이어지는 진입 경로를 보여준다.", 584)
    L, R, NW, NH = 20, 196, 156, 48
    # zone A 지도관제
    d.zone(8, 8, 356, 88, "지도관제")
    d.node(L, 36, NW, NH, "상점·라이더 모드", "지연 상점·라이더 위치", href="#map",
           keys="지도 지연 상점 라이더 위치 상점목록 배달목록")
    d.node(R, 36, NW, NH, "지도관제 설정", "지연 기준·배달 보기", href="#map-5",
           keys="지도 설정 지연 기준 테마 지도 가이드")
    # row C 공통 작업 (no zone)
    d.node(L, 128, NW, NH, "배차하기", "즉시배차·배차요청", kind="focal", href="#dispatch",
           keys="배차 즉시배차 배차요청 승낙 거절 배차변경 배차취소 다중선택")
    d.node(R, 128, NW, NH, "대리 접수", "+ 버튼·상점 길게 누르기", href="#order",
           keys="대리접수 주문 접수 도착지 주소 대기 상태로 접수")
    # zone B 목록관제
    d.zone(8, 200, 356, 88, "목록관제")
    d.node(L, 228, NW, NH, "접수·배차·완료·예정", "탭별 배달 목록", href="#list",
           keys="목록 접수 탭 배차 탭 완료 탭 예정 탭 예약 대기 상세 정렬 필터")
    d.node(R, 228, NW, NH, "+ 버튼", "대리 접수·멀티선택", href="#list-5",
           keys="플러스 버튼 멀티선택 단일선택 맨위로")
    # zone D 마이페이지
    d.zone(8, 300, 356, 276, "마이페이지")
    rows = [
        (("관제 허브 선택", "보이는 허브 범위", "#start-1", "관제 허브 허브 선택 지사"),
         ("상점 관리", "상세·설정복사·VAN", "#store", "상점 가맹점 설정복사 VAN 상점 등록")),
        (("운행 설정", "할증·수행 상황·공유망", "#ops", "운행설정 할증 설정할증 공유콜 도착지 중단"),
         ("라이더 관리", "등록·빠른 설정·매출", "#rider", "라이더 등록 빠른 설정 매출통계 바로머니")),
        (("바로머니 출금", "마스터 계정", "#withdraw", "출금 출금요청 계좌 문자 인증 한도"),
         ("공지·자동 지원금", "공지 등록·지원금 규칙", "#more-2", "공지 공지사항 지원금 자동 지원금")),
        (("알림·시스템 설정", "소리·화면·목록 색", "#settings", "알림 소리 설정 화면모드 글씨"),
         ("배달 내역", "지난 배달 조회", "#more-1", "배달내역 지난 배달 조회")),
    ]
    for i, (a, b) in enumerate(rows):
        y = 328 + i * 60
        d.node(L, y, NW, NH, a[0], a[1], href=a[2], keys=a[3])
        d.node(R, y, NW, NH, b[0], b[1], href=b[2], keys=b[3])
    # connectors (straight: shared x)
    d.line("M98 84 V124", "acc")
    d.label(106, 96, "배달 누르기")
    d.line("M98 228 V180", "acc")
    d.label(106, 182, "배차 버튼")
    d.line("M274 228 V180")
    d.label(282, 182, "대리 접수")
    return d.svg()


# ------------------------------------------------------------------ 2. 배달 상태 흐름
def state_flow():
    d = D("dg-state", "배달 상태와 목록관제 탭",
          "배달이 예약·대기, 접수, 배차요청, 배차, 픽업, 완료 또는 취소 상태로 바뀌는 순서와 각 상태가 보이는 목록관제 탭을 보여준다.", 568)
    d.zone(8, 8, 360, 76, "예정 탭")
    d.node(110, 28, 156, 44, "예약 · 대기")
    d.zone(8, 104, 360, 96, "접수 탭")
    d.node(20, 140, 136, 44, "접수", kind="focal")
    d.node(220, 140, 136, 44, "배차요청")
    d.zone(8, 228, 360, 216, "배차 탭")
    d.node(110, 256, 156, 44, "배차")
    d.node(110, 320, 156, 44, "픽업지 도착")
    d.node(110, 384, 156, 44, "픽업 완료")
    d.zone(8, 464, 360, 96, "완료 탭")
    d.node(20, 496, 64, 44, "취소")
    d.node(110, 496, 156, 44, "배달 완료")
    # 예약·대기 → 접수
    d.line("M150 72 V92 Q150 100 142 100 H96 Q88 100 88 108 V136")
    d.label(158, 76, "예약해제 · 접수로 변경")
    # 접수 ↔ 배차요청
    d.line("M156 152 H216")
    d.label(188, 128, "배차요청", "middle")
    d.line("M220 172 H160", "dash")
    d.label(188, 178, "거절", "middle")
    # 접수 → 배차 (즉시배차), 배차요청 → 배차 (승낙)
    d.line("M96 184 V270 Q96 278 104 278 H106", "acc")
    d.label(104, 206, "즉시배차")
    d.line("M288 184 V270 Q288 278 280 278 H270")
    d.label(296, 206, "승낙")
    # 배차 → 픽업 → 완료
    d.line("M188 300 V316")
    d.line("M188 364 V380")
    d.line("M188 428 V492")
    # 접수 → 취소
    d.line("M72 184 V492", "dash")
    d.label(32, 404, "취소", "start")
    return d.svg()


# ------------------------------------------------------------------ 3. 배차 흐름 (스윔레인)
def dispatch_lanes():
    d = D("dg-lane", "배차 흐름: 관제자 · HCR 앱 · 라이더 앱",
          "관제자가 라이더를 고른 뒤 즉시배차는 바로 배차 탭으로, 배차요청은 라이더 앱의 승낙 또는 거절을 거쳐 배차 탭이나 접수 상태로 가는 흐름을 보여준다.", 496)
    for x in (124, 252):
        d.raw(f'<line class="lane" x1="{x}" y1="8" x2="{x}" y2="488"/>')
    for x, t in ((62, "관제자"), (188, "HCR 앱"), (314, "라이더 앱")):
        d.raw(f'<text class="zt" x="{x}" y="24" text-anchor="middle">{t}</text>')
    d.node(10, 48, 104, 48, "라이더 고르기", "지도·목록에서")
    d.node(136, 128, 104, 48, "배차요청 표시", "접수 탭에 남음")
    d.node(262, 208, 104, 48, "요청 확인", "15초 안에")
    d.node(136, 320, 104, 48, "배차 탭으로", "배차 후 N분", kind="focal")
    d.node(136, 416, 104, 48, "다시 접수로", "다른 라이더로")
    # 배차요청: N1 right → down to N2
    d.line("M114 64 H180 Q188 64 188 72 V124")
    d.label(124, 40, "배차요청")
    # N2 → N3
    d.line("M240 152 H306 Q314 152 314 160 V204")
    # 즉시배차: N1 bottom → N4 left
    d.line("M62 96 V336 Q62 344 70 344 H132", "acc")
    d.label(70, 200, "즉시배차")
    # 승낙: N3 → N4 right
    d.line("M300 256 V336 Q300 344 292 344 H244")
    d.label(252, 320, "승낙")
    # 거절: N3 → N5 right
    d.line("M332 256 V432 Q332 440 324 440 H244", "dash")
    d.label(252, 416, "거절")
    return d.svg()


# ------------------------------------------------------------------ 4. 설정 × 반영되는 곳
def settings_matrix():
    cols = [("관제", "허브", "#start-1"), ("지도", "설정", "#map-5"), ("운행", "설정", "#ops"), ("상점", "설정", "#store-1")]
    rows = [
        ("보이는 배달 범위", "목록관제·지도에 보이는 허브", [1, 0, 0, 0]),
        ("지연 표시 기준", "배차지연·픽업지연 분", [0, 1, 0, 0]),
        ("배달대행료 할증", "설정할증·추가할증·구역 대행료", [0, 0, 1, 1]),
        ("배달 접수·중단", "수행 상황·도착지 중단·접수 제한", [0, 0, 1, 1]),
        ("라이더에게 보이는 콜", "노출 시간·공유콜 숨김·공유망", [0, 0, 1, 0]),
    ]
    cx0, cw, top, rh = 196, 44, 64, 52
    h = top + rh * len(rows) + 16
    d = D("dg-set", "설정이 반영되는 곳",
          "관제 허브 선택, 지도관제 설정, 운행 설정, 상점 설정이 각각 배달 범위, 지연 표시, 대행료 할증, 접수·중단, 라이더 노출 중 어디에 반영되는지 보여준다.", h)
    for i, (a, b, href) in enumerate(cols):
        x = cx0 + i * cw + cw / 2
        d.raw(f'<a class="dg-h" href="{href}"><title>{a}{b} 설명으로 이동</title>'
              f'<text class="zt hd" x="{x}" y="26" text-anchor="middle">{a}</text>'
              f'<text class="zt hd" x="{x}" y="44" text-anchor="middle">{b}</text></a>')
    for j, (name, sub, marks) in enumerate(rows):
        y = top + j * rh
        d.raw(f'<line class="lane" x1="8" y1="{y}" x2="{W - 8}" y2="{y}"/>')
        assert tw(name, NODE_FS) <= 172 and tw(sub, 10) <= 176, name
        d.raw(f'<text class="nm" x="12" y="{y + 22}">{esc(name)}</text>'
              f'<text class="sb sm" x="12" y="{y + 40}">{esc(sub)}</text>')
        for i, m in enumerate(marks):
            x = cx0 + i * cw + cw / 2
            if m:
                d.raw(f'<circle class="dot" cx="{x}" cy="{y + rh / 2}" r="7"/>')
            else:
                d.raw(f'<circle class="dot0" cx="{x}" cy="{y + rh / 2}" r="2"/>')
    d.raw(f'<line class="lane" x1="8" y1="{top + rh * len(rows)}" x2="{W - 8}" y2="{top + rh * len(rows)}"/>')
    return d.svg()


# ------------------------------------------------------------------ 5. 배차요청 시퀀스
def request_sequence():
    d = D("dg-seq", "배차요청이 오가는 순서",
          "관제자가 HCR에서 배차요청을 보내면 서버가 라이더 앱에 알리고, 라이더가 15초 안에 승낙하거나 거절한 결과가 서버를 거쳐 HCR에 반영되는 순서를 보여준다.", 392)
    xs = {"h": 64, "s": 188, "r": 312}
    for k, x in xs.items():
        d.raw(f'<line class="lane dashl" x1="{x}" y1="52" x2="{x}" y2="384"/>')
    d.node(14, 12, 100, 36, "HCR 앱")
    d.node(138, 12, 100, 36, "서버")
    d.node(262, 12, 100, 36, "라이더 앱")
    d.line("M64 92 H182", "acc"); d.label(126, 68, "배차요청", "middle")
    d.line("M188 132 H306"); d.label(250, 108, "푸시·소켓", "middle")
    d.node(262, 152, 100, 56, "배차요청 창", "15초 안에", kind="focal")
    d.line("M312 240 H194"); d.label(250, 216, "승낙 / 거절", "middle")
    d.line("M188 280 H70"); d.label(126, 256, "결과 반영", "middle")
    d.node(14, 300, 100, 56, "배차 탭으로", "거절은 접수로")
    return d.svg()

ALL = {"map": feature_map, "state": state_flow, "lane": dispatch_lanes, "set": settings_matrix, "seq": request_sequence}

if __name__ == "__main__":
    for k, f in ALL.items():
        print(k, len(f()))
