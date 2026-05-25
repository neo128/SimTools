# SimTools 中文快速开始

本文是 SimTools 的本地快速使用入口，覆盖 7 个已接入仿真工具的状态检查、启动、加载、操作、测试和产物查看。

更完整的英文/中文混合细节见：

- [docs/14_QUICK_USE.md](docs/14_QUICK_USE.md)
- [docs/15_REAL_LOCAL_RUN_REQUIREMENTS.md](docs/15_REAL_LOCAL_RUN_REQUIREMENTS.md)
- [docs/16_VERIFICATION_REPORT_2026-05-25.md](docs/16_VERIFICATION_REPORT_2026-05-25.md)

## 基本原则

- SimTools 是元管理器，不是把所有 simulator 装进一个 Python 环境。
- 每个仿真工具使用独立本地环境，例如 `.venv-ai2thor`、`.venv-habitat`、`.venv-omnigibson`。
- 默认命令尽量只做状态检查或 dry-run；真实 viewer 必须显式加 `--execute`。
- `pytest` 不启动真实 GUI，不导入重型 simulator。
- 不自动运行 `sudo`，不自动修改系统配置，不自动接受任何 EULA。

## 一键检查当前项目状态

在仓库根目录运行：

```bash
python -m simtools list
python -m simtools compare
python -m simtools validate --json
python -m simtools real-status --strict
pytest
```

当前目标状态：

```text
Real-ready tools: 7/7
```

## 通用命令

查看工具列表：

```bash
python -m simtools list
```

查看某个工具信息：

```bash
python -m simtools info ai2thor
python -m simtools info omnigibson
```

查看安装/运行诊断：

```bash
python -m simtools doctor
python -m simtools doctor ai2thor
python -m simtools doctor behavior1k
```

查看安装计划，不自动安装：

```bash
python -m simtools install-plan
python -m simtools install-plan omnigibson
```

查看产物：

```bash
python -m simtools artifacts
python -m simtools artifacts ai2thor
```

查看实验库和 run 历史：

```bash
python -m simtools experiments list
python -m simtools experiments info ai2thor_floorplan1_navigation_smoke
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools runs list
```

启动 SimTools dashboard：

```bash
python -m simtools ui
```

Dashboard 包含 Experiment Library、Run History 和 Run Detail，可读取
`.simtools/runs/` 下的 `report.json` 并展示 artifact path。

## Experiment Workbench v0.2

实验配置位于 `configs/experiments/`，当前内置：

| Experiment | Tool | 输出 |
| --- | --- | --- |
| `ai2thor_floorplan1_navigation_smoke` | AI2-THOR | PPM screenshot 引用 |
| `habitat_skokloster_visual_observation` | Habitat | PNG artifact 引用 |
| `maniskill_pickcube_visual_rollout` | ManiSkill | MP4 artifact 引用 |

每次实验 run 会创建：

```text
.simtools/runs/<timestamp>_<experiment_id>/
  run.yaml
  manifest_snapshot.yaml
  environment.json
  stdout.log
  stderr.log
  report.json
  artifacts/
```

其中 `report.json` 至少包含 `run_id`、`experiment_id`、`tool_id`、
`scene`、`task`、`dry_run`、`status`、`started_at`、`finished_at`、
`duration_seconds`、`artifacts`、`command` 和 `message`。Dashboard 的
Run Detail 会显示 run 目录、report 路径和 artifact 目录。

安全 dry-run：

```bash
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools experiments report <run_id>
python -m simtools runs list
```

Workbench v0.2 默认 dry-run。真实 run 需要显式使用 `--no-dry-run`，
第一阶段只复用已有路径：AI2-THOR 使用 smoke，Habitat 使用 visual render，
ManiSkill 使用 visual rollout。RoboCasa365、MolmoSpaces、OmniGibson 和
BEHAVIOR-1K 先记录实验 metadata 和 dry-run report。

## 工具总览

| 工具 | 本地环境 | Viewer 状态 | 主要验证方式 |
| --- | --- | --- | --- |
| AI2-THOR | `.venv-ai2thor` | Unity 交互 viewer + 鼠标 UI | Unity 窗口、PPM 截图 |
| Habitat | `.venv-habitat` | 可视化 artifact | RGB PNG |
| ManiSkill | `.venv-maniskill` | 可视化 artifact | MP4 |
| RoboCasa365 | `.venv-robocasa365` | 可视化 artifact | MuJoCo EGL RGB PNG |
| MolmoSpaces | `.venv-molmospaces` | 可视化 artifact | MuJoCo RGB PNG |
| OmniGibson | `.venv-omnigibson` | Isaac/OmniGibson 交互 viewer gate | viewer launch proof |
| BEHAVIOR-1K | `.venv-omnigibson` | 委托 OmniGibson viewer | delegated viewer proof |

## AI2-THOR

### 检查

```bash
.venv-ai2thor/bin/python -m simtools doctor ai2thor
python -m simtools run ai2thor --mode smoke --dry-run --no-save-report
```

### 启动和加载

快速验证 Unity 能启动并退出：

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768 --max-actions 0
```

启动终端控制的 Unity viewer：

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768
```

启动鼠标交互 UI：

```bash
./scripts/view_ai2thor_ui.sh FloorPlan1 --width 1024 --height 768 --port 8502
```

浏览器打开：

```text
http://localhost:8502
```

切换场景时替换 scene 名称：

```bash
./scripts/view_ai2thor.sh FloorPlan201
./scripts/view_ai2thor.sh FloorPlan301
./scripts/view_ai2thor.sh FloorPlan401
```

常用 iTHOR 场景：

| 房间 | 场景 |
| --- | --- |
| 厨房 | `FloorPlan1` 到 `FloorPlan30` |
| 客厅 | `FloorPlan201` 到 `FloorPlan230` |
| 卧室 | `FloorPlan301` 到 `FloorPlan330` |
| 浴室 | `FloorPlan401` 到 `FloorPlan430` |

### 操作

终端 viewer 常用命令：

| 输入 | 动作 |
| --- | --- |
| `w` | MoveAhead |
| `s` | MoveBack |
| `a` | RotateLeft |
| `d` | RotateRight |
| `u` | LookUp |
| `j` | LookDown |
| `shot` | 保存截图 |
| `help` | 查看控制 |
| `quit` | 退出 |

鼠标 UI 可使用按钮移动、旋转、俯仰，选择可见物体后执行 `Pick up`、`Open`、`Close`、`Toggle on/off`、`Put held object`、`Save screenshot`。

### 产物

```text
.simtools/artifacts/ai2thor/
```

## Habitat

### 检查

```bash
python -m simtools doctor habitat
python -m simtools run habitat --mode smoke --no-save-report
```

### 启动和加载

Habitat 当前通过官方 test scene 渲染 RGB 图片作为可视化验证：

```bash
python -m simtools view habitat --execute --scene skokloster-castle --width 640 --height 480
```

加载目标：

```text
habitat_test_scenes/skokloster-castle.glb
```

### 操作

当前 SimTools 封装的是可复现渲染路径，不是人工交互窗口。修改 `--scene`、`--width`、`--height` 后重新运行即可生成新的视觉产物。

### 产物

```text
.simtools/artifacts/habitat/skokloster-castle_rgb.png
```

## ManiSkill

### 检查

```bash
python -m simtools doctor maniskill
python -m simtools run maniskill --mode smoke --no-save-report
```

### 启动和加载

渲染 PickCube-v1 任务视频：

```bash
.venv-maniskill/bin/python -m simtools view maniskill --execute --scene PickCube-v1
```

### 操作

当前 SimTools 使用 ManiSkill 官方随机动作 demo 生成 MP4，用于验证环境、任务加载、渲染和视频输出链路。人工 GUI viewer 仍保持 opt-in，不在测试中启动。

### 产物

```text
.simtools/artifacts/maniskill/videos/0.mp4
```

## RoboCasa365

### 检查

```bash
python -m simtools doctor robocasa365
python -m simtools run robocasa365 --mode smoke --no-save-report
```

### 启动和加载

渲染 Kitchen 场景：

```bash
python -m simtools view robocasa365 --execute --scene Kitchen --width 640 --height 480
```

### 操作

当前路径使用 MuJoCo EGL 离屏渲染，重点验证 RoboCasa/robosuite/MuJoCo、本地 kitchen assets 和 RGB 输出。更复杂的人类交互或策略控制应放在后续专用 adapter 中。

### 产物

```text
.simtools/artifacts/robocasa365/kitchen_rgb.png
```

## MolmoSpaces

### 检查

```bash
python -m simtools doctor molmospaces
python -m simtools run molmospaces --mode smoke --no-save-report
```

### 启动和加载

渲染 iTHOR FloorPlan1：

```bash
python -m simtools view molmospaces --execute --scene FloorPlan1 --width 640 --height 480
```

### 操作

当前路径验证 MolmoSpaces、MuJoCo、资源缓存和 RGB 渲染。切换场景时使用 `--scene`，但前提是对应资源已经显式获取到本地缓存。

### 产物

```text
.simtools/artifacts/molmospaces/floorplan1_rgb.png
.simtools/artifacts/molmospaces/floorplan1_rgb_camera.png
```

## OmniGibson

### 检查

```bash
python -m simtools doctor omnigibson
python -m simtools run omnigibson --mode smoke --no-save-report
```

检查 CUDA：

```bash
.venv-omnigibson/bin/python -s -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
```

期望：

```text
True 1
```

### 启动和加载

启动真实 OmniGibson viewer gate：

```bash
python -m simtools view omnigibson --execute
```

该命令会启动 `.venv-omnigibson` 中的：

```bash
python -m omnigibson.examples.robots.robot_control_example --quickstart
```

### 操作

OmniGibson 官方 quickstart viewer 是交互式长期运行进程。SimTools 会等待 readiness marker，例如：

```text
Simulation App Startup Complete
Pressed None. Action:
```

看到这些 marker 后，SimTools 在验证 timeout 后返回：

```text
status: passed
timed_out: true
```

这里的 timeout 不是失败，而是说明 viewer 已进入交互循环。真实人工操作请在启动出的 OmniGibson/Isaac 窗口中按官方示例提示进行。

### 产物

```text
.simtools/artifacts/omnigibson/viewer_launch_proof_20260525.json
```

## BEHAVIOR-1K

### 检查

```bash
python -m simtools doctor behavior1k
python -m simtools run behavior1k --mode smoke --no-save-report
```

### 启动和加载

BEHAVIOR-1K 复用 `.venv-omnigibson`，可视化委托给 OmniGibson viewer gate：

```bash
python -m simtools view behavior1k --execute
```

期望：

```text
status: passed
viewer_status: delegated_to_omnigibson
```

如需打开实际 viewer：

```bash
python -m simtools view omnigibson --execute
```

### 操作

当前 SimTools 对 BEHAVIOR-1K 的定位是任务/数据集/BDDL 依赖验证，并将可视化交给 OmniGibson。也就是说，BEHAVIOR-1K 的视觉入口不是单独窗口，而是 OmniGibson 的已验证 viewer。

### 产物

```text
.simtools/artifacts/omnigibson/viewer_launch_proof_20260525.json
```

## 完整测试流程

轻量项目验证，不启动真实 GUI：

```bash
pytest
python -m compileall -q src simtools tests
python -m simtools validate --json
python -m simtools real-status --strict
python -m simtools experiments list
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools runs list
git diff --check
```

7 个工具 smoke：

```bash
python -m simtools run ai2thor --mode smoke --dry-run --no-save-report
python -m simtools run habitat --mode smoke --no-save-report
python -m simtools run maniskill --mode smoke --no-save-report
python -m simtools run robocasa365 --mode smoke --no-save-report
python -m simtools run molmospaces --mode smoke --no-save-report
python -m simtools run omnigibson --mode smoke --no-save-report
python -m simtools run behavior1k --mode smoke --no-save-report
```

真实 viewer / 可视化验证：

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768 --max-actions 0
python -m simtools view habitat --execute --scene skokloster-castle --width 640 --height 480
.venv-maniskill/bin/python -m simtools view maniskill --execute --scene PickCube-v1
python -m simtools view robocasa365 --execute --scene Kitchen --width 640 --height 480
python -m simtools view molmospaces --execute --scene FloorPlan1 --width 640 --height 480
python -m simtools view omnigibson --execute
python -m simtools view behavior1k --execute
```

## 常见问题

### 为什么有些工具没有人工交互窗口？

SimTools 的 `real_viewer` 标准是“真实本地可运行并有可验证视觉输出”。AI2-THOR 和 OmniGibson 有交互式 viewer；Habitat、ManiSkill、RoboCasa365、MolmoSpaces 当前以 PNG/MP4 artifact 作为可视化验证路径。

### 为什么 OmniGibson 返回 timeout 仍然算 passed？

OmniGibson quickstart viewer 会进入长期交互循环。SimTools 检测到 readiness marker 后会停止等待并返回 `passed`，避免命令永久挂住。

### 为什么不能自动下载 BEHAVIOR/OmniGibson 数据集？

该数据集涉及 EULA 和大体积资产。SimTools 不自动接受 EULA，不自动下载大数据集。当前仓库中的 verified 状态基于用户已经完成的本地数据准备。

### 如何确认所有工具仍然 ready？

```bash
python -m simtools real-status --strict
```

输出应包含：

```text
Real-ready tools: 7/7
```
