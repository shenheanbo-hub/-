# 加班薪资记录仪（Android）

使用 Python、Kivy 和 Buildozer 编写的离线 Android App。

## 日期识别

- 默认日期直接读取手机系统日期，不调用网络 API。
- 日期选择器完全在 App 内运行，不申请手机日历读取权限。
- 内置 2025、2026 年国务院办公厅公布的节假日和调休上班日。
- 未内置年份按星期判断，识别结果始终可以手动修改。

## 工资计算

时薪 = 月基本工资 ÷ 21.75 ÷ 8。平日、休息日和法定节假日分别按 1.5、2、3 倍计算。

## 获取 APK

打开仓库的 **Actions** → **Build Android APK**。构建完成后，在运行页面底部下载
`overtime-recorder-apk`，解压后即可获得 APK。首次推送到 `main` 会自动开始构建；也可以点击
**Run workflow** 手动重新构建。

数据保存在 App 私有目录，卸载 App 会同时清除数据。

## 永久发布正式 APK

Actions 中普通的 APK 是临时构建产物。需要长期保存正式版本时：

1. 打开 **Actions** → **Build Android APK**。
2. 点击 **Run workflow**。
3. 在 `release_version` 中填写版本号，例如 `v1.2.0`。
4. 点击绿色的 **Run workflow**。

构建成功后，工作流会自动创建 GitHub Release，并把 APK 作为正式版本附件上传。版本号必须使用
`v数字.数字.数字` 格式，且每次发布必须使用新的版本号。Release 中的 APK 不受 Actions
构建产物保留期限影响。
