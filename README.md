<div align="center">
<p>   
   <img src="https://cdn.kagamiz.com/Bilibili-Toolkit/bilibili.png" width="300">
</p>
<h1 align="center">- Bilibili AutoRedPacket -</h1>
<h4 align="center"> _✨ B站直播间自动抢红包 ✨_ </h4>
</div>


### 简介

- 自动搜索有红包直播间,并自动毛取。基于Playwright开发(指堆屎山)。

### 使用

- 使用 Pyinsteller 打包好的 ExE文件

```

双击ExE文件启动即可

```
- 使用 Python 启动

```
pip install -r requirements.txt
python RedPacket.py
```

#### 注意

 - 使用非ExE文件启动,且仅安装了Python-Playwright。第一次启动会自动安装Playwright浏览器组件。

### 配置项

<details>
<summary>展开/收起</summary>

#### `分区`
 - 默认：`虚拟主播`
 - 说明：选择搜索红包的直播分区,默认虚拟主播分区！

#### `搜索排序`
 - 默认：`数量优先`
 - 说明：直播间排序方式,默认数量优先。数量优先：先毛取存在红包数最多的直播间,速度优先：先毛取存在红包数最少的直播间

#### `打开直播间数`
 - 默认：`5`
 - 说明：同时打开的直播间数,请按照自己的电脑性能选择！

#### `最小红包价值`
 - 默认：`0`
 - 说明：限制进行毛取的最小红包价值,输入0则无限制。

#### `忽略的红包价值`
 - 默认：`无`
 - 说明：毛取时将忽略在次设置中的红包价值

#### `显示浏览器`
 - 默认：`不显示`
 - 说明：设置浏览器是否在前台显示
</details>

### 特别感谢

- [B站自动抢红包](https://greasyfork.org/zh-CN/scripts/439169-b%E7%AB%99%E7%9B%B4%E6%92%AD%E8%87%AA%E5%8A%A8%E6%8A%A2%E7%BA%A2%E5%8C%85) B站直播自动抢红包


