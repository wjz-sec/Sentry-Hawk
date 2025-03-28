# Sentry-Hawk

### 介绍 📖

本平台的核心思路是从攻击者视角出发，对企业的网络资产进行全面、深入的审视与管理。通过自动化手段，实现对网络空间的快速测绘，精准识别资产，将资产、漏洞、任务等进行统一管理，以便企业安全团队能够清晰、直观地了解网络安全状态，并迅速做出响应。旨在改变传统安全防护的被动局面，主动出击，提前发现并解决可能被攻击者利用的安全问题，最大程度降低企业网络安全风险。

### 前端地址
[https://github.com/wjz-sec/SentryHawk-Front](https://github.com/wjz-sec/SentryHawk-Front)

### 项目功能 🔨

- 高速端口识别：借助强大的扫描能力，几分钟内可对数百万端口进行扫描，精准识别网络服务类型，让企业清晰了解网络端口的开放情况和服务运行状态。

- 自动域名枚举：自动发现与企业相关的域名，包括主域名、子域名等，防止因域名管理不善而导致的安全漏洞。

- 服务发现：全面探测网络中的各类服务，如 Web 服务、数据库服务、邮件服务等，掌握服务的运行情况和版本信息，为后续的漏洞扫描和风险评估提供基础数据。

- 多协议指纹识别：对多种网络协议进行指纹识别，准确判断协议类型和版本，有助于发现因协议漏洞而带来的安全风险。

- nuclei 漏洞 poc 扫描：利用 nuclei 丰富的漏洞 poc 库，对企业网络资产进行全面扫描，快速发现已知漏洞。

- 手动添加 poc 支持：安全人员可根据企业实际情况，手动添加自定义 poc，对特定的安全隐患进行针对性扫描，提高漏洞检测的灵活性和精准度。

- 漏洞管理：对扫描发现的漏洞进行详细记录和分类，包括漏洞名称、编号、危害等级、生产商等信息。提供漏洞修复建议和跟踪功能，确保漏洞得到及时、有效的处理。

- 资产管理：对企业的网络资产进行统一管理，包括资产的录入、更新、删除等操作。支持资产分类管理，可根据资产类型、所属部门、重要程度等进行分类，方便资产的查找和管理。

- 任务管理：创建、编辑和执行各种扫描任务和安全检查任务。可设置任务的执行时间、频率、扫描范围等参数，实现任务的自动化调度。

- 系统设置：对平台的系统参数进行设置，如扫描参数、数据库连接参数、邮件通知设置等。可根据企业网络环境和安全需求，对平台进行个性化配置。


### 安装使用步骤 📔

- 1.下载
```shell
git clone git@github.com:wjz-sec/Sentry-Hawk.git
```
- 2.安装依赖包 `pip install -r requirements.txt`
- 3.创建迁移文件 `python ./manage.py makemigrations`
- 4.迁移数据库 `python ./manage.py migrate`
- 5.启动服务 `python ./manage.py runserver 0.0.0.0:8000`


### 项目截图 📷

- 登录页：

![login_light](/images/light/login.png)

- 首页：

![home_light](/images/light/home.png)

- 资产管理：

![asset](/images/light/asset.png)

- 任务中心

![scan](/images/light/scan.png)
![scan_add](/images/light/scan_add.png)


### 浏览器支持 🌎

- 本地开发推荐使用 Chrome 最新版浏览器 [Download](https://www.google.com/intl/zh-CN/chrome/)。
- 生产环境支持现代浏览器，不再支持 IE 浏览器，更多浏览器可以查看 [Can I Use Es Module](https://caniuse.com/?search=ESModule)。

| ![IE](https://i.imgtg.com/2023/04/11/8z7ot.png) | ![Edge](https://i.imgtg.com/2023/04/11/8zr3p.png) | ![Firefox](https://i.imgtg.com/2023/04/11/8zKiU.png) | ![Chrome](https://i.imgtg.com/2023/04/11/8zNrx.png) | ![Safari](https://i.imgtg.com/2023/04/11/8zeGj.png) |
| :---------------------------------------------: | :-----------------------------------------------: | :--------------------------------------------------: | :-------------------------------------------------: | :-------------------------------------------------: |
|                   not support                   |                  last 2 versions                  |                   last 2 versions                    |                   last 2 versions                   |                   last 2 versions                   |


### 微信交流群 👨‍👨‍👦‍👦

![wx_group](/images/wx_group.jpg)