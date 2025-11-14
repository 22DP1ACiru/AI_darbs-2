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

7. **SVARĪGI! Kļūda ar pēdējo OpenAI bibliotēkas versiju:**
    Startējot aplikāciju var rasties kļūda ar tekstu:
    ```
    TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
    ```
    Tā ir problēma ar jaunāko OpenAI bibliotēkas versiju, kurā ir mainījušies parametri. Lai to atrisinātu, vieglākais veids ir palaist šo komandu:
    ```
    !pip install openai==1.55.3 httpx==0.27.2 --force-reinstall
    ```
    Tā instalē stabīlu bibliotēkas versiju un instalē saderīgu httpx versiju.
    Source: [Raised GitHub issue](https://github.com/vanna-ai/vanna/issues/730).
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