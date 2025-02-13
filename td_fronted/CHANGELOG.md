---
title: 更新日志
spline: explain
toc: false
docClass: timeline
---

## 🌈 0.12.0 `2025-01-06` 
### 🐞 Bug Fixes
- `Vue`: 修复升级至 Vue 3.4 及 3.5 的生产模式下的问题 @uyarn ([#796](https://github.com/Tencent/tdesign-vue-next-starter/pull/796))
### 📈 Performance
- defineProps改为Vue3.5解构语法 @liect ([#799](https://github.com/Tencent/tdesign-vue-next-starter/pull/799))

## 🌈 0.11.0 `2024-11-06` 
### 🚀 Features
- `feat`: 调整默认lock文件配置 @timi137137 ([#717](https://github.com/Tencent/tdesign-vue-next-starter/pull/717))
- `Router`: 路由跳转携带参数 @SuxueCode ([#720](https://github.com/Tencent/tdesign-vue-next-starter/pull/720))
- `feat`: 新增菜单自动折叠 @RSS1102 ([#744](https://github.com/Tencent/tdesign-vue-next-starter/pull/744))
### 🐞 Bug Fixes
- `breadcrumb`: 修复多层级路由指向错误 @lz6060788 ([#749](https://github.com/Tencent/tdesign-vue-next-starter/pull/749))
- `deps`: 修正因锁文件错误导致的编译失败 @timi137137 ([#777](https://github.com/Tencent/tdesign-vue-next-starter/pull/777))
### 🚧 Others
- `revert`: 回退Vue 3.3 @timi137137 ([#709](https://github.com/Tencent/tdesign-vue-next-starter/pull/709))
- build(deps-dev): bump @types/lodash from 4.14.202 to 4.17.6 @dependabot[bot] ([#732](https://github.com/Tencent/tdesign-vue-next-starter/pull/732))
- build(deps): bump tdesign-vue-next from 1.9.3 to 1.9.9 @dependabot[bot] ([#748](https://github.com/Tencent/tdesign-vue-next-starter/pull/748))

## 🌈 0.10.0 `2024-04-02`
### 🚀  Features
- 优化整体代码风格 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/638 https://github.com/Tencent/tdesign-vue-next-starter/pull/650 https://github.com/Tencent/tdesign-vue-next-starter/pull/680 https://github.com/Tencent/tdesign-vue-next-starter/pull/684)
- 新增侧边栏颜色切换 by @qingmang @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/681)
- 使用 `t-descriptions` 替换详情页代码 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/707)

### 🐞 Bug Fixes
- 修复国际化配置缺失 by @liweijie0812 @timi137137  (https://github.com/Tencent/tdesign-vue-next-starter/pull/614 https://github.com/Tencent/tdesign-vue-next-starter/pull/632 https://github.com/Tencent/tdesign-vue-next-starter/pull/636)
- 修复 `ECharts` 图例缩放错误 by @lcosmos (https://github.com/Tencent/tdesign-vue-next-starter/pull/622)
- 修复 `ECharts` 图样文字重叠 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/682)
- 修复 `husky` 找不到npx命令 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/635)
- 修复路由切换时过渡动画异常 by @mokeyjay (https://github.com/Tencent/tdesign-vue-next-starter/pull/666)
- 修复mock环境下获取菜单异常  by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/630)

## 🌈 0.9.0 `2023-10-04`
### 🚀  Features
- 新增内置国际化配置，支持中英切换 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/607)
- 新增 node 版本要求 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/605)

### 🐞 Bug Fixes
- 修复`t-link`在设置主题色时的样式异常 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/565)
- 移除无效的 `stylelint` 规则 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/584)
- 修复部分内置样式对 button 的影响 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/586)
- 修正部分模板页面卡片组件操作插槽用法 by @ngyyuusora (https://github.com/Tencent/tdesign-vue-next-starter/pull/587)
- 修改部分错别字 by @dufu1991 (https://github.com/Tencent/tdesign-vue-next-starter/pull/600)
- 优化”暂无通知“的样式问题 by @Summer-Shen (https://github.com/Tencent/tdesign-vue-next-starter/pull/604)

## 🌈 0.8.0 `2023-07-12`
### ❗️ BREAKING CHANGES
- 重构内置 axios 及请求相关逻辑，新增接口级防抖节流 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/556)
- 更新 stylelint 相关配置 移除 stylelint-less 依赖  by @timi137137 @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/553 https://github.com/Tencent/tdesign-vue-next-starter/pull/558)

### 🐞 Bug Fixes
- 修复路由跳转表头闪烁的问题 by @tanhh326 (https://github.com/Tencent/tdesign-vue-next-starter/pull/550)
- 修复筛选列表页，搜索合同状态显示object的异常 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/559)

## 🌈 0.7.7 `2023-06-27`
### 🚀  Features
- Vite版本升级至4 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/533)
- 组件库版本升级至 1.3.8 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/548)
- Axios支持格式化Params by @ngyyuusora (https://github.com/Tencent/tdesign-vue-next-starter/pull/544)

### 🐞 Bug Fixes
- 修复登出后路由重置问题 by @ngyyuusora (https://github.com/Tencent/tdesign-vue-next-starter/pull/545)
- 修复请求时204无内容判断异常 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/539)

## 🌈 0.7.6 `2023-05-30`
### 🚀  Features
- 移除了将所有文件一并提交的代码 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/515)
- 组件库版本升级至 1.3.4 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/518)
- 禁止隐式Any类型声明 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/519)

### 🐞 Bug Fixes
- 修复多标签页中保活异常问题 by @ngyyuusora (https://github.com/Tencent/tdesign-vue-next-starter/pull/523)
- 修复store存储token读取异常问题 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/526)

## 🌈 0.7.5 `2023-05-18`
### 🚀  Features
- 站点引入主题生成器插件，支持在页面模板站点尝试及预览不同主题的效果 by @uyarn @timi137137 
- 优化路由守卫获取菜单异常的处理，跳转登录页并弹窗提示 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/502)
- 规范不同系统中的结束符 by @SpringHgui @yunxifd (https://github.com/Tencent/tdesign-vue-next-starter/pull/505)

### 🐞 Bug Fixes
- 修复无法将通知设为未读的缺陷 by @izoyo (https://github.com/Tencent/tdesign-vue-next-starter/pull/511)
- 修复 store 中并未对 localStorage 的 TOKEN_NAME 键进行赋值的缺陷 by @SpringHgui (https://github.com/Tencent/tdesign-vue-next-starter/pull/504)

## 🌈 0.7.4 `2023-04-13`
### 🚀  Features
- Eslint 新增 `simple-import-sort` 插件规范引入 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/464)
- 菜单路由支持`keepAlive`参数控制页面是否开启缓存 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/470)
- 标签页可配置禁止拖拽 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/454)

### 🐞 Bug Fixes
- 修复拼音输入的问题 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/421)
- 修复同级路由路径存着相同启始字符时菜单高亮异常的问题 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/450)
- 修复部分`devDependencies`错误配置在`dependencies`的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/456)
- 修复请求出错重试后触发两次回调的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/458)
- 修复多级菜单高亮问题 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/459)

## 🌈 0.7.3 `2023-03-15`
### 🚀  Features
- 优化菜单生成 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/413)
- 优化修改主题色的逻辑 by @hzgotb (https://github.com/Tencent/tdesign-vue-next-starter/pull/428)
- 接口配置硬编码调整到环境变量 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/445)

### 🐞 Bug Fixes
- 修复修改.html文件stylelint检查出错的问题 by @hmingv (https://github.com/Tencent/tdesign-vue-next-starter/pull/436)
- 删除废弃的globEager by @hmingv (https://github.com/Tencent/tdesign-vue-next-starter/pull/439)

## 🌈 0.7.2 `2023-02-21`
### 🚀  Features
- 优化菜单生成逻辑 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/413)
- 多标签Tab栏支持拖拽排序 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/426)

### 🐞 Bug Fixes
- 修复列表页示例拼音输入的问题 by @liweijie0812 (https://github.com/Tencent/tdesign-vue-next-starter/pull/421)
- 优化登录页及个人中心页样式 by @Wen1kang (https://github.com/Tencent/tdesign-vue-next-starter/pull/415)
- 修复 tdesign-vue-next 1.0.8版本由于引入Teleport后drawer内样式穿透失效引起的样式错乱 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/425)

## 🌈 0.7.1 `2023-02-08`
### 🐞 Bug Fixes
- 修复环境变量的问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/399)
- 修复 stylelint 14的配置问题 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/404)
- 修复dashboard&layout相关样式Bug by @Wen1kang (https://github.com/Tencent/tdesign-vue-next-starter/pull/403)
- 修复菜单图标样式问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/402)

## 🌈 0.7.0 `2023-01-16`
### ❗️ BREAKING CHANGES
- 移除所有内置主题色相关代码，全部通过 `tvision-color` 计算获取，调整颜色相关方法的目录结构 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/392)
- 新增后端路由权限相关代码，默认菜单路由权限改为后端控制，具体使用可参考文档 [权限控制](https://tdesign.tencent.com/starter/docs/vue-next/permission-control) by @timi137137 @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/394)

### 🚀  Features
- 支持任意颜色作为初始化主题颜色 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/392)
- 升级 `tvision-color` 至1.5.0 使用新的`getColorGradations`方法，修正部分选择的过曝主题色 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/392)
- 升级相关依赖 `vite`需升级至`3.0`以上，支持图标后端配置等场景需求  by @timi137137 @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/394)

### 🐞 Bug Fixes
- 修复自定义颜色切换明亮暗黑模式时无法沿用的缺陷 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/392)

`Tips: 此次发布 较 0.6.x 版本 删除了此前大量内置项目的色彩生成逻辑，权限控制相关逻辑也发生巨大变动 若打开预览无法访问请清除 localStorage 等缓存再尝试 跟进升级请慎重`

## 🌈 0.6.1 `2022-12-19`
### 🚀  Features
- 优化登录跳转支持回跳带query参数的页面 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/374)
- 引入类型声明为type 方便CLI工具做JS版本转换处理 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/375)
- 新增打开外部页面（内嵌及外链）配置及示例 by @dianjie (https://github.com/Tencent/tdesign-vue-next-starter/pull/377)
- 支持编辑器使用`volar`提示组件名称及对应API  by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/378)

### 🐞 Bug Fixes
- 修复DateRangePicker组件内分页样式显示异常 by @wandoupeas (https://github.com/Tencent/tdesign-vue-next-starter/pull/373)
- 修复组件升级引入的布局高度问题 by @dianjie (https://github.com/Tencent/tdesign-vue-next-starter/pull/367)

## 🌈 0.6.0 `2022-11-25`
### ❗️ BREAKING CHANGES
- 废弃大量内置`less variables`, 尺寸、色彩、字体、圆角及阴影统一使用组件库内置变量 具体变量可参考 [Design Token](https://tdesign.tencent.com/starter/docs/vue-next/design-token) by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/365)
- 升级默认主题色的配色方案  组件库升级至0.24.9及请参照改动 @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/365)

### 🐞 Bug Fixes
- 修复组件库升级至0.24.8及以上由于头部高度变化导致部分导航模式样式异常的问题 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/365)
- 避免 Content-Type 被改为 `text/plain` by @TonyLuo (https://github.com/Tencent/tdesign-vue-next-starter/pull/361)

## 🌈 0.5.6 `2022-11-18`
### 🐞 Bug Fixes
- 修正退出后 userStore.userInfo 存在残留的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/357)
- 修复0.5.5 头部高度在多标签页的样式异常 by @uyarn @dodu2014 (https://github.com/Tencent/tdesign-vue-next-starter/pull/360)

## 🌈 0.5.5 `2022-11-16`
### 🚀  Features
- 升级axios至1.0版本 by @dependabot (https://github.com/Tencent/tdesign-vue-next-starter/pull/351)
- 升级tdesign-vue-next至0.24版本 支持尺寸类Design Token 部分样式需调整 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/355)

### 🐞 Bug Fixes
- 修复导航布局`side`模式下小屏显示问题 by @dianjie (https://github.com/Tencent/tdesign-vue-next-starter/pull/348)

## 🌈 0.5.4 `2022-10-26`
### 🚀  Features
- 升级`vue-router`至4.1+ by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/341)
- 升级`vue-tsc`至 1.0+ by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/341)

### 🐞 Bug Fixes
- 修复系统设置事件绑定位置的错误(#344) by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/345)

## 🌈 0.5.3 `2022-10-18`
### 🚀  Features
- 项目通用 less vars 设置为全局变量，不需要再手动引入 by @dianjie (https://github.com/Tencent/tdesign-vue-next-starter/pull/327)
- 升级组件库依赖至0.24.2 优化下拉菜单高度及多级结构 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/339)

## 🌈 0.5.2 `2022-09-27`
### 🚀  Features
- 升级组件库依赖至0.23 修复切换页面等场景下表格吸附效果未重新计算导致的样式异常 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/322)
- 增加urlPrefix判断 避免undefined拼接到url导致请求无效 @kerwin612 (https://github.com/Tencent/tdesign-vue-next-starter/pull/311)

### 🐞 Bug Fixes
- 修复`Sidenav`参数错误导致跟随系统样式异常的问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/315)
- 修复user持久化导致的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/316)
- 修复路径重复拼接的问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/319)

## 🌈 0.5.1 `2022-09-14`
### 🚀  Features
- 多标签页的右键操作扩展支持非当前页进行操作 by @zhangpaopao0609 @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/297)
- 使用插件将store数据持久化 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/291)
- add README in English by @paiakarit @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/301 https://github.com/Tencent/tdesign-vue-next-starter/pull/305)

### 🐞 Bug Fixes
- 解决当打开多个标签后 退出会报错的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/293)
- 修复底部版权信息及面包屑导航垂直居中问题 by @zengqiu (https://github.com/Tencent/tdesign-vue-next-starter/pull/299 https://github.com/Tencent/tdesign-vue-next-starter/pull/298)
- 修复浏览器不兼容页中浏览器推荐卡片遮挡页脚信息问题 by @zengqiu (https://github.com/Tencent/tdesign-vue-next-starter/pull/303)

## 🌈 0.5.0 `2022-09-06`
### ❗️ BREAKING CHANGES
- jsx代码全部改完sfc(.vue) 统一全部页面及组件用sfc编写 by @zhangpaopao0609 (https://github.com/Tencent/tdesign-vue-next-starter/pull/279)

### 🐞 Bug Fixes
- 修复混合模式下选择分割菜单再点击顶部登录页出现空白页的异常 by @setli (https://github.com/Tencent/tdesign-vue-next-starter/pull/287)
- 修复顶部布局头部缺失的问题 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/292)
- 修复侧边栏折叠时版本号前显示 false 问题 by @zengqiu (https://github.com/Tencent/tdesign-vue-next-starter/pull/294)

## 🌈 0.4.1 `2022-08-30`
### 🚀  Features
- 升级tdesign-vue-next至0.20.2版本 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/276)
- tabs-router 支持存储路由的参数 by @dodu2014 (https://github.com/Tencent/tdesign-vue-next-starter/pull/269)

### 🐞 Bug Fixes
- 修复更新vue-router版本后的遗留问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/261)
- 修正请求时formData类型的数据会被过滤的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/272)
- 修正store内数据提前被清理导致报错的问题 by @PDieE (https://github.com/Tencent/tdesign-vue-next-starter/pull/274)

## 🌈 0.4.0 `2022-08-08`
### ❗️ BREAKING CHANGES
- 升级vue-router版本 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/257)

### 🚀 Features
- 处理代码中不符合规范的文件和写法 升级相关依赖 增加更多的规范 by @uyarn (https://github.com/Tencent/tdesign-vue-next-starter/pull/243)
- 新增支持子菜单是否默认展开的配置 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/245)
- 升级组件库依赖至0.19.0 组件圆角样式有变化 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/252)

### 🐞 Bug Fixes
- 修复变更颜色/模式时出现页面卡死的异常 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/254)
- 修复侧边栏开合时图表没有刷新的问题 by @timi137137 (https://github.com/Tencent/tdesign-vue-next-starter/pull/253)
- 填补登录页面缺失的手机号输入框及相关逻辑 by @hxywuya (https://github.com/Tencent/tdesign-vue-next-starter/pull/255)

## 🌈 0.3.6 `2022-07-18`
### 🚀  Features
- 升级tdesign-vue-next至0.18.0版本 
- 增加apis目录 管理项目中使用到的api by @timi137137 ([#221](https://github.com/Tencent/tdesign-vue-next-starter/pull/221))
- router调整为自动导入 by @timi137137 ([#223](https://github.com/Tencent/tdesign-vue-next-starter/pull/223))

### 🐞 Bug Fixes
- 部分选择器未随自定义样式前缀更改 by @wandoupeas ([#229](https://github.com/Tencent/tdesign-vue-next-starter/pull/229))

## 🌈 0.3.5 `2022-06-27`
### 🚀  Features
- 调整类型相关问题的项目结构 by @timi137137 ([#184](https://github.com/Tencent/tdesign-vue-next-starter/pull/184))
- 改造请求封装相关代码 by @timi137137 ([#185](https://github.com/Tencent/tdesign-vue-next-starter/pull/185))

### 🐞 Bug Fixes
- 修复首页TAB关闭其他时的异常 by @SadWood ([#180](https://github.com/Tencent/tdesign-vue-next-starter/pull/180))
- 修复升级0.16版本后自定义设置中选项样式的异常 by @uyarn ([#193](https://github.com/Tencent/tdesign-vue-next-starter/pull/193))

## 🌈 0.3.4 `2022-06-17`
### 🚀  Features
- 升级组件库依赖至0.16.0，`datepicker`、`dialog`组件的使用请参考改动 by @pengYYYYY ([#174](https://github.com/Tencent/tdesign-vue-next-starter/pull/174))

### 🐞 Bug Fixes
- 修复退出登录之后重新登陆新增了空Tab的缺陷 by @kerwin612 ([#168](https://github.com/Tencent/tdesign-vue-next-starter/pull/168))
- 修复切换多标签Tab页时的告警问题 by @kerwin612 ([#173](https://github.com/Tencent/tdesign-vue-next-starter/pull/173))

## 🌈 0.3.3 `2022-06-02`
### 🚀  Features
- 模板中使用颜色变量全部改造为CSS Token by @kerwin612 ([#157](https://github.com/Tencent/tdesign-vue-next-starter/pull/157))

### 🐞 Bug Fixes
-  升级组件库至0.15.4，修复菜单字重及顶部菜单箭头翻转方向、暗黑模式的颜色问题 by @uyarn @leejim ([#159](https://github.com/Tencent/tdesign-vue-next-starter/pull/159))  [tdesign-vue-next#916](https://github.com/Tencent/tdesign-vue-next/pull/916)

## 🌈 0.3.2 `2022-05-27`
### 🚀  Features
- 升级组件库依赖至0.15.1 by @pengYYYYY ([#154](https://github.com/Tencent/tdesign-vue-next-starter/pull/154))
- 增加多标签页增加支持指定路由不缓存的功能 by @uyarn ([#155](https://github.com/Tencent/tdesign-vue-next-starter/pull/155))

### 🐞 Bug Fixes
- 修复页面滚动条不重置的问题 by @kerwin612 ([#158](https://github.com/Tencent/tdesign-vue-next-starter/pull/158))
- 修复多标签页关闭逻辑缺陷 by @uyarn ([#156](https://github.com/Tencent/tdesign-vue-next-starter/pull/156))

## 🌈 0.3.1 `2022-05-13`
### 🚀  Features
- lint新增style scoped提示 by @kerwin612 ([#138](https://github.com/Tencent/tdesign-vue-next-starter/pull/138))
- 新增维护中页面 by @uyarn ([#146](https://github.com/Tencent/tdesign-vue-next-starter/pull/146))
- 升级组件库依赖至0.14+ 

### 🐞 Bug Fixes
- 修复多标签Tab页关闭左侧，关闭其他可能导致主页标签被删除 by @kerwin612 ([#148](https://github.com/Tencent/tdesign-vue-next-starter/pull/148)) 
- 修复多个滚动列表之间切换时页面不刷新导致的样式缺陷 by @kerwin612 ([#152](https://github.com/Tencent/tdesign-vue-next-starter/pull/152)) 

## 🌈 0.3.0 `2022-04-28`
### 🚀  Features
- 优化菜单选中判断逻辑 by @kerwin612 ([#132](https://github.com/Tencent/tdesign-vue-next-starter/pull/132))
- 升级组件库依赖至0.13 + 版本 by @uyarn ([#133](https://github.com/Tencent/tdesign-vue-next-starter/pull/133))
   - 替换全部Card为`t-card`卡片组件，减少重复代码实现
   - 调整图表相关代码目录结构，图表部分代码调整至所在Page内，减少各页面模块的耦合
   - 调整表格相关代码及展示，增加吸顶功能展示、去除minWidth的使用等 

### 🐞 Bug Fixes
- 修复分步表单页底部居中问题
- 修复顶部菜单栏下拉菜单与表单层级问题

## 🌈 0.2.3 `2022-04-26`
### 🚀  Features
- 补充mock示例 by @kerwin612 ([#127](https://github.com/Tencent/tdesign-vue-next-starter/pull/127)) 

### 🐞 Bug Fixes
- 修复顶部菜单栏未选中项样式问题 by @kerwin612 ([#131](https://github.com/Tencent/tdesign-vue-next-starter/pull/131))
- 修复搜索框样式异常问题 by @kerwin612 ([#130](https://github.com/Tencent/tdesign-vue-next-starter/pull/130))
- 修复顶部布局布局菜单样式问题 by @kerwin612 ([#129](https://github.com/Tencent/tdesign-vue-next-starter/pull/129))

## 🌈 0.2.2 `2022-04-06`
### 🚀  Features
- 支持多标签页支持持久化 by @uyarn ([#111](https://github.com/Tencent/tdesign-vue-next-starter/pull/111))
- 升级组件库依赖tdesign-vue-next至0.11版本 by @pengYYYYY

### 🐞 Bug Fixes
- 修复图表文字颜色异常 by @uyarn ([#112](https://github.com/Tencent/tdesign-vue-next-starter/pull/112))
- 修复mock roles模块错误 by @lscho ([#104](https://github.com/Tencent/tdesign-vue-next-starter/pull/104))

## 🌈 0.2.1 `2022-03-25`
### 🚀  Features
- 新增多标签Tab页功能 ([#98](https://github.com/Tencent/tdesign-vue-next-starter/pull/98))

## 🌈 0.2.0 `2022-03-04`
### 🚀  Features
- pinia替换vuex作为状态管理库 by @PengYYYYY
- 升级组件库依赖tdesign-vue-next至0.9版本

## 🌈 0.1.3 `2022-02-27`
### 🚀  Features
- 使用 `setup script` 重构了页面逻辑

### 🐞 Bug Fixes
- 修复菜单下拉与表格定位冲突

## 🌈 0.1.2 `2022-02-18`
### 🐞 Bug Fixes
- 修复面包屑点击跳转当前页错误的问题 by @ccccpj

## 🌈 0.1.1 `2022-01-27`
### 🐞 Bug Fixes
- 修复表单页检验提示未正常显示的问题

## 🌈 0.1.0 `2022-01-10`
### 🚀  Features
- 升级 `tdesign-vue-next` 版本到 `0.6.3`

### 🐞 Bug Fixes
- 修复一级菜单收起出现多余 `1` 的 bug
- 修复 `time-picker` 的文字覆盖
- 修复版本图表渲染问题
