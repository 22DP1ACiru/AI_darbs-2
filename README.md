# E-Shop parauga projekts izmantošanai mācību uzdevumam

Šis ir vienkāršs Flask e-veikala projekts, kas paredzēts kā sākumpunkts mākslīgā intelekta čatbota integrācijas uzdevumam.

## Projekta uzstādīšana

### Priekšnosacījumi
- Python

### Instrukcijas

1.  **Klonējiet repozitoriju:**
    ```bash
    git clone <jūsu_repozitorija_saite_šeit>
    cd <projekta_mape>
    ```

2.  **Izveidojiet un aktivizējiet virtuālo vidi:**
    ```bash
    # Izveido virtuālo vidi
    python -m venv venv

    # Aktivizē vidi (Windows)
    .\venv\Scripts\activate

    # Aktivizē vidi (macOS/Linux)
    source venv/bin/activate
    ```

3.  **Instalējiet nepieciešamās bibliotēkas:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Izveidojiet vides mainīgo (`.env`) failu:**
    Nokopējiet `.env.example` failu uz jaunu failu ar nosaukumu `.env`. Atveriet `.env` failu un ievadiet savu `HUGGINGFACE_API_KEY`.

5.  **Inicializējiet un aizpildiet datubāzi:**
    Palaidiet `seeder.py` skriptu. Tas izveidos `eshop.db` datubāzes failu, nepieciešamās tabulas un pievienos sākuma datus (produktus un lietotājus).
    ```bash
    python seeder.py
    ```

6.  **Palaidiet aplikāciju:**
    ```bash
    python app.py
    ```
    Pēc noklusējuma vietne ir pieejama adresē `http://127.0.0.1:5000`.

---

## Izveidotie lietotāju konti

Pēc datubāzes inicializēšanas ar `seeder.py` ir pieejami divi lietotāju konti testēšanai.

### Administratora konts
-   **Lietotājvārds:** `admin`
-   **Parole:** `adminpass`

### Parasts lietotāja konts
-   **Lietotājvārds:** `testuser`
-   **Parole:** `testpass`

---

### Problēmu risināšana

#### Kļūda, aktivizējot virtuālo vidi PowerShell (Windows)

Ja, mēģinot aktivizēt virtuālo vidi ar komandu `.\venv\Scripts\activate`, jūs saņemat kļūdu `... activate.ps1 cannot be loaded because running scripts is disabled on this system`, tas nozīmē, ka jūsu PowerShell drošības politika bloķē skriptu izpildi.

**Ātrs risinājums:**
Atveriet termināli kā **administrators** un izpildiet šo komandu, lai atļautu skriptu izpildi tikai pašreizējā sesijā:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

# AI testēšana
## Iegūt informāciju par produktu
Čatbots cenšās uzturēt kontaktu ar lietotāju un palīdz izvēlēties kādu no mājaslapā piejamajiem produktiem.

## AI atbild tikai par produktiem
Ja lietotājs ieraksta kaut ko bīstamu, vai kaut ko kas nav saistīts ar produkta iegādi AI atbildēs ar frāzi "I cannot help with that."

## Screenshot ar AI testiem
![alt text](image.png)
![alt text](image-1.png)
