# 系统需求文档

## I. 核心系统功能

### A. 生产线集成

- **通信协议**：RS485 模块直接接入 MQTT。
- **生产状态管理**：
  - 开始生产
  - 停止生产
  - 添加一个开关量（用于显示）
- **数据字段（用于显示、存储、分析）**：
  - 生产线编号
  - 生产批号（从下层传输到上层）
  - 氟离子传感器集成
  - 

- 设备独立于生产系统
- 通过 MQTT 上传氟离子浓度数据
- 数据需要在前端显示

### B. 数据采集与存储

- **数据采集频率**：每秒采集一次数据
- **本地数据缓存**：可缓存本地数据 1 天，并上传到上层
- **冷数据存储**：手动冷存储，每年约 30GB

### C. 数据下载与导出

- 所有数据可整体下载
- 支持通过时间段导出（精确到 年-月-日 时:分:秒）
- 导出文件需兼容 Excel

### D. 实时性要求

- 生产数据到前端显示的延迟不超过 **1 秒**



---

## II. 用户管理与权限

### A. 账号登录

- 使用 **用户名 / 密码** 登录认证
- 提供用户管理模块：
  - 创建用户
  - 编辑用户
  - 删除用户

### B. 用户权限管理（RBAC）

- 支持系统自动创建用户
- 支持设置新用户的初始密码
- 权限等级：
  - **超级管理员**：拥有所有权限，包括用户管理
  - **管理员**：可下载日志文件，无法管理用户
  - **普通用户**：仅能查看生产数据，无法下载日志

---

## III. 系统管理与功能

### A. 生产线管理

- 支持最多 **8 条生产线**
- 支持手动添加或删除生产线

### B. 智能化功能

- **数据分析**：利用历史及实时数据，提供生产或维护反馈
- **设备运行状态统计**：
  - 运行总时长百分比
  - 总运行时间
- **能源消耗统计**：
  - 当前电流
  - 总耗电量
  - 能源使用情况
- **数据可视化**：生成图表进行展示

---

## IV. 用户界面与体验

### A. 移动端支持

- 提供移动端观测界面
- 无需下载数据或进行远程控制

### B. 主页风格

- 风格定位：**科技感、高大上**

---

## V. 技术栈

### A. 后端

- 使用 **Python FastAPI**

### B. 前端

- 使用 **Next.js**
- 避免组态（HMI）风格，界面更现代化
