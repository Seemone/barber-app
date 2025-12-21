# BarberApp API Documentation

## Overview

- **Base URL**: `https://aws.bookappbusiness.com:2807`
- **Endpoint**: `POST /$1/0`
- **Encoding**: All payloads are Base64 encoded
- **Content-Type**: `text/plain; charset=utf-8`

## Authentication

All requests use path-based authentication:
```
{BarberID}/{Username}/{Password}/{Action}/{Parameters...}
```

Example credentials (from captured traffic):
- Barber ID: `BARBER_ID`
- Username: `USER_NAME`
- Password: `USER_PASSWORD`

---

## Endpoints

### 1. InitGet - App Initialization

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/InitGet/403/0/A/
```

**Response (decoded):**
```
OK;0922962916;{
  "Titolo": "Vicariparrucchieri",
  "Messaggio": "Orario di lavoro:\n  Mattina.  Pomeriggio \nMartedi. 8:30/13:00. 15:00/20:00\nMercoledì. 8:30/13:00. 15:00/20:00\nGiovedì. 8:30/13:00. 15:00/20:00\nVenerdì. 8:30/13:00. 15:00/20:00\nSabato. 8:30/18:00",
  "Gallery": [
    "https://bookappweb.it/vicariparrucchieri/wp-content/uploads/sites/73/2020/11/5fa0328e9cbce.jpg",
    ...
  ],
  "NomeLogo": "https://www.bookappbusiness.com/public_html/img/loghi/_107/240923223257.png"
};304;0;0;1;_107;;;;;;;;0;0;0;0;0;0;0;;;0;0;;0;0;;;{
  "Personalizzata": false,
  "FidelityPuntiBase": 93,
  "FidelityPuntiFuturi": 0,
  "FidelityPuntiGlobal": 93,
  "Attivata": true,
  "Abilitata": true,
  "FidelitySogliaBase": 850,
  "FidelitySogliaGlobal": 5000,
  "FidelityScontoBase": 10,
  "FidelityScontoExtra": 1
  ...
};;1;0;0;1;;https://www.bookappbusiness.com/public_html/img/;;199827;Vicariparrucchieri;0;1;0;0;0;1;
```

---

### 2. ParrucchieriGetMobile - Get Barbers List

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/ParrucchieriGetMobile//
```

**Response (decoded JSON):**
```json
[
  {
    "Id": 7,
    "Nome": "Giovanni",
    "MinutiTaglio": 45,
    "Servizi": "1111111111111111111111111111100000000000000000000",
    "MinutiTaglioArr": [45,45,15,15,30,45,15,20,60,45,45,45,30,45,20,30,45,30,30,30,45,45,45,45,45,30,30,45,30,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
    "FotoCount": 2,
    "Colore": 1856652,
    "Posizione": 0,
    "Nascosto": false
  },
  {
    "Id": 12,
    "Nome": "rosario",
    "MinutiTaglio": 60,
    ...
  },
  {
    "Id": 14,
    "Nome": "michele",
    "MinutiTaglio": 60,
    ...
  }
]
```

---

### 3. ServiziAppFlutter - Get Services List

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/ServiziAppFlutter//
```

**Response (decoded JSON):**
```json
{
  "Nome": [
    "taglio normal: laterale macchinetta e sopra forbice  + shampoo",
    "",
    "sopracciglia",
    "barba corta a macchinetta o rasoio",
    "trattamento acumen(complete)",
    "Taglio capelli pettine e forbice medio-corto",
    "shampoo",
    "colore",
    "stiratura arginina",
    "Taglio capelli + hair tattoo",
    "taglio capelli (medio corto) e barba (macchinetta o rasoio)",
    ...
  ],
  "Descrizione": [...],
  "Prezzo": [13.0, 13.0, 4.0, 5.0, 15.0, 15.0, 4.0, 0.0, 3.0, 13.0, 18.0, 20.0, 9.0, 16.0, 5.0, 10.0, 15.0, 8.0, 8.0, 10.0, ...],
  "Pos": [1,2,3,4,5,6,7,8,9,10,...],
  "ID": [0,1,2,3,4,5,6,7,8,9,...],
  "Preferiti": "00000000000000000000000000000000000000000000000000",
  "ServiziPrezzoEsposto": "10111110101111111111111111110000000000000000000000",
  "ServiziUsoInterno": "00000001010000000000000000000000000000000000000000",
  "NotificheCount": 43
}
```

---

### 4. LastUpdateGet - Check for Updates

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/LastUpdateGet//
```

**Response (decoded):**
```
211225122758
```
Format: `DDMMYYHHMMSS` → 21/12/25 12:27:58

---

### 5. PrenotazioniSospeseMobileGet - Get Pending Reservations

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotazioniSospeseMobileGet/USER_NAME/////////
```

**Response (decoded JSON):**
```json
[
  {
    "Or": "221225",        // Date: 22/12/25
    "Pe": 1,               // Period/Service ID?
    "No": "USER_NAME",  // Username
    "Ti": 0,               // Type?
    "Pa": "Giovanni",      // Barber name
    "Nm": "3929795647",    // Phone number
    "Nf": null
  }
]
```

---

### 6. PrenotazioniMobileGet - Get Confirmed Reservations

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotazioniMobileGet/USER_NAME/////////
```

**Response:** Empty (no confirmed reservations)

---

### 7. OrariGet - Get Available Slots

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/OrariGet//
```

**Response (decoded JSON):**
```json
[
  {
    "Gi": "221225",      // Date: 22/12/25 (DDMMYY)
    "Pa": "Giovanni",    // Barber name
    "Fe": false,         // Holiday/closed (true = closed)
    "Pr": [],            // ⚠️ AVAILABLE slots (not bookings!)
    "Su": 0              // Unknown
  },
  {
    "Gi": "241225",
    "Pa": "Giovanni",
    "Fe": false,
    "Pr": [
      {
        "Or": "2412251115",   // DateTime (DDMMYYHHmm) = 24/12/25 11:15
        "No": "",             // Name (empty for available)
        "Ti": 0,              // Service type?
        "Pa": "Giovanni",     // Barber
        "Sl": 15              // ⚠️ Slot duration in MINUTES
      }
    ],
    "Su": 0
  }
]
```

> [!IMPORTANT]
> **Il campo `Pr` contiene gli slot DISPONIBILI, non le prenotazioni esistenti!**
> - Se `Pr` è vuoto → Nessuno slot disponibile (tutto occupato)
> - Se `Pr` ha elementi → Quelli sono gli slot liberi
> - `Sl` indica la durata dello slot in minuti (es. 15, 30, 45, 60)
> - Per prenotare un servizio, lo slot deve avere `Sl >= durata_servizio`

---

### 8. PrenotaSospesoAdd - Join Queue (Waitlist)

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotaSospesoAdd/231225/0/0/Giovanni/
```

**Parameters:**
| Position | Value | Description |
|----------|-------|-------------|
| 1 | `231225` | Date (DDMMYY) |
| 2 | `0` | Service ID (0 = default taglio) |
| 3 | `0` | Unknown (always 0?) |
| 4 | `Giovanni` | Barber name |

**Response (decoded):**
```
OK
```

**After joining queue, PrenotazioniSospeseMobileGet returns:**
```json
[
  {
    "Or": "231225",         // Date
    "Pe": 0,                // Service ID
    "No": "USER_NAME",   // Username
    "Ti": 0,                // Type
    "Pa": "Giovanni",       // Barber
    "Nm": "3929795647",     // Phone
    "Nf": null
  }
]
```

---

### 9. PrenotazioneSospesaDelete - Remove from Queue

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotazioneSospesaDelete/USER_NAME/231225//
```

**Parameters:**
| Position | Value | Description |
|----------|-------|-------------|
| 1 | `USER_NAME` | Username |
| 2 | `231225` | Date (DDMMYY) |

**Response (decoded):**
```
OK
```

**Note:** After removing from queue, `PrenotazioniSospeseMobileGet` returns empty response.

---

### 10. PrenotazioneAdd - Book Appointment ⭐

**This is the main booking endpoint!**

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotazioneAdd/2412251115/2/Giovanni//0/////////2///
```

**Parameters:**
| Position | Value | Description |
|----------|-------|-------------|
| 1 | `2412251115` | DateTime (DDMMYYHHmm) - Dec 24, 2025 at 11:15 |
| 2 | `2` | Service ID (2 = sopracciglia) |
| 3 | `Giovanni` | Barber name |
| 4 | (empty) | |
| 5 | `0` | Unknown |
| 6-13 | (empty) | |
| 14 | `2` | Service ID (repeated) |
| 15-17 | (empty) | |

**Response (decoded):**
```
OK{"Personalizzata":false,"FidelityPuntiBase":93,"FidelityPuntiFuturi":4,...}
```

Returns `OK` followed by updated fidelity card info.

**After booking, PrenotazioniMobileGet returns:**
```json
[
  {
    "Or": "2412251115",    // DateTime
    "Pr": 1,               // Confirmed (1 = yes)
    "No": "USER_NAME",  // Username
    "Ti": 2,               // Service ID
    "Pa": "Giovanni",      // Barber
    "Sl": 0,               // Slot?
    "Pn": 4                // Fidelity points earned
  }
]
```

---

### 11. PrenotazioneDelete - Cancel Appointment

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/PrenotazioneDelete/USER_NAME/2412251115/0/Giovanni//0//0.0/2//
```

**Parameters:**
| Position | Value | Description |
|----------|-------|-------------|
| 1 | `USER_NAME` | Username |
| 2 | `2412251115` | DateTime (DDMMYYHHmm) |
| 3 | `0` | Unknown |
| 4 | `Giovanni` | Barber name |
| 5 | (empty) | |
| 6 | `0` | Unknown |
| 7 | (empty) | |
| 8 | `0.0` | Price? |
| 9 | `2` | Service ID |

**Response (decoded):**
```
OK{"Personalizzata":false,"FidelityPuntiBase":93,"FidelityPuntiFuturi":0,...}
```

Returns `OK` followed by updated fidelity card info (points deducted).

---

## Data Structures

### Date Format
- `DDMMYY` - e.g., `221225` = December 22, 2025

### Time Slot Format
- `DDMMYYHHmm` - e.g., `2412251115` = December 24, 2025 at 11:15

### Barber IDs
| ID | Name |
|----|------|
| 7 | Giovanni |
| 12 | rosario |
| 14 | michele |

### Service IDs (partial list)
| ID | Service | Price (€) | Duration (min) |
|----|---------|-----------|----------------|
| 0 | Taglio normale + shampoo | 13 | 45 |
| 2 | Sopracciglia | 4 | 15 |
| 3 | Barba corta | 5 | 15 |
| 5 | Taglio pettine e forbice | 15 | 45 |
| 10 | Taglio + barba | 18 | 45 |

---

## Endpoints Summary ✅

All **11 endpoints** documented:

| # | Endpoint | Action |
|---|----------|--------|
| 1 | InitGet | App initialization |
| 2 | ParrucchieriGetMobile | Get barbers list |
| 3 | ServiziAppFlutter | Get services list |
| 4 | LastUpdateGet | Check for updates |
| 5 | PrenotazioniSospeseMobileGet | Get pending reservations |
| 6 | PrenotazioniMobileGet | Get confirmed reservations |
| 7 | OrariGet | Get available slots |
| 8 | PrenotaSospesoAdd | Join queue/waitlist |
| 9 | PrenotazioneSospesaDelete | Leave queue |
| 10 | **PrenotazioneAdd** | **Book appointment** ⭐ |
| 11 | **PrenotazioneDelete** | **Cancel appointment** |
| 12 | ClienteGet | Get client profile data |

---

### 12. ClienteGet - Get Client Profile

**Request:**
```
BARBER_ID/USER_NAME/USER_PASSWORD/ClienteGet/USER_NAME/USER_PASSWORD//
```

**Parameters:**
- `{action}`: `ClienteGet`
- `{param1}`: Username
- `{param2}`: Password

**Response (decoded JSON):**
```json
{
  "Nome": "Nome",
  "Cognome": "Cognome",
  "Cellulare": "3331234567",
  "Mail": "nome.cognome@gmail.com",
  "Username": "USER_NAME",
  "Password": "USER_PASSWORD",
  "Attivato": 1,
  "UltimaPrenotazione": "2025-12-24T11:15:00",
  "Note": null,
  "DataNascita": "1980-01-01T00:00:00",
  "TotalePrenotazioni": 0,
  "Versione": 403,
  "RecensioneStellina": 0,
  "Recensione": "",
  "Sconto": "",
  "Sospeso": false,
  "Fidelity": null,
  "ComunicazioniMarketing": false
}
```

> [!NOTE]
> Questo endpoint restituisce i dati del profilo utente, inclusa l'ultima prenotazione effettuata.

---

### 13. CercaAttivitaVicinaGet - Search Nearby Businesses (PUBLIC)

> [!IMPORTANT]
> Questo è un endpoint **pubblico** che non richiede autenticazione!
> Restituisce il campo `Key` che è l'ID utente da usare nelle altre richieste.

**Request:**
```
///CercaAttivitaVicinaGet/1/37.1905136/13.7697186/10000//
```

**Parameters:**
- `{tipo}`: Tipo attività (`1` = barbiere/parrucchiere)
- `{lat}`: Latitudine GPS
- `{lon}`: Longitudine GPS
- `{raggio}`: Raggio di ricerca in metri

**Response (decoded JSON):**
```json
[{
  "Prefisso": "_107",
  "Nome": "Vicariparrucchieri",
  "Key": "BARBER_ID",              // <-- ID da usare come UserID!
  "Telefono": "0922962916",
  "Indirizzo": "Palma di Montechiaro Agrigento (Km 0)",
  "Distanza": 483,
  "Lat": 37.192638,
  "Lon": 13.764964,
  "CodiceAttivita": 199827
}]
```

---

## Python Client Usage

```python
from barberapp_client import BarberAppClient

client = BarberAppClient(
    user_id="BARBER_ID",
    username="USER_NAME",
    password="USER_PASSWORD"
)

# Get barbers
barbers = client.get_barbers()

# Get services
services = client.get_services()

# Get available slots
slots = client.get_available_slots()

# Book appointment (once we discover the endpoint)
# client.book(date="231225", time="1000", barber_id=7, service_id=0)
```
