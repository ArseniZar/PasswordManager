

# 🔐 Menedżer Haseł

Prosty i bezpieczny menedżer haseł napisany w Pythonie z przyjaznym dla użytkownika interfejsem graficznym (GUI).

## 🌟 Główne Funkcjonalności

Aplikacja została zaprojektowana z myślą o maksymalnym bezpieczeństwie i wygodzie użytkowania. Oto, co oferuje:

### 🛡️ Bezkompromisowe Bezpieczeństwo (Zero-Knowledge)

Twoja prywatność jest naszym priorytetem. Działamy w modelu "zero-knowledge", co oznacza, że tylko Ty masz dostęp do swoich danych.

-   **Szyfrowanie po Stronie Klienta:** Twoje hasła są szyfrowane i deszyfrowane lokalnie na Twoim urządzeniu przy użyciu silnego algorytmu pochodzącego od Twojego hasła głównego.
-   **Nikt Inny Nie Ma Dostępu:** Hasła przechowywane w bazie danych są w formie zaszyfrowanej. Bez Twojego hasła głównego są one bezużytecznym zbiorem znaków. Nawet my, twórcy aplikacji, nie możemy ich odczytać.

> ⚠️ **Niezwykle Ważne!**
> Taki poziom bezpieczeństwa oznacza, że w przypadku utraty hasła głównego do konta, **Twoje zapisane hasła NIE MOGĄ zostać odzyskane**. Są utracone na zawsze. Zastanów się nad bezpiecznym przechowywaniem swojego hasła głównego.

### ⚙️ Intuicyjne Zarządzanie Hasłami

Zarządzaj swoimi danymi uwierzytelniającymi w prosty i efektywny sposób.

-   🔑 **Tworzenie i Edycja:** Z łatwością dodawaj nowe wpisy dla stron internetowych, aplikacji i usług, a także aktualizuj istniejące.
-   🔍 **Błyskawiczne Wyszukiwanie:** Potężna funkcja wyszukiwania pozwala znaleźć potrzebne dane w ciągu kilku sekund.
-   🗑️ **Bezpieczne Usuwanie:** Bezpowrotnie usuwaj wpisy, których już nie potrzebujesz.

### 🔄 Pełna Kontrola nad Danymi (Import i Eksport)

Twoje dane należą do Ciebie. Masz pełną swobodę w zarządzaniu nimi.

-   📤 **Eksport Danych:** Wyeksportuj całą swoją bazę haseł do zaszyfrowanego pliku. Jest to idealne rozwiązanie do tworzenia kopii zapasowych lub przenoszenia danych.
-   📥 **Import Danych:** Z łatwością zaimportuj hasła z wcześniej wyeksportowanego pliku, co sprawia, że konfiguracja na nowym urządzeniu lub odtwarzanie kopii zapasowej jest dziecinnie proste.

---

## 🚀 Pierwsze Kroki

Poniższe instrukcje pomogą Ci uruchomić kopię projektu na Twojej lokalnej maszynie w celach deweloperskich i testowych.

### ✅ Wymagania wstępne

-   Python 3.8 lub nowszy
-   `git` (do sklonowania repozytorium)

### 🧪 Instalacja i Konfiguracja

1.  **Sklonuj repozytorium**
    ```bash
    git clone https://github.com/your-username/password-manager.git
    cd password-manager
    ```

2.  **Stwórz wirtualne środowisko**
    ```bash
    python3 -m venv venv
    ```

3.  **Aktywuj wirtualne środowisko**

    *Na macOS/Linux:*
    ```bash
    source venv/bin/activate
    ```
    *Na Windows:*
    ```bash
    venv\Scripts\activate
    ```

4.  **Zainstaluj wymagane biblioteki Python**
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Instrukcje Konfiguracji Pliku

Ten projekt używa klasy `Config` w pliku `config.py` do zarządzania wszystkimi ustawieniami aplikacji. Ten przewodnik wyjaśnia, jak poprawnie go skonfigurować.

### 1. Czym jest plik konfiguracyjny?

> Plik konfiguracyjny to miejsce, z którego aplikacja odczytuje ważne parametry do poprawnego działania: lokalizację bazy danych, klucze bezpieczeństwa, dane logowania do poczty e-mail itp. Takie podejście pozwala na zmianę ustawień bez modyfikowania głównego kodu aplikacji.

### 2. Przykładowy plik `config.py`

Stwórz plik o nazwie `config.py` i dodaj poniższą zawartość. Pamiętaj, aby zastąpić wartości zastępcze.

```python
class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///passwordmanager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'twój-sekretny-klucz-tutaj'
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "twój-email@gmail.com"
    MAIL_PASSWORD = "twoje-haslo-aplikacji-gmail"
    MAIL_DEFAULT_SENDER = ("Menedżer Haseł", "twój-email@gmail.com")
    LOGIN_VIEW = "auth.login"
    LOGIN_MESSAGE = "Musisz być zalogowany, aby uzyskać dostęp do tej strony."
```

### 3. Objaśnienie parametrów

#### **Baza Danych**

-   `SQLALCHEMY_DATABASE_URI`
    Określa lokalizację bazy danych.
    Przykłady:
    -   `"sqlite:///passwordmanager.db"` — lokalny plik SQLite.
    -   `"postgresql://uzytkownik:haslo@localhost/nazwabazy"` — przykład dla PostgreSQL.

-   `SQLALCHEMY_TRACK_MODIFICATIONS`
    Śledzi zmiany w bazie danych. Dla lepszej wydajności ustaw na `False` w środowisku produkcyjnym, ale możesz zostawić `True` do debugowania.

#### **Bezpieczeństwo**

-   `SECRET_KEY`
    Bardzo ważny parametr — tajny klucz do zabezpieczania sesji i formularzy przed atakami.
    **MUSISZ** zastąpić go własnym, długim, losowym tajnym kluczem!
    Nigdy nie publikuj tego klucza publicznie.

#### **Jak wygenerować tajny klucz (SECRET_KEY)**

1.  Stwórz skrypt, np. `generate_key.py`:
    ```python
    import secrets

    def generate_flask_secret_key(length=32):
        """Generuje bezpieczny, losowy tajny klucz dla aplikacji Flask."""
        return secrets.token_urlsafe(length)

    # Wygeneruj i wydrukuj tajny klucz
    if __name__ == "__main__":
        key = generate_flask_secret_key()
        print("Twój nowy tajny klucz to:", key)
    ```

2.  Uruchom skrypt:
    ```bash
    python generate_key.py
    ```

3.  Spowoduje to wydrukowanie nowego, losowego tajnego klucza, na przykład:
    `Twój nowy tajny klucz to: Rkq9s1V0rM3a7fZpLqE8dWzXtN4uH2YbQ_jOVx-PQaE`

4.  Skopiuj wygenerowany ciąg znaków i użyj go do zastąpienia wartości `SECRET_KEY` w swojej konfiguracji:
    `SECRET_KEY = "Rkq9s1V0rM3a7fZpLqE8dWzXtN4uH2YbQ_jOVx-PQaE"`

#### **Pamięć Podręczna (Caching)**

-   `CACHE_TYPE` — typ pamięci podręcznej. `SimpleCache` to prosta wbudowana pamięć podręczna, dobra na etapie deweloperskim.
-   `CACHE_DEFAULT_TIMEOUT` — czas wygaśnięcia pamięci podręcznej w sekundach (np. 300 sekund = 5 minut).

#### **Ustawienia E-mail**

Używane do wysyłania e-maili (np. reset hasła).

-   `MAIL_SERVER` — adres serwera SMTP. Dla Gmaila użyj "smtp.gmail.com".
-   `MAIL_PORT` — port serwera (587 dla TLS).
-   `MAIL_USE_TLS` — czy używać TLS (zalecane `True`).
-   `MAIL_USE_SSL` — czy używać SSL (zazwyczaj `False`, jeśli TLS jest włączone).
-   `MAIL_USERNAME` — twój adres e-mail do wysyłania wiadomości.
-   `MAIL_PASSWORD` — twoje hasło do poczty e-mail lub token aplikacji (patrz niżej).
-   `MAIL_DEFAULT_SENDER` — krotka (nazwa, e-mail) wyświetlana jako nadawca.

#### **Ustawienia Logowania**

-   `LOGIN_VIEW` — nazwa ścieżki (route) dla strony logowania (np. "auth.login").
-   `LOGIN_MESSAGE` — wiadomość wyświetlana, gdy użytkownik nie ma uprawnień.

### 4. Jak uzyskać Hasło Aplikacji dla Gmaila

> **Dlaczego tego potrzebuję?** Jeśli masz włączoną Weryfikację dwuetapową na swoim Koncie Google (a powinieneś!), Google blokuje próby logowania z mniej bezpiecznych aplikacji. Hasło Aplikacji to 16-cyfrowy kod dostępu, który daje aplikacji pozwolenie na dostęp do Twojego Konta Google.

Postępuj zgodnie z tymi krokami, aby je wygenerować:

1.  **Włącz Weryfikację dwuetapową:**
    -   Przejdź na stronę bezpieczeństwa swojego Konta Google: [myaccount.google.com/security](https://myaccount.google.com/security)
    -   W sekcji "Logowanie się w Google" wybierz **Weryfikacja dwuetapowa** i włącz ją, jeśli jeszcze tego nie zrobiłeś.

2.  **Utwórz Hasło Aplikacji:**
    -   Wróć na stronę [Bezpieczeństwo](https://myaccount.google.com/security).
    -   W sekcji "Logowanie się w Google" wybierz **Hasła do aplikacji**. Może być konieczne ponowne zalogowanie się.
    -   W menu rozwijanym *Wybierz aplikację* wybierz **Inna (nazwa własna)**.
    -   Wpisz opisową nazwę, np. `Aplikacja Menedżer Haseł`, i kliknij **Generuj**.

3.  **Użyj wygenerowanego hasła:**
    -   Google wyświetli 16-znakowe hasło w żółtym polu.
    -   **Skopiuj to hasło.** To właśnie jego użyjesz jako wartości zmiennej `MAIL_PASSWORD` w pliku `config.py`.

---

## 🏃‍♀️ Jak Uruchomić Aplikację

### 1. Tryb deweloperski (zalecany do testowania)

Uruchom aplikację z włączonym trybem debugowania. Zapewnia to szczegółowe komunikaty o błędach i automatycznie przeładowuje serwer po wprowadzeniu zmian w kodzie.

```bash
python run.py
```
> **Ostrzeżenie:** Ten tryb jest przydatny podczas developmentu, ale **NIGDY** nie powinien być używany w środowisku produkcyjnym na żywo.

### 2. Tryb produkcyjny

Aby uruchomić aplikację do faktycznego użytku, należy wyłączyć tryb debugowania dla lepszej wydajności i bezpieczeństwa.

1.  Otwórz plik `run.py` i zmień flagę `debug` na `False`:
    ```python
    if __name__ == '__main__':
        app.run(debug=False)
    ```
2.  Następnie uruchom aplikację z terminala:
    ```bash
    python run.py
    ```