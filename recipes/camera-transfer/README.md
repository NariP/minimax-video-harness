# camera-transfer — 레퍼런스 영상의 카메라만 따라하기

피사체는 그 자리에 가만히 두고, 레퍼런스 영상의 **카메라 경로·앵글 변화·컷 타이밍**만 새 피사체와 새 공간으로 옮긴다.
Higgsfield Genjutsu Motion Transfer의 "텔레포트 캠" 스타일을 MiniMax H3로 재현하는 레시피.

## 언제 쓰나

| 잘 맞음 | 안 맞음 |
|---|---|
| 피사체가 거의 안 움직이고 카메라만 바뀌는 영상 | 피사체의 동작(춤·연기)을 옮기고 싶을 때 → motion 계열 레시피 |
| 원본 피사체와 새 피사체의 **덩어리 모양이 비슷**할 때 (둥근 강아지 → 둥근 인형) | 모양 차이가 클 때 (사람 → 네발 동물) |
| 2~15초 레퍼런스 | 15초 초과 → 잘라서 여러 번 |

## 입력

| 역할 | 파일 | 조건 |
|---|---|---|
| `reference_videos[0]` | 카메라 레퍼런스 | 2~15초, 23.976~60fps. VP9(인스타 릴스 등)는 하네스가 H.264로 자동 변환 |
| `reference_images[0]` | 새 피사체 **+ 새 공간**이 한 장에 담긴 스틸 | 피사체가 원하는 포즈로 원하는 배경에 있는 컷이 가장 안정적 |

> 스틸은 먼저 이미지 모델로 만들어 둔다(피사체 신원 고정 + 배경 교체). 영상 단계에서 배경까지 새로 지어내게 하면 각도마다 공간이 흔들린다.

## 절차

```
1. 레퍼런스 컷 시점 측정  →  2. prompt.txt 작성  →  3. check  →  4. submit  →  5. poll
```

### 1. 컷 시점 측정

```bash
ffmpeg -v error -i inputs/camera_ref.mp4 \
  -vf "select='gte(scene,0)',metadata=print:key=lavfi.scene_score:file=-" -f null - \
  | paste - - | awk '{for(i=1;i<=NF;i++){if($i~/pts_time/){split($i,a,":");t=a[2]} if($i~/scene_score/){split($i,b,"=");s=b[2]}} if(s>0.15) printf "%.3f %.3f\n",t,s}'
```

- 점수가 연달아 높은 구간은 휩 팬(흐린 회전 전환)일 가능성이 크다. 컨택트 시트로 눈으로 확인한다:
  `ffmpeg -i inputs/camera_ref.mp4 -vf "fps=12,scale=120:-1,tile=12x8" -frames:v 1 sheet.jpg`
- 각 컷의 프레이밍(초근접/정면 풀샷/옆/위/뒤/전경 가림)을 한 줄씩 적어 둔다.

### 2. prompt.txt

`prompt.template.txt`를 복사해 채운다. Ref2VA 6섹션 형식(MiniMax 공식 `h3-prompt-writing`)이다.

핵심 규칙:
- **카메라 움직임을 문장으로 새로 지시하지 않는다.** 컷마다 프레이밍 한 줄 + 원본과 **같은 타임스탬프**만 적는다. 다른 무빙을 쓰면 Video 1과 경쟁한다.
- **원본 피사체·세트·조명을 복사하지 말라고 명시한다.** (`Its dog, living room … are not used.`)
- 공간 랜드마크를 방향별로 2~3개 정한다(나무/벤치/꽃밭 등). 각도가 바뀔 때 "다른 쪽"으로 읽힌다.
- 허용할 미세 움직임만 적는다(바람에 털, 고개 한 번 갸웃). 큰 동작을 적으면 카메라 대신 피사체가 움직인다.

### 3~5. 실행

```bash
cp <repo>/recipes/camera-transfer/job.example.json job.json   # 내 작업 폴더에서, id·경로 수정
python3 <repo>/harness/minimax.py check  job.json   # 예상 과금 초 확인
python3 <repo>/harness/minimax.py submit job.json
python3 <repo>/harness/minimax.py poll   camera-transfer-v1
```

## 결과가 이상할 때

| 증상 | 원인 | 수정 |
|---|---|---|
| 원본 방·가구가 남아 있음 | 영상이 공간까지 가져감 | 1차: 원본 공간만 유지하고 피사체만 교체 → 2차: 그 결과를 영상 편집으로 배경 교체 |
| 전환 수가 줄고 뭉개짐 | 8초에 15컷 이상은 과밀 | 레퍼런스를 4초씩 잘라 두 번 생성 후 이어 붙이기 |
| 각도마다 얼굴·소품이 다름 | 신원 고정 문장이 약함 | `subject_definitions`·`retention_analysis`에 고정 목록을 구체적으로, 참조 이미지 해상도 확보 |
| 피사체가 걸어다님 | 동작 문장이 많음 | 허용 움직임을 한 줄로 줄이고 `stays in the same spot and pose` 반복 |

## 검증된 사례

- 8초 9:16 릴스(흰 푸들, 거실, 컷 약 15개) → 펠트 인형 + 잔디밭 스틸 1장. 768P·8초, 과금 16초. 1회차에 채택.
