# 本地RSS源设置指南

## RSSHub简介

RSSHub是一个开源的RSS生成器，可以为各种网站生成RSS订阅源。对于需要访问如淘股吧等网站的RSS内容，我们需要部署RSSHub服务。

## 安装RSSHub

### 方法1：全局安装（推荐）

```bash
# 安装Node.js（如果尚未安装）
# 从 https://nodejs.org/ 下载并安装

# 全局安装RSSHub
npm install -g rsshub
```

### 方法2：使用Docker

```bash
# 拉取RSSHub镜像
docker pull diygod/rsshub

# 运行RSSHub容器
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

## 启动RSSHub服务

### 本地启动

```bash
# 启动RSSHub服务
rsshub

# 服务将在 http://localhost:1200 启动
```

### 指定端口启动

```bash
# 在指定端口启动RSSHub服务
rsshub --port 3000
```

## 访问本地RSS源

启动RSSHub后，可以通过以下URL访问RSS源：

### 淘股吧博客示例
```
http://localhost:1200/taoguba/blog/11056656
```

### 其他常见RSS源
```
# 微博用户
http://localhost:1200/weibo/user/用户ID

# 知乎专栏
http://localhost:1200/zhihu/zhuanlan/专栏ID

# Twitter用户
http://localhost:1200/twitter/user/用户名

# YouTube频道
http://localhost:1200/youtube/channel/频道ID
```

## 验证RSS源可用性

### 使用curl命令验证
```bash
curl -I http://localhost:1200/taoguba/blog/11056656
```

### 使用浏览器验证
直接在浏览器中访问 `http://localhost:1200/taoguba/blog/11056656` 查看是否返回RSS内容。

## 常见问题解决

### 问题1：服务无法启动
**症状**：`rsshub` 命令无响应或报错
**解决方案**：
- 检查Node.js是否正确安装：`node --version`
- 检查端口是否被占用：`lsof -i :1200`
- 尝试使用其他端口：`rsshub --port 3000`

### 问题2：RSS源返回错误
**症状**：访问RSS源返回错误信息
**解决方案**：
- 检查RSSHub是否正常运行
- 验证URL格式是否正确
- 检查目标网站是否可用

### 问题3：访问速度慢
**症状**：获取RSS内容耗时过长
**解决方案**：
- 检查网络连接
- 考虑使用代理（如果需要）
- 避免频繁请求同一RSS源

## 安全注意事项

### 本地访问
- RSSHub默认只监听本地地址，外部无法访问
- 如需外部访问，使用 `--address 0.0.0.0` 参数

### 隐私保护
- RSSHub不会记录用户数据
- 所有请求都是实时生成的

## 与RSS聚合器集成

### 配置RSS聚合器访问本地源
在 `config.yaml` 中添加：

```yaml
sources:
  - name: "淘股吧博客"
    url: "http://localhost:1200/taoguba/blog/11056656"
    category: "股票"
    priority: 1
    enabled: true
```

### 使用Python脚本访问
```python
# 在Python中访问本地RSS源
import requests

url = "http://localhost:1200/taoguba/blog/11056656"
headers = {
    "Accept": "application/xml,text/xml,application/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("成功获取RSS内容")
else:
    print(f"获取失败: {response.status_code}")
```

## 停止RSSHub服务

### 在终端中停止
- 按 `Ctrl+C` 停止正在运行的RSSHub服务

### Docker容器停止
```bash
# 停止RSSHub容器
docker stop rsshub

# 删除容器（可选）
docker rm rsshub
```

## 性能优化建议

- 合理设置请求频率，避免对目标网站造成过大压力
- 使用缓存机制避免重复请求相同内容
- 定期重启RSSHub服务以释放内存