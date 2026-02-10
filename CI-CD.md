## CI/CD – DevOps Notes API

מסמך זה מסביר איך ה-Pipeline עובד, אילו Secrets / Variables צריך ב-GitHub,
ואיך תהליך ה-CI/CD מרים תשתית ואפליקציה ב-AWS בצורה אוטומטית.

---

### 1. טריגר – מתי ה-Workflow רץ?

קובץ ה-Workflow נמצא ב:

- `.github/workflows/deploy-on-merge.yml`

הוא רץ בשני מקרים:

- **`push` ל-`main`** – אחרי ש-PR מוזג זה ה-flow המלא: CI + CD.
- **`pull_request` ל-`main`** – מריץ רק CI (בדיקת health), בלי CD.

---

### 2. שלב CI – בדיקה של האפליקציה

Job בשם **`ci`**:

- מריץ Runner מסוג `ubuntu-latest`.
- מבצע:
  - `actions/checkout` – הורדת הקוד.
  - `actions/setup-python` – הגדרת Python (3.11).
  - `pip install -r requirements.txt` – התקנת Flask ותלויות.
  - הרצת האפליקציה עם `APP_PORT=8000` וביצוע `curl` לנתיב `/health`.

אם `/health` לא מחזיר 200 – ה-Job נכשל, ואין מעבר ל-CD.

> האפליקציה תומכת בברירת מחדל ל-`APP_PORT` (8000), כך שאפשר להריץ גם בלי env,
> אבל ב-CI אנחנו מגדירים אותו מפורשות לצורך בהירות.

---

### 3. שלב CD – הרמת תשתית ב-AWS

Job בשם **`cd`**:

- תלוי ב-`ci` (`needs: ci`).
- רץ רק על `push` ל-`main` (לא על `pull_request`).  
  `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`

הוא משתמש ב-AWS CLI כדי:

1. **להתקין AWS CLI** על ה-Runner.
2. **להכין סקריפט User Data** מתוך הקובץ `scripts/ec2-userdata.sh`:
   - מחליף את ה-placeholder `__REPO_URL__` בכתובת ה-Repo האמיתית (`https://github.com/<owner>/<repo>.git`).
3. **ליצור / לעדכן Security Group**:
   - קבוצה בשם `devops-notes-api-sg`.
   - פתיחת פורט `8000/tcp` מהאינטרנט (`0.0.0.0/0`) לאפליקציה.
   - פתיחת פורט `22/tcp` ל-SSH (לבחירתכם – אפשר לצמצם CIDR בקלות).
4. **לוודא קיום Key Pair** בשם `devops-notes-api-key` (לצורך SSH אם צריך).
5. **לסיים instance קיים (Replace on deploy):**
   - מחפשים instance עם התג `Name=devops-notes-api` במצב running או pending.
   - אם נמצא – מריצים `terminate-instances` ומחכים לסיום (`aws ec2 wait instance-terminated`).
   - כך בכל push ל-`main` יש **מכונה אחת** עם התג הייחודי, והגרסה החדשה מחליפה את הקודמת.
6. **להריץ EC2 חדש** עם `aws ec2 run-instances` באותו תג (`Name=devops-notes-api`) ותוך שימוש ב-User Data שהוכן.

כך:

- ה-Pipeline הוא ה-Actor שיוצר את התשתית; בכל deploy אנחנו **מחליפים** instance קיים בחדש (תג ייחודי → חיפוש → מחיקה → יצירה).
- ה-Instance עצמו מרים את האפליקציה דרך User Data.

---

### 4. סקריפט ה-User Data (scripts/ec2-userdata.sh)

הקובץ נמצא ב:

- `scripts/ec2-userdata.sh`

תפקידו:

1. לקבל את `REPO_URL` (מוחלף ע"י ה-Workflow).
2. להתקין:
   - `python3`
   - `python3-pip`
   - `git`
3. לבצע `clone` של ה-repo לנתיב `/opt/devops-notes-api` (או `git pull` אם כבר קיים).
4. להריץ:
   - `pip3 install -r requirements.txt`
   - `APP_PORT=8000 nohup python3 app.py &`

כלומר:

- **Pipeline** – יוצר EC2 ומעביר User Data.
- **EC2** – מריץ את ה-bootstrap ומעלה את Flask.

---

### 5. Secrets ו-Variables נדרשים ב-GitHub

יש להגדיר ב-Repository ב-GitHub (Settings → Secrets and variables → Actions):

#### Secrets

- **`AWS_ACCESS_KEY_ID`** – מפתח גישה של IAM User או Role.
- **`AWS_SECRET_ACCESS_KEY`** – ה-Secret key התואם.
- **`AWS_REGION`** – לדוגמה: `eu-central-1` / `us-east-1`.

המשתמש ב-AWS צריך לפחות הרשאות ל-EC2 עבור:

- `ec2:RunInstances`
- `ec2:DescribeInstances`
- `ec2:CreateSecurityGroup`
- `ec2:DescribeSecurityGroups`
- `ec2:AuthorizeSecurityGroupIngress`
- `ec2:CreateKeyPair`
- `ec2:DescribeKeyPairs`

#### Variables

- **`AWS_AMI_ID`** – מזהה ה-AMI של מערכת ההפעלה שתשמש ל-EC2 (למשל Ubuntu LTS).
  - לדוגמה: `ami-0123456789abcdef0`
  - את הערך בוחרים מתוך AWS Console בהתאם ל-region.

> הערה: ה-Workflow בודק ש-`AWS_AMI_ID` הוגדר, ואם לא – נכשל עם הודעה ברורה
> כדי שהסטודנט יזכור להגדיר אותו.

---

### 6. איך לבדוק שהכול עובד?

1. ודאו שכל ה-Secrets / Variables מוגדרים כנדרש.
2. צרו Branch, בצעו שינוי קטן בקוד, ופתחו PR בעזרת `gh pr create`.
3. לאחר Review ו-Merge ל-`main`, יווצר אירוע `push`:
   - GitHub Actions יריץ קודם את Job ה-CI.
   - אם הוא מצליח – ירוץ Job ה-CD וירים EC2.
4. לאחר מספר דקות:
   - מצאו את ה-Instance ב-AWS Console (חפשו לפי ה-Tag Name: `devops-notes-api`).
   - ודאו שה-Security Group פתוח על פורט 8000 ל-0.0.0.0/0 (או לטווח המצומצם שבחרתם).
   - פנו אל `http://<public-ip>:8000/health` וצפו לקבל `{ "status": "ok" }`.

כך הסטודנט רואה קצה-אל-קצה:

- PR ב-GitHub → Merge → Event → Actions → AWS CLI → EC2 → Flask API חי באינטרנט.

