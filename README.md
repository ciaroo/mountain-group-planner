# Vermiglio26

**Studente:** Francesco Ciarini  

**Tipo di progetto scelto:** Full-Stack Web Application  

**Framework utilizzato:** Django

Vermiglio26 è una web application sviluppata con Django per organizzare una vacanza di gruppo.

L'idea del progetto è adattare un sistema di gestione eventi a un caso concreto.  
Gli organizzatori possono creare e gestire attività, eventi e avvisi oltre che visualizzare dati dei profili degli utenti registrati, utili per la gestione organizzativa della vacanza.  
I partecipanti possono registrarsi, consultare il programma della settimana e prenotarsi alle attività disponibili.

## Funzionalità principali

L'applicazione permette di:

- registrare nuovi utenti;
- gestire login e logout;
- compilare un profilo personale;
- consultare un calendario delle attività;
- visualizzare il dettaglio di ogni attività;
- prenotarsi alle attività che richiedono iscrizione;
- annullare una prenotazione;
- controllare i posti disponibili;
- distinguere utenti partecipanti e organizzatori;
- creare, modificare ed eliminare attività;
- pubblicare avvisi;
- consultare riepiloghi utili per l'organizzazione;
- esportare tabelle di dati degli utenti registrati in formato CSV.

Sono presenti anche alcune funzioni pensate per il contesto della vacanza, come la raccolta di allergie, preferenze alimentari, disponibilità auto e richiesta biancheria.

## Ruoli

L'applicazione prevede due ruoli principali.

### Partecipante

- registrarsi al sito;
- accedere con il proprio account;
- compilare e modificare il proprio profilo;
- consultare il calendario delle attività;
- aprire il dettaglio di ogni attività;
- prenotarsi alle attività disponibili;
- annullare una prenotazione;
- consultare le proprie prenotazioni.

### Organizzatore

- accedere all'area organizzatore;
- creare nuove attività;
- modificare attività esistenti;
- eliminare attività;
- duplicare attività su più date;
- pubblicare e gestire avvisi;
- vedere la lista dei partecipanti;
- consultare riepiloghi organizzativi;
- visualizzare allergie e preferenze alimentari;
- visualizzare la disponibilità delle auto;
- esportare dati in formato CSV.

## Tecnologie usate

Il progetto è stato realizzato con:

- Python
- Django
- HTML
- CSS
- Bootstrap
- SQLite per l'esecuzione locale
- PostgreSQL Neon per il database online
- Render per il deploy
- GitHub per il versionamento


## Esecuzione locale

Per eseguire il progetto in locale:

```bash
git clone https://github.com/ciaroo/mountain-group-planner.git
cd mountain-group-planner
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Il sito sarà disponibile all'indirizzo:

```text
http://127.0.0.1:8000/
```
## Database demo locale

Nel repository è presente un database SQLite demo già popolato:
```text
db.sqlite3
```

Il database contiene dati fittizi pensati per provare il progetto.
Non contiene dati reali dei partecipanti alla vacanza.

Sono presenti:

- utenti demo;
- profili demo;
- attività demo;
- prenotazioni demo;
- avvisi demo.

## Account demo

È possibile provare il progetto con questi account.

| Username | Password | Ruolo |

|---|---|---|

| `mario_demo` | `demo12345` | Partecipante |

| `admin_demo` | `demo12345` | Organizzatore / amministratore |

| `organizzatore_demo` | `demo12345` | Staff organizzatore |

## Versione online demo

Il sito è disponibile a questo indirizzo:
```text
https://mountain-group-planner-demo-esame.onrender.com
```

Questa versione usa un database demo separato.
Anche online sono presenti solo dati fittizi.

Il deploy online è stato realizzato con Render, mentre per il database online demo è stato usato Neon PostgreSQL.

