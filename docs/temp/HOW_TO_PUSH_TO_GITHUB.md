# 如何將您的專案推送到 GitHub (手動操作指南)

這份文件將引導您完成將本地專案推送到共享 GitHub 倉庫的最後幾個步驟。

## 狀況說明 (目前進度)

我們已經完成了以下前置作業：

1.  **下載倉庫**：我們已經將您同學的 GitHub 倉庫 (`https://github.com/yyfsunnyboy/Mathproject`) 下載到您電腦上的一個名為 `cloned_repo` 的子資料夾中。
2.  **整合檔案**：我們已經將您本地的主要專案檔案複製並覆蓋到 `cloned_repo` 資料夾中，這樣 Git 就能偵測到您所做的變更。
3.  **暫存變更**：我們已經執行了 `git add .`，將所有變更都放進了 Git 的「暫存區」，準備進行提交。

我們目前停在 `git commit` (提交) 這個步驟，因為 Git 需要知道您的身分（姓名和 Email）才能記錄是誰做的這次提交。

---

## 接下來的步驟 (您需要手動完成)

請打開您電腦的**命令提示字元 (cmd)** 或 **PowerShell**，然後依照以下指令一步步操作。

### 步驟一：進入正確的資料夾

首先，您需要進入我們準備好的 `cloned_repo` 資料夾。請在命令提示字元中輸入以下指令：

```bash
cd "C:\Users\NICK\Downloads\Mathproject-main (1)\Mathproject-main\cloned_repo"
```

**注意：** `cd` 是切換目錄 (Change Directory) 的意思。

### 步驟二：設定您的 Git 身分

這是我們之前卡住的步驟。請執行以下兩行指令來設定您的姓名和 Email。

**請務必將 `"Your Name"` 和 `"your-email@example.com"` 換成您自己的 GitHub 使用者名稱和 Email。**

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

### 步驟三：提交您的變更 (Commit)

現在您的身分已經設定好了，可以正式提交變更了。執行以下指令：

```bash
git commit -m "整合本機端的專案程式碼"
```

這個指令會將您所有暫存的變更建立成一個「提交紀錄」。

### 步驟四：推送到 GitHub (Push)

這是最後一步，將您的提交紀錄上傳到 GitHub。

```bash
git push origin main
```

**執行這個指令後，可能會發生幾件事：**

1.  **要求登入**：系統可能會跳出一個視窗或在命令列中提示您輸入 GitHub 的使用者名稱和密碼。
    *   **注意**：現在 GitHub 通常要求使用 **Personal Access Token (個人存取權杖)** 來代替密碼。如果您登入失敗，請[參考此連結建立一個權杖](https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)，並在要求輸入密碼時，改為貼上您的權杖。
2.  **權限問題**：如果您看到 `Permission denied` 或 `403` 之類的錯誤，這代表您沒有這個 GitHub 倉庫的寫入權限。您需要請倉庫的擁有者 (`yyfsunnyboy`) 到倉庫的 `Settings` > `Collaborators` 頁面，將您的 GitHub 帳號加入為協作者。

---

完成以上所有步驟後，您的程式碼就成功推送到 GitHub 上了。您可以重新整理 GitHub 頁面來確認。
